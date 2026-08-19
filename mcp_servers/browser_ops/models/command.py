from typing import Optional, List, Any, Literal, Union
from pydantic import BaseModel, Field
from .step import Step
from .test import Test

class SocketCommand(BaseModel):
    command: str
    session_id: Optional[str] = None
    steps: Optional[List[Step]] = None
    test: Optional[Test] = None
    start: Optional[int] = None
    end: Optional[int] = None
    id: Optional[str] = None
