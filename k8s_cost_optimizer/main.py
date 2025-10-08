from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, List

from k8s_cost_optimizer.config import settings
from k8s_cost_optimizer.utils.logger import setup_logging, logger
from k8s_cost_optimizer.agents.orchestrator import AICostOptimizationOrchestrator
from k8s_cost_optimizer.models.schemas import (
    OptimizationRequest,
    OptimizationRun,
    OptimizationScheduledResponse,
    RunStatus,
    OptimizationAction,
    ActionStatus
)

setup_logging(settings.log_level)
app = FastAPI(title="Kubernetes AI Cost Optimization Agent", version="3.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator: AICostOptimizationOrchestrator

class AppState:
    def __init__(self):
        self.runs: Dict[str, OptimizationRun] = {}
        self.pending_actions: Dict[str, OptimizationAction] = {}
        self.activity_log: List[OptimizationAction] = []
        self.stats = {"total_savings": 0.0, "actions_executed": 0}

STATE = AppState()

@app.on_event("startup")
async def startup_event():
    global orchestrator
    logger.info("Application starting up...")
    try:
        orchestrator = AICostOptimizationOrchestrator(settings)
        logger.info("Orchestrator initialized successfully.")
    except Exception as e:
        logger.error("Fatal: Failed to initialize orchestrator", error=str(e), exc_info=True)
        orchestrator = None

async def execute_autonomous_action(action: OptimizationAction):
    success, message = await orchestrator.execute_single_action(action)
    action.executed_at = datetime.utcnow()
    if success:
        action.status = ActionStatus.EXECUTED
        STATE.stats["total_savings"] += action.estimated_savings
        STATE.stats["actions_executed"] += 1
    else:
        action.status = ActionStatus.FAILED
        action.error = message
    STATE.activity_log.insert(0, action) # Prepend to show newest first

def execute_analysis_run(run_id: str, dry_run: bool, background_tasks: BackgroundTasks):
    STATE.runs[run_id].status = RunStatus.RUNNING
    try:
        result = orchestrator.run_and_categorize_actions(run_id, dry_run)
        
        run_record = STATE.runs[run_id]
        if "error" in result:
            run_record.status = RunStatus.FAILED
            run_record.detail = result["error"]
        else:
            run_record.status = RunStatus.COMPLETED
            run_record.report = result["report"]
            # --- Store all generated actions with the run ---
            run_record.actions = result.get("pending_actions", []) + result.get("auto_execute_actions", [])
            
            for action in result["pending_actions"]:
                STATE.pending_actions[action.id] = action
            
            for action in result["auto_execute_actions"]:
                background_tasks.add_task(execute_autonomous_action, action)
            
            logger.info(f"Analysis {run_id} complete. Queued {len(result['pending_actions'])} actions for HITL and {len(result['auto_execute_actions'])} for auto-execution.")

    except Exception as e:
        logger.error("Unhandled exception during analysis run", run_id=run_id, error=str(e), exc_info=True)
        STATE.runs[run_id].status = RunStatus.FAILED
        STATE.runs[run_id].detail = "An internal error occurred."

@app.post("/optimize", status_code=status.HTTP_202_ACCEPTED, response_model=OptimizationScheduledResponse)
async def schedule_optimization(request: OptimizationRequest, background_tasks: BackgroundTasks):
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator is not available.")
    
    run_id = f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    dry_run = request.dry_run if request.dry_run is not None else settings.agent.dry_run
    
    STATE.runs[run_id] = OptimizationRun(run_id=run_id, status=RunStatus.PENDING)
    background_tasks.add_task(execute_analysis_run, run_id, dry_run, background_tasks)
    
    return OptimizationScheduledResponse(run_id=run_id, status=RunStatus.PENDING, detail="Optimization analysis run has been scheduled.")

@app.post("/actions/{action_id}/approve", response_model=OptimizationAction)
async def approve_action(action_id: str):
    if action_id not in STATE.pending_actions:
        raise HTTPException(status_code=404, detail="Pending action not found.")
    action = STATE.pending_actions.pop(action_id)
    await execute_autonomous_action(action)
    return action

@app.post("/actions/{action_id}/reject", response_model=OptimizationAction)
async def reject_action(action_id: str):
    if action_id not in STATE.pending_actions:
        raise HTTPException(status_code=404, detail="Pending action not found.")
    action = STATE.pending_actions.pop(action_id)
    action.status = ActionStatus.REJECTED
    action.executed_at = datetime.utcnow()
    STATE.activity_log.insert(0, action)
    logger.info("Action rejected by user", action_id=action_id)
    return action

@app.get("/health")
async def health_check():
    return {"status": "ok" if orchestrator else "degraded"}

@app.get("/dashboard/stats", response_model=Dict)
async def get_dashboard_stats():
    return {
        "totalSavings": STATE.stats["total_savings"],
        "actionsExecuted": STATE.stats["actions_executed"],
        "pendingActions": len(STATE.pending_actions)
    }

@app.get("/actions/pending", response_model=List[OptimizationAction])
async def get_pending_actions():
    return list(STATE.pending_actions.values())

@app.get("/activities", response_model=List[OptimizationAction])
async def get_activity_log():
    return STATE.activity_log[:20]

@app.get("/runs", response_model=List[OptimizationRun])
async def get_all_runs():
    return sorted(list(STATE.runs.values()), key=lambda r: r.run_id, reverse=True)

@app.get("/runs/{run_id}", response_model=OptimizationRun)
async def get_run_details(run_id: str):
    if run_id not in STATE.runs:
        raise HTTPException(status_code=404, detail="Run not found.")
    return STATE.runs[run_id]

