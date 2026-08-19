from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
from .step import Step

class Test(BaseModel):
    __test__ = False
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Unnamed Test"
    description: Optional[str] = None
    steps: List[Step] = Field(default_factory=list)
    continue_on_failure: bool = False
