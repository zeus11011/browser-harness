from pathlib import Path
# pyrefly: ignore [missing-import]
from browser_ops.selenium_wrapper.session import SessionManager
# pyrefly: ignore [missing-import]
from browser_ops.server import McpServerApp
# pyrefly: ignore [missing-import]
from browser_ops.models import TestStore


def main():
    session_manager = SessionManager(headless=True)
    test_store = TestStore(work_dir=Path.cwd())
    app = McpServerApp(session_manager, test_store)
    app.mcp.run()


if __name__ == "__main__":
    main()