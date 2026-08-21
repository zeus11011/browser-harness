"""Planning node: breaks the user's manual steps into atomic, executable steps."""

from graph.prompts import system_prompt
from graph.state import GraphState, Plan

BASE_INSTRUCTION = (
    "Break the user's manual steps down into the simplest possible atomic steps."
)


def make_planning_node(llm):
    planner_llm = llm.with_structured_output(Plan)
    prompt = system_prompt("planner")

    async def planning(state: GraphState):
        instruction = BASE_INSTRUCTION
        if feedback := state.get("feedback"):
            instruction += (
                "\n\nA previous plan failed to execute. Re-simplify it, "
                f"addressing this feedback:\n{feedback}"
            )

        plan = await planner_llm.ainvoke(
            [
                {"role": "system", "content": prompt},
                *state["messages"],
                {"role": "user", "content": instruction},
            ]
        )
        rendered = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(plan.steps))

        return {
            "messages": [{"role": "assistant", "content": f"Plan:\n{rendered}"}],
            "plan": plan.steps,
            "step_index": 0,
            "retries": 0,
            "replans": state.get("replans", 0),
            "feedback": "",
        }

    return planning
