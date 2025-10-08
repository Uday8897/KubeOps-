from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import uuid

class OptimizationType(str, Enum):
    POD_CLEANUP = "pod_cleanup"
    PVC_CLEANUP = "pvc_cleanup"
    RIGHTSIZING = "rightsizing"
    HPA_OPTIMIZATION = "hpa_optimization"
    NODE_OPTIMIZATION = "node_optimization"

class ActionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTED = "executed"
    FAILED = "failed"
    REJECTED = "rejected"

class RunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

# This class is used for the request body of the /optimize endpoint
class OptimizationRequest(BaseModel):
    dry_run: Optional[bool] = None

# --- THIS IS THE MISSING CLASS ---
# This class defines the response when an optimization run is first scheduled
class OptimizationScheduledResponse(BaseModel):
    run_id: str
    status: RunStatus
    detail: str

class OptimizationAction(BaseModel):
    id: str = Field(default_factory=lambda: f"action_{uuid.uuid4().hex[:8]}")
    type: OptimizationType
    target: str
    namespace: str
    action_details: Dict[str, Any]
    estimated_savings: float = 0.0
    confidence: float = Field(ge=0, le=1)
    status: ActionStatus = ActionStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None
    error: Optional[str] = None

class ClusterState(BaseModel):
    total_nodes: int
    total_pods: int
    total_namespaces: int
    resource_usage: Dict[str, float]
    cost_metrics: Dict[str, float]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class OptimizationRun(BaseModel):
    run_id: str
    status: RunStatus
    report: Optional[Dict[str, Any]] = None
    detail: Optional[str] = None
    actions: List[OptimizationAction] = []

