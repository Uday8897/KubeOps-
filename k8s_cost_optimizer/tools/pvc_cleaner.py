from typing import List
from k8s_cost_optimizer.models.schemas import OptimizationAction, OptimizationType
from k8s_cost_optimizer.utils.logger import logger
from .base_tool import BaseOptimizationTool

class PVCCleanerTool(BaseOptimizationTool):
    def analyze(self) -> List[OptimizationAction]:
        actions = []
        unbound_pvcs = self.k8s_client.get_unbound_pvcs()

        for pvc in unbound_pvcs:
            actions.append(OptimizationAction(
                type=OptimizationType.PVC_CLEANUP,
                target=pvc.metadata.name,
                namespace=pvc.metadata.namespace,
                action_details={"operation": "delete_pvc", "phase": pvc.status.phase},
                confidence=0.9,
                estimated_savings=5.0
            ))

        logger.info(f"Generated {len(actions)} PVC cleanup actions.")
        return actions