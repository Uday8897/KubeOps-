from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from datetime import datetime
from typing import Dict, Any, List, Tuple

from k8s_cost_optimizer.config import Settings
from k8s_cost_optimizer.models.schemas import ClusterState, ActionStatus, OptimizationType, OptimizationAction
from k8s_cost_optimizer.utils.k8s_client import KubernetesClient
from k8s_cost_optimizer.utils.prometheus import PrometheusClient
from k8s_cost_optimizer.utils.kubecost_client import KubecostClient
from k8s_cost_optimizer.utils.logger import logger
from k8s_cost_optimizer.tools.pod_cleaner import PodCleanupTool
from k8s_cost_optimizer.tools.pvc_cleaner import PVCCleanerTool
from k8s_cost_optimizer.tools.hpa_optimizer import HPAOptimizerTool
from k8s_cost_optimizer.tools.node_optimizer import NodeOptimizerTool
from k8s_cost_optimizer.tools.kubecost_suggester import KubecostSuggesterTool
from k8s_cost_optimizer.agents.safety_controller import SafetyController

class AICostOptimizationOrchestrator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.k8s_client = KubernetesClient()
        self.prometheus_client = PrometheusClient(
            url=self.settings.prometheus.url,
            timeout=self.settings.prometheus.timeout
        )
        self.kubecost_client = KubecostClient(
          base_url=self.settings.kubecost.url
        )
        
        self.tools = [
            KubecostSuggesterTool(
                kubecost_client=self.kubecost_client,
                k8s_client=self.k8s_client,
                prometheus_client=self.prometheus_client
            ),
            PodCleanupTool(self.k8s_client, self.prometheus_client),
            PVCCleanerTool(self.k8s_client, self.prometheus_client),
            HPAOptimizerTool(self.k8s_client, self.prometheus_client),
            NodeOptimizerTool(self.k8s_client, self.prometheus_client),
        ]
        
        self.safety_controller = SafetyController(self.k8s_client)
        self.llm = ChatGroq(model=settings.groq_model_name, groq_api_key=settings.groq_api_key)
        self.agent = self._build_workflow().compile()
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(dict)
        workflow.add_node("collect_metrics", self._collect_metrics_node)
        workflow.add_node("analyze_cluster", self._analyze_cluster_node)
        workflow.add_node("generate_actions", self._generate_actions_node)
        workflow.add_node("validate_safety", self._validate_safety_node)
        workflow.add_node("generate_report", self._generate_report_node)
        
        workflow.add_edge(START, "collect_metrics")
        workflow.add_edge("collect_metrics", "analyze_cluster")
        workflow.add_edge("analyze_cluster", "generate_actions")
        workflow.add_edge("generate_actions", "validate_safety")
        workflow.add_edge("validate_safety", "generate_report")
        workflow.add_edge("generate_report", END)
        
        return workflow

    def _run_analysis_workflow(self, run_id: str, dry_run: bool) -> Dict:
        """Runs the analysis part of the workflow and returns potential actions."""
        log = logger.bind(run_id=run_id)
        log.info("Starting new Kubernetes cost optimization analysis workflow", dry_run=dry_run)
        initial_state = {"run_id": run_id, "dry_run": dry_run, "actions": []}
        final_state = self.agent.invoke(initial_state)

        if final_state.get("error"):
             log.error("Analysis workflow finished with an error.", error=final_state.get("error"))
        else:
             log.info("Analysis workflow completed successfully.", report=final_state.get("report"))
        return final_state

    def run_and_categorize_actions(self, run_id: str, dry_run: bool) -> Dict:
        """
        Runs the full analysis and then categorizes actions for HITL or autonomous execution.
        This is the new main entry point for the backend.
        """
        analysis_result = self._run_analysis_workflow(run_id, dry_run)
        
        if "error" in analysis_result:
            return analysis_result

        all_actions = analysis_result.get('actions', [])
        approved_actions = [a for a in all_actions if a.status == ActionStatus.APPROVED]

        pending_for_approval = []
        auto_execute_actions = []
        
        CONFIDENCE_THRESHOLD = 0.90 
        DESTRUCTIVE_ACTIONS = [
            OptimizationType.POD_CLEANUP, 
            OptimizationType.PVC_CLEANUP, 
            OptimizationType.NODE_OPTIMIZATION
        ]

        logger.info(f"Categorizing {len(approved_actions)} approved actions for run {run_id}.")

        for action in approved_actions:
            is_destructive = action.type in DESTRUCTIVE_ACTIONS
            is_highly_confident = action.confidence > CONFIDENCE_THRESHOLD

            if is_destructive:
                pending_for_approval.append(action)
                logger.info("Action requires HITL (destructive)", action_id=action.id, type=action.type.value)
            elif is_highly_confident and not dry_run:
                auto_execute_actions.append(action)
                logger.info("Action auto-approved for immediate execution", action_id=action.id, type=action.type.value, confidence=action.confidence)
            else:
                pending_for_approval.append(action)
                logger.info("Action requires HITL (low confidence or dry_run)", action_id=action.id, type=action.type.value, confidence=action.confidence)

        return {
            "report": analysis_result.get("report"),
            "pending_actions": pending_for_approval,
            "auto_execute_actions": auto_execute_actions
        }

    async def execute_single_action(self, action: OptimizationAction) -> Tuple[bool, str]:
        """Executes a single, approved action. Called by the API for both auto and manual approval."""
        log = logger.bind(action_id=action.id, type=action.type.value)
        log.info("Executing single action.")
        success = False
        message = ""

        try:
            if action.type == OptimizationType.POD_CLEANUP:
                success = self.k8s_client.delete_pod(name=action.target, namespace=action.namespace)
            elif action.type == OptimizationType.PVC_CLEANUP:
                success = self.k8s_client.delete_pvc(name=action.target, namespace=action.namespace)
            elif action.type == OptimizationType.NODE_OPTIMIZATION:
                if self.k8s_client.cordon_node(node_name=action.target):
                    success = self.k8s_client.drain_node(node_name=action.target)
            else:
                log.warning("Live execution logic for action type not implemented, skipping.")
                success = True
            
            if not success:
                message = f"Execution failed in Kubernetes client for action type {action.type.value}"
                log.error(message)
        except Exception as e:
            success = False
            message = str(e)
            log.error("Exception during action execution", error=message)

        return success, message
    
    def _log_node_entry(self, state: dict, node_name: str) -> any:
        return logger.bind(run_id=state.get('run_id'), node=node_name)

    def _collect_metrics_node(self, state: dict) -> dict:
        log = self._log_node_entry(state, "collect_metrics")
        log.info("Starting metric collection")
        nodes = self.k8s_client.get_nodes()
        pods = self.k8s_client.get_all_pods()
        estimated_cost = self.kubecost_client.get_total_monthly_cost()
        state['cluster_state'] = ClusterState(
            total_nodes=len(nodes), total_pods=len(pods),
            total_namespaces=len({pod.metadata.namespace for pod in pods}),
            resource_usage={'cpu_utilization_percent': 65.0, 'memory_utilization_percent': 72.0},
            cost_metrics={'estimated_monthly_cost_usd': estimated_cost}
        )
        return state
    
    def _analyze_cluster_node(self, state: dict) -> dict:
        log = self._log_node_entry(state, "analyze_cluster")
        log.info("Starting AI cluster analysis")
        cluster_state_model = state['cluster_state']
        prompt = f"Analyze the following Kubernetes cluster state and provide a brief, one-sentence summary of the primary cost optimization opportunities. Cluster State: {cluster_state_model.model_dump_json(indent=2)}"
        try:
            response = self.llm.invoke(prompt)
            state['ai_analysis'] = response.content
            log.info("AI analysis completed")
        except Exception as e:
            log.error("AI analysis failed", error=str(e))
            state['ai_analysis'] = "AI analysis was not available for this run."
        return state
    
    def _generate_actions_node(self, state: dict) -> dict:
        log = self._log_node_entry(state, "generate_actions")
        log.info("Generating optimization actions from tools")
        all_actions = []
        for tool in self.tools:
            try:
                actions = tool.analyze()
                all_actions.extend(actions)
            except Exception as e:
                log.error(f"Tool {tool.__class__.__name__} failed during analysis", error=str(e))
        state['actions'] = all_actions
        log.info(f"Generated {len(all_actions)} total actions.")
        return state
        
    def _validate_safety_node(self, state: dict) -> dict:
        log = self._log_node_entry(state, "validate_safety")
        log.info("Validating generated actions")
        state['actions'] = self.safety_controller.validate_actions(state.get('actions', []), state.get('run_id'))
        return state
        
    def _generate_report_node(self, state: dict) -> dict:
        log = self._log_node_entry(state, "generate_report")
        log.info("Generating final report of potential actions")
        actions = state.get('actions', [])
        approved_actions = [a for a in actions if a.status == ActionStatus.APPROVED]
        state['report'] = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_actions_generated': len(actions),
            'actions_approved_for_review': len(approved_actions),
            'dry_run': state.get('dry_run'),
            'ai_analysis_summary': state.get('ai_analysis')
        }
        return state