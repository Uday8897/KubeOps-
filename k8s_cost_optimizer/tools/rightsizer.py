from typing import List, Dict, Any
from k8s_cost_optimizer.models.schemas import OptimizationAction, OptimizationType
from k8s_cost_optimizer.utils.logger import logger
from .base_tool import BaseOptimizationTool
from kubernetes.utils import parse_quantity

class RightsizingTool(BaseOptimizationTool):
    def analyze(self) -> List[OptimizationAction]:
        actions = []
        log = logger.bind(tool="RightsizingTool")
        log.info("Starting workload rightsizing analysis.")

        cpu_query = 'quantile_over_time(0.95, rate(container_cpu_usage_seconds_total{container!="", pod!=""}[5m])[7d:5m])'
        mem_query = 'quantile_over_time(0.95, container_memory_working_set_bytes{container!="", pod!=""}[7d:5m])'

        cpu_results = self.prometheus_client.query(cpu_query)
        mem_results = self.prometheus_client.query(mem_query)

        if not cpu_results and not mem_results:
            log.warning("Could not retrieve metrics from Prometheus for rightsizing.")
            return []

        recommendations = self._process_metrics(cpu_results or [], mem_results or [])
        pods = self.k8s_client.get_all_pods()

        for pod in pods:
            if not pod.metadata.owner_references:
                continue

            for container in pod.spec.containers:
                key = f"{pod.metadata.namespace}/{pod.metadata.name}/{container.name}"
                if key not in recommendations:
                    continue

                rec = recommendations[key]
                current_requests = container.resources.requests or {}
                
                if self._is_recommendation_significant(rec, current_requests):
                    actions.append(OptimizationAction(
                        type=OptimizationType.RIGHTSIZING,
                        target=self._get_owner_workload(pod),
                        namespace=pod.metadata.namespace,
                        action_details={
                            "operation": "patch_workload_resources",
                            "container": container.name,
                            "current_requests": current_requests,
                            "recommended_requests": rec
                        },
                        confidence=0.85,
                        estimated_savings=15.0
                    ))

        log.info(f"Generated {len(actions)} rightsizing actions.")
        return actions

    def _process_metrics(self, cpu_results: List, mem_results: List) -> Dict[str, Dict[str, str]]:
        recs: Dict[str, Dict[str, str]] = {}
        for result in cpu_results:
            metric = result.get('metric', {})
            key = f"{metric.get('namespace')}/{metric.get('pod')}/{metric.get('container')}"
            value_cores = float(result.get('value', [0, '0'])[1])
            recs.setdefault(key, {})['cpu'] = f"{max(25, int(value_cores * 1000))}m"

        for result in mem_results:
            metric = result.get('metric', {})
            key = f"{metric.get('namespace')}/{metric.get('pod')}/{metric.get('container')}"
            value_bytes = int(result.get('value', [0, '0'])[1])
            recs.setdefault(key, {})['memory'] = f"{max(50, int(value_bytes / 1024 / 1024))}Mi"
        return recs

    def _get_owner_workload(self, pod: Any) -> str:
        owner = pod.metadata.owner_references[0]
        if owner.kind == "ReplicaSet":
            return owner.name.rsplit('-', 1)[0]
        return owner.name

    def _is_recommendation_significant(self, rec: Dict, current: Dict) -> bool:
        try:
            current_cpu_m = parse_quantity(current.get('cpu', '0m')) * 1000
            rec_cpu_m = parse_quantity(rec.get('cpu', '0m')) * 1000
            if rec_cpu_m > 0 and current_cpu_m > 0 and rec_cpu_m < (current_cpu_m * 0.7):
                return True
        except (ValueError, TypeError):
            pass
        return False