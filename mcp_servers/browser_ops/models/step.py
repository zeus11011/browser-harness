from typing import Optional, Any, Union, Dict
from pydantic import BaseModel, Field
import uuid

class Locator(BaseModel):
    by: str = Field(
        description="Locator strategy to find element on page (e.g. 'css', 'xpath', 'id', 'name', 'class_name', 'tag_name', 'link_text', 'partial_link_text')"
    )
    value: str = Field(
        description="Selector or search string value (e.g. '#submit-btn', '//div[@class=\"nav\"]', 'username')"
    )

class Step(BaseModel):
    id: Any = Field(default_factory=lambda: str(uuid.uuid4()))
    step_type: str
    locator: Optional[Locator] = None
    value: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
