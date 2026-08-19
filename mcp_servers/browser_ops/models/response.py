from typing import Optional, List, Any
from pydantic import BaseModel

class StepResult(BaseModel):
    step_id: Any
    status: str  # "success", "failed", "skipped"
    duration_ms: int
    error: Optional[str] = None
    screenshot: Optional[str] = None

class ExecutionResponse(BaseModel):
    success: bool
    session_id: Optional[str] = None
    results: List[StepResult]

class PingResponse(BaseModel):
    status: str = "pong"

class GeneralResponse(BaseModel):
    success: bool
    session_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None
