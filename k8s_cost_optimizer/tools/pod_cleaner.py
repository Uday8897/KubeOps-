from typing import List
from datetime import datetime, timedelta, timezone
from k8s_cost_optimizer.models.schemas import OptimizationAction, OptimizationType
from k8s_cost_optimizer.utils.logger import logger
from .base_tool import BaseOptimizationTool

class PodCleanupTool(BaseOptimizationTool):
    def analyze(self) -> List[OptimizationAction]:
        actions = []
        pods = self.k8s_client.get_all_pods()
        
        for pod in pods:
            if pod.status.phase in ["Succeeded", "Failed"]:
                try:
                    end_time_str = pod.status.container_statuses[0].state.terminated.finished_at
                    end_time = end_time_str.replace(tzinfo=timezone.utc)
                    if datetime.now(timezone.utc) - end_time > timedelta(hours=24):
                        actions.append(OptimizationAction(
                            type=OptimizationType.POD_CLEANUP,
                            target=pod.metadata.name,
                            namespace=pod.metadata.namespace,
                            action_details={"operation": "delete_pod", "phase": pod.status.phase},
                            confidence=0.99,
                            estimated_savings=0.1
                        ))
                except (AttributeError, IndexError):
                    continue

        logger.info(f"Generated {len(actions)} pod cleanup actions.")
        return actions