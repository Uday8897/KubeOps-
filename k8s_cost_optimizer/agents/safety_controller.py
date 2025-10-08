from typing import List
from k8s_cost_optimizer.models.schemas import OptimizationAction, ActionStatus, OptimizationType
from k8s_cost_optimizer.utils.k8s_client import KubernetesClient
from k8s_cost_optimizer.utils.logger import logger

class SafetyController:
    def __init__(self, k8s_client: KubernetesClient):
        self.k8s_client = k8s_client
        self.critical_namespaces = ['kube-system', 'kube-public', 'opencost']
    
    def validate_actions(self, actions: List[OptimizationAction], run_id: str) -> List[OptimizationAction]:
        log = logger.bind(run_id=run_id)
        log.info(f"Validating {len(actions)} actions for safety.")
        
        for action in actions:
            if self._is_action_safe(action):
                action.status = ActionStatus.APPROVED
                log.info("Action approved", action_id=action.id, type=action.type.value)
            else:
                action.status = ActionStatus.REJECTED
                log.warning("Action rejected", action_id=action.id, reason=action.error)
        
        return actions

    def _is_action_safe(self, action: OptimizationAction) -> bool:
        if action.namespace in self.critical_namespaces:
            action.error = f"Action targets a critical namespace: {action.namespace}"
            return False
        
        if action.confidence < 0.7:
             action.error = f"Confidence ({action.confidence}) is below threshold (0.7)"
             return False

        if action.type == OptimizationType.NODE_OPTIMIZATION:
            nodes = self.k8s_client.get_nodes()
            ready_nodes = [
                n for n in nodes if n.status and any(c.type == "Ready" and c.status == "True" for c in n.status.conditions)
            ]
            if len(ready_nodes) <= 2:
                action.error = "Cannot drain node from a cluster with <= 2 ready nodes."
                return False
            return True

        return True