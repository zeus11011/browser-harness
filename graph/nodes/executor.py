"""Executor node: runs exactly one step of the plan via the browser_ops tools."""

from graph.prompts import system_prompt
from graph.state import GraphState


def make_executor_node(llm, tools):
    llm_with_tools = llm.bind_tools(tools)
    prompt = system_prompt("manual-test")

    async def executor(state: GraphState):
        plan = state["plan"]
        index = state["step_index"]
        context = (
            f"Plan step {index + 1} of {len(plan)}: {plan[index]}\n\n"
            "Execute ONLY this step using the browser_ops tools. Do not run any "
            "later step. If this step needs no tool call, say why instead."
        )
        if feedback := state.get("feedback"):
            context += f"\n\nThe previous attempt at this step failed: {feedback}"

        response = await llm_with_tools.ainvoke(
            [
                {"role": "system", "content": prompt},
                *state["messages"],
                {"role": "user", "content": context},
            ]
        )
        return {"messages": [response], "feedback": ""}

    return executor
