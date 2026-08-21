"""Connection to the browser_ops MCP server."""

from langchain_mcp_adapters.client import MultiServerMCPClient

from graph.prompts import PROJECT_ROOT

BROWSER_OPS_SERVER = PROJECT_ROOT / "mcp_servers" / "server.py"


async def get_browser_ops_tools():
    # Same server this project's client.py talks to: mcp_servers/server.py
    client = MultiServerMCPClient(
        {
            "browser_ops": {
                "command": "python",
                "args": [str(BROWSER_OPS_SERVER)],
                "transport": "stdio",
            }
        }
    )
    return await client.get_tools()
