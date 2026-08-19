from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .step import Locator, Step
class SessionInfo(BaseModel):
    id: str
    port: int
    steps_count: int
    is_active: bool


class MouseEvents(BaseModel):
    locator: Locator


class ElementTextParams(BaseModel):
    locator: Locator
    value: str


class NavigateParams(BaseModel):
    url: str


class ValueParams(BaseModel):
    value: str


class SleepParams(BaseModel):
    ms: int


class WaitParams(BaseModel):
    locator: Locator
    timeout_ms: Optional[int] = None


class JavascriptParams(BaseModel):
    script: str


class ScrollParams(BaseModel):
    x: int = 0
    y: int = 0


class VerifyAttributeParams(BaseModel):
    locator: Locator
    attribute: str
    expected_value: str


class DragAndDropParams(BaseModel):
    source: Locator
    target: Locator


class ScreenshotParams(BaseModel):
    locator: Optional[Locator] = None
    path: Optional[str] = None


class ClickFromImageParams(BaseModel):
    x: int
    y: int


class EmptyParams(BaseModel):
    pass


class CreateSessionParams(BaseModel):
    headless: Optional[bool] = None


class CloseSessionParams(BaseModel):
    session_id: Optional[str] = None


class SwitchSessionParams(BaseModel):
    session_id: str


class UpdateSessionParams(BaseModel):
    session_id: Optional[str] = None
    steps: List[Step]


class SaveSessionParams(BaseModel):
    session_id: Optional[str] = None
    test_id: Optional[str] = None
    save_to_disk: Optional[bool] = True


class SessionDetail(BaseModel):
    session_id: str
    port: int
    steps_count: int
    is_active: bool
    steps: Optional[List[Step]] = None


class SessionResponse(BaseModel):
    success: bool
    session_id: Optional[str] = None
    message: str
    session: Optional[SessionDetail] = None


class SessionListResult(BaseModel):
    success: bool
    count: int
    active_session_id: Optional[str] = None
    sessions: List[SessionInfo]


class SaveSessionResult(BaseModel):
    success: bool
    test_id: str
    step_count: int
    saved_to_disk: bool
    path: Optional[str] = None
    message: str
