import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from graph import build_graph


async def main():
    agent = await build_graph()
    # Run the agent
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
        # plan/execute/verify loops once per step, so the default limit of 25 is low
        config={"recursion_limit": 100},
    )
    print(response)
    # Print the agent's response
    messages = response.get("messages", [])
    if messages:
        last_message = messages[-1]
        if hasattr(last_message, "content"):
            print(last_message.content)
        else:
            print(last_message)
    else:
        print(response)


if __name__ == "__main__":
   asyncio.run(main())