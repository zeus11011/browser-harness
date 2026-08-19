from pathlib import Path
from mcp_servers.browser_ops.selenium_wrapper.session import SessionManager
from mcp_servers.browser_ops.server import McpServerApp
from mcp_servers.browser_ops.models import TestStore


def main():
    session_manager = SessionManager(headless=True)
    test_store = TestStore(work_dir=Path.cwd())
    app = McpServerApp(session_manager, test_store)
    app.mcp.run(transport="streamable-http", host="127.0.0.1", port=8080)


if __name__ == "__main__":
    main()