"""Graph state and the structured outputs the nodes produce."""

from typing import Annotated, Literal, TypedDict

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class Plan(BaseModel):
    """Atomic steps produced by the planner."""

    steps: list[str] = Field(
        description="Ordered atomic steps, each one browser action or verification."
    )


class Verdict(BaseModel):
    """The verifier's judgement on the step the executor just ran."""

    status: Literal["pass", "retry", "replan"] = Field(
        description=(
            "'pass' if the step achieved its intent; "
            "'retry' if the step was clear but the executor botched the execution; "
            "'replan' if the step itself was too vague/ambiguous to execute."
        )
    )
    reason: str = Field(description="Short explanation of the verdict.")


class GraphState(TypedDict):
    messages: Annotated[list, add_messages]
    plan: list[str]
    step_index: int
    retries: int
    replans: int
    feedback: str
