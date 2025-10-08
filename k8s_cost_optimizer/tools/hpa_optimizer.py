from typing import List
from k8s_cost_optimizer.models.schemas import OptimizationAction, OptimizationType
from k8s_cost_optimizer.utils.logger import logger
from .base_tool import BaseOptimizationTool

class HPAOptimizerTool(BaseOptimizationTool):
    def analyze(self) -> List[OptimizationAction]:
        actions = []
        hpas = self.k8s_client.list_hpas()
        
        for hpa in hpas:
            current_min = hpa.spec.min_replicas
            current_max = hpa.spec.max_replicas
            current_replicas = hpa.status.current_replicas

            if current_replicas == current_min and current_min > 1:
                actions.append(OptimizationAction(
                    type=OptimizationType.HPA_OPTIMIZATION,
                    target=hpa.metadata.name,
                    namespace=hpa.metadata.namespace,
                    action_details={
                        "operation": "patch_hpa",
                        "recommendation": f"Consider lowering minReplicas from {current_min}",
                        "current_min": current_min,
                        "current_max": current_max
                    },
                    confidence=0.75,
                    estimated_savings=2.5 * (current_min - 1)
                ))
        
        logger.info(f"Generated {len(actions)} HPA optimization actions.")
        return actions