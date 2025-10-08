from typing import List
from k8s_cost_optimizer.models.schemas import OptimizationAction, OptimizationType
from k8s_cost_optimizer.utils.logger import logger
from .base_tool import BaseOptimizationTool

class NodeOptimizerTool(BaseOptimizationTool):
    def analyze(self) -> List[OptimizationAction]:
        actions = []
        log = logger.bind(tool="NodeOptimizerTool")
        log.info("Starting node optimization analysis.")

        query = '(sum(kube_pod_container_resource_requests{resource="cpu", unit="core"}) by (node)) / (sum(kube_node_status_capacity{resource="cpu", unit="core"}) by (node)) < 0.3'
        
        results = self.prometheus_client.query(query)
        if not results:
            log.warning("Could not retrieve node utilization metrics from Prometheus.")
            return []

        underutilized_nodes = [res['metric']['node'] for res in results]

        for node_name in underutilized_nodes:
            actions.append(OptimizationAction(
                type=OptimizationType.NODE_OPTIMIZATION,
                target=node_name,
                namespace="",
                action_details={
                    "operation": "cordon_and_drain",
                    "reason": "Node is underutilized, consolidating workloads to save costs."
                },
                confidence=0.9,
                estimated_savings=100.0
            ))

        log.info(f"Generated {len(actions)} node optimization actions.")
        return actions