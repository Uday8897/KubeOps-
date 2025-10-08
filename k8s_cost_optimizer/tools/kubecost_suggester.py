from typing import List, Optional
from k8s_cost_optimizer.models.schemas import OptimizationAction, OptimizationType
from k8s_cost_optimizer.utils.logger import logger
from k8s_cost_optimizer.utils.kubecost_client import KubecostClient
from k8s_cost_optimizer.tools.base_tool import BaseOptimizationTool

class KubecostSuggesterTool(BaseOptimizationTool):
    def __init__(self, kubecost_client: KubecostClient, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kubecost_client = kubecost_client

    def analyze(self) -> List[OptimizationAction]:
        actions = []
        log = logger.bind(tool="KubecostSuggesterTool")
        log.info("Querying Kubecost for savings recommendations.")
        
        recommendations = self.kubecost_client.get_savings_recommendations()

        for rec in recommendations:
            if rec.get('type') == 'Request Sizing':
                action = self._create_rightsizing_action(rec)
                if action:
                    actions.append(action)
        
        log.info(f"Generated {len(actions)} actions from Kubecost recommendations.")
        return actions

    def _create_rightsizing_action(self, rec: dict) -> Optional[OptimizationAction]:
        try:
            return OptimizationAction(
                type=OptimizationType.RIGHTSIZING,
                target=rec['name'],
                namespace=rec['namespace'],
                action_details={
                    "operation": "patch_workload_resources",
                    "container": rec['container'],
                    "current_requests": rec['requestCurrent'],
                    "recommended_requests": rec['requestRec']
                },
                confidence=0.95,
                estimated_savings=rec.get('monthlySavings', 20.0)
            )
        except KeyError as e:
            logger.warning("Could not parse Kubecost rightsizing recommendation due to missing key", key=str(e), recommendation=rec)
            return None
