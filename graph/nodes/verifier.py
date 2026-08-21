"""Verifier node: judges whether the step the executor just ran achieved its intent."""

from graph.prompts import system_prompt
from graph.state import GraphState, Verdict


def make_verifier_node(llm):
    verifier_llm = llm.with_structured_output(Verdict)
    prompt = system_prompt("verifier")

    async def verifier(state: GraphState):
        index = state["step_index"]
        step = state["plan"][index]

        verdict = await verifier_llm.ainvoke(
            [
                {"role": "system", "content": prompt},
                *state["messages"],
                {
                    "role": "user",
                    "content": f"Did this step succeed? Step {index + 1}: {step}",
                },
            ]
        )
        note = {
            "role": "assistant",
            "content": f"[verifier] step {index + 1} -> {verdict.status}: {verdict.reason}",
        }

        if verdict.status == "pass":
            return {
                "messages": [note],
                "step_index": index + 1,
                "retries": 0,
                "feedback": "",
            }
        if verdict.status == "retry":
            return {
                "messages": [note],
                "retries": state.get("retries", 0) + 1,
                "feedback": verdict.reason,
            }
        return {
            "messages": [note],
            "replans": state.get("replans", 0) + 1,
            "retries": 0,
            "feedback": verdict.reason,
        }

    return verifier
