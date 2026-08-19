import asyncio
import uuid
from typing import Optional, List, Dict, Any
try:
    from fastmcp import FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP

from .selenium_wrapper.session import SessionManager, Session
from .models.test_store import TestStore
from .models.step import Step, Locator
from .models.test import Test
from .models.response import StepResult
from .executor.step_executor import StepExecutor
from .models import (
    SessionResponse, SessionDetail, SessionListResult, SaveSessionResult
)

class McpServerApp:
    def __init__(self, session_manager: SessionManager, test_store: TestStore):
        self.session_manager = session_manager
        self.test_store = test_store
        self.step_executor = StepExecutor()
        self.active_session_id: Optional[str] = None
        self._lock = asyncio.Lock()
        self.mcp = FastMCP("browser_ops")
        self._register_tools()

    async def get_active_session(self) -> Session:
        async with self._lock:
            if self.active_session_id:
                sess = await self.session_manager.get_session(self.active_session_id)
                if sess:
                    return sess
            # If missing or closed, get/create one dynamically
            sess = await self.session_manager.get_or_create_session(None)
            self.active_session_id = sess.id
            return sess

    async def _run_step(
        self,
        step_type: str,
        locator: Optional[Locator] = None,
        value: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> StepResult:
        step = Step(
            id=str(uuid.uuid4()),
            step_type=step_type,
            locator=locator,
            value=value,
            params=params
        )
        try:
            session = await self.get_active_session()
        except Exception as e:
            return StepResult(
                step_id=step.id,
                status="failed",
                duration_ms=0,
                error=f"Session error: {e}"
            )

        res = await self.step_executor.execute_step(session.driver, step)

        if res.status == "success":
            async with session._lock:
                session.last_steps.append(step)
                current_steps = list(session.last_steps)

            test_id = f"session_{session.id}"
            test = Test(
                id=test_id,
                name=f"Recorded Test for session {session.id}",
                steps=current_steps,
                continue_on_failure=False
            )
            existing = await self.test_store.get(test_id)
            if existing:
                await self.test_store.update(test)
            else:
                await self.test_store.create(test)

        return res

    def _register_tools(self):
        # Mouse & Click Commands
        @self.mcp.tool(description="Click on a web element specified by locator")
        async def click(locator: Locator) -> Dict[str, Any]:
            res = await self._run_step("click", locator)
            return res.model_dump()

        @self.mcp.tool(description="Double-click on a web element specified by locator")
        async def double_click(locator: Locator) -> Dict[str, Any]:
            res = await self._run_step("double_click", locator)
            return res.model_dump()

        @self.mcp.tool(description="Right-click on a web element specified by locator")
        async def right_click(locator: Locator) -> Dict[str, Any]:
            res = await self._run_step("right_click", locator)
            return res.model_dump()

        @self.mcp.tool(description="Hover mouse cursor over a web element specified by locator")
        async def hover(locator: Locator) -> Dict[str, Any]:
            res = await self._run_step("hover", locator)
            return res.model_dump()

        @self.mcp.tool(description="Drag element from source locator and drop onto target locator")
        async def drag_and_drop(source: Locator, target: Locator) -> Dict[str, Any]:
            res = await self._run_step("drag_and_drop", source, params={"target": target.model_dump()})
            return res.model_dump()

        @self.mcp.tool(description="Click element at (x, y) coordinates and return its XPath")
        async def click_from_image(x: int, y: int) -> Dict[str, Any]:
            res = await self._run_step("click_from_image", params={"x": x, "y": y})
            return res.model_dump()

        # Text & Input Commands
        @self.mcp.tool(description="Type text into an input element specified by locator")
        async def type_text(locator: Locator, value: str) -> Dict[str, Any]:
            res = await self._run_step("type_text", locator, value=value)
            return res.model_dump()

        @self.mcp.tool(description="Clear input text from element specified by locator")
        async def clear(locator: Locator) -> Dict[str, Any]:
            res = await self._run_step("clear", locator)
            return res.model_dump()

        @self.mcp.tool(description="Submit a form element specified by locator")
        async def submit(locator: Locator) -> Dict[str, Any]:
            res = await self._run_step("submit", locator)
            return res.model_dump()

        @self.mcp.tool(description="Press a specific key on an element specified by locator")
        async def press_key(locator: Locator, value: str) -> Dict[str, Any]:
            res = await self._run_step("press_key", locator, value=value)
            return res.model_dump()

        @self.mcp.tool(description="Upload a file from file_path to input element specified by locator")
        async def upload_file(locator: Locator, value: str) -> Dict[str, Any]:
            res = await self._run_step("upload_file", locator, value=value)
            return res.model_dump()

        # Select Commands
        @self.mcp.tool(description="Select an option from dropdown by visible text")
        async def select_by_text(locator: Locator, value: str) -> Dict[str, Any]:
            res = await self._run_step("select_by_text", locator, value=value)
            return res.model_dump()

        @self.mcp.tool(description="Select an option from dropdown by value attribute")
        async def select_by_value(locator: Locator, value: str) -> Dict[str, Any]:
            res = await self._run_step("select_by_value", locator, value=value)
            return res.model_dump()

        @self.mcp.tool(description="Select an option from dropdown by index")
        async def select_by_index(locator: Locator, value: str) -> Dict[str, Any]:
            res = await self._run_step("select_by_index", locator, value=value)
            return res.model_dump()

        @self.mcp.tool(description="Deselect options in multi-select element")
        async def deselect(locator: Locator) -> Dict[str, Any]:
            res = await self._run_step("deselect", locator)
            return res.model_dump()

        # Navigation Commands
        @self.mcp.tool(description="Navigate browser to target URL")
        async def navigate(url: str) -> Dict[str, Any]:
            res = await self._run_step("navigate", value=url)
            return res.model_dump()

        @self.mcp.tool(description="Refresh current webpage")
        async def refresh() -> Dict[str, Any]:
            res = await self._run_step("refresh")
            return res.model_dump()

        @self.mcp.tool(description="Navigate backward in browser history")
        async def back() -> Dict[str, Any]:
            res = await self._run_step("back")
            return res.model_dump()

        @self.mcp.tool(description="Navigate forward in browser history")
        async def forward() -> Dict[str, Any]:
            res = await self._run_step("forward")
            return res.model_dump()

        # Wait & Sleep Commands
        @self.mcp.tool(description="Wait for element to be present on page")
        async def wait(locator: Locator, timeout_ms: Optional[int] = None) -> Dict[str, Any]:
            params = {"timeout": timeout_ms} if timeout_ms else None
            res = await self._run_step("wait", locator=locator, params=params)
            return res.model_dump()

        @self.mcp.tool(description="Pause execution for duration in ms")
        async def sleep(ms: int) -> Dict[str, Any]:
            res = await self._run_step("sleep", value=str(ms))
            return res.model_dump()

        # JS & Scroll Commands
        @self.mcp.tool(description="Execute arbitrary JavaScript in browser context")
        async def execute_javascript(script: str) -> Dict[str, Any]:
            res = await self._run_step("execute_javascript", value=script)
            return res.model_dump()

        @self.mcp.tool(description="Scroll page by x and y pixel offsets")
        async def scroll(x: int = 0, y: int = 0) -> Dict[str, Any]:
            res = await self._run_step("scroll", params={"x": x, "y": y})
            return res.model_dump()

        @self.mcp.tool(description="Scroll page until target element is in view")
        async def scroll_into_view(locator: Locator) -> Dict[str, Any]:
            res = await self._run_step("scroll_into_view", locator=locator)
            return res.model_dump()

        # Frame, Window & Alert Commands
        @self.mcp.tool(description="Switch context to iframe specified by locator")
        async def switch_frame(locator: Locator) -> Dict[str, Any]:
            res = await self._run_step("switch_frame", locator=locator)
            return res.model_dump()

        @self.mcp.tool(description="Switch active window or tab by handle or title")
        async def switch_window(value: str) -> Dict[str, Any]:
            res = await self._run_step("switch_window", value=value)
            return res.model_dump()

        @self.mcp.tool(description="Accept active JavaScript alert dialog")
        async def accept_alert() -> Dict[str, Any]:
            res = await self._run_step("accept_alert")
            return res.model_dump()

        @self.mcp.tool(description="Dismiss active JavaScript alert dialog")
        async def dismiss_alert() -> Dict[str, Any]:
            res = await self._run_step("dismiss_alert")
            return res.model_dump()

        # Screenshot Command
        @self.mcp.tool(description="Take a screenshot of full page or element, optionally saving to file path")
        async def screenshot(locator: Optional[Locator] = None, path: Optional[str] = None) -> Dict[str, Any]:
            params = {"path": path} if path else None
            res = await self._run_step("screenshot", locator=locator, params=params)
            return res.model_dump()

        # Verifications
        @self.mcp.tool(description="Verify element text matches expected string")
        async def verify_text(locator: Locator, value: str) -> Dict[str, Any]:
            res = await self._run_step("verify_text", locator=locator, value=value)
            return res.model_dump()

        @self.mcp.tool(description="Verify element attribute matches expected value")
        async def verify_attribute(locator: Locator, attribute: str, expected_value: str) -> Dict[str, Any]:
            res = await self._run_step("verify_attribute", locator=locator, value=expected_value, params={"attribute": attribute})
            return res.model_dump()

        @self.mcp.tool(description="Verify page title matches expected value")
        async def verify_title(value: str) -> Dict[str, Any]:
            res = await self._run_step("verify_title", value=value)
            return res.model_dump()

        @self.mcp.tool(description="Verify current page URL matches expected value")
        async def verify_url(value: str) -> Dict[str, Any]:
            res = await self._run_step("verify_url", value=value)
            return res.model_dump()

        @self.mcp.tool(description="Verify element exists in DOM")
        async def verify_exists(locator: Locator) -> Dict[str, Any]:
            res = await self._run_step("verify_exists", locator=locator)
            return res.model_dump()

        @self.mcp.tool(description="Verify element is currently visible")
        async def verify_visible(locator: Locator) -> Dict[str, Any]:
            res = await self._run_step("verify_visible", locator=locator)
            return res.model_dump()

        @self.mcp.tool(description="Verify element is enabled")
        async def verify_enabled(locator: Locator) -> Dict[str, Any]:
            res = await self._run_step("verify_enabled", locator=locator)
            return res.model_dump()

        @self.mcp.tool(description="Verify element is selected")
        async def verify_selected(locator: Locator) -> Dict[str, Any]:
            res = await self._run_step("verify_selected", locator=locator)
            return res.model_dump()

        @self.mcp.tool(description="Verify computed CSS property matches expected value")
        async def verify_css(locator: Locator, property_name: str, expected_value: str) -> Dict[str, Any]:
            res = await self._run_step("verify_css", locator=locator, value=expected_value, params={"property": property_name})
            return res.model_dump()

        @self.mcp.tool(description="Verify element count matches expected value")
        async def verify_count(locator: Locator, expected_count: int) -> Dict[str, Any]:
            res = await self._run_step("verify_count", locator=locator, value=str(expected_count))
            return res.model_dump()

        # Session CRUD Tools
        @self.mcp.tool(description="Create a new browser session and set it as active")
        async def create_session(headless: Optional[bool] = None) -> Dict[str, Any]:
            sess = await self.session_manager.create_session()
            async with self._lock:
                self.active_session_id = sess.id
            return SessionResponse(
                success=True,
                session_id=sess.id,
                message=f"Session '{sess.id}' created and set as active",
                session=SessionDetail(session_id=sess.id, port=sess.port, steps_count=0, is_active=True, steps=[])
            ).model_dump()

        @self.mcp.tool(description="Close and delete a browser session by ID, or active session if unspecified")
        async def delete_session(session_id: Optional[str] = None) -> Dict[str, Any]:
            target_id = session_id or self.active_session_id
            if not target_id:
                return SessionResponse(success=False, message="No active session to delete").model_dump()
            await self.session_manager.close_session(target_id)
            async with self._lock:
                if self.active_session_id == target_id:
                    self.active_session_id = None
            return SessionResponse(success=True, session_id=target_id, message=f"Session '{target_id}' deleted").model_dump()

        @self.mcp.tool(description="Switch active browsing session to specified session ID")
        async def switch_session(session_id: str) -> Dict[str, Any]:
            sess = await self.session_manager.get_session(session_id)
            if not sess:
                return SessionResponse(success=False, session_id=session_id, message=f"Session '{session_id}' not found").model_dump()
            async with self._lock:
                self.active_session_id = session_id
            async with sess._lock:
                cnt = len(sess.last_steps)
            return SessionResponse(
                success=True,
                session_id=session_id,
                message=f"Switched active session to '{session_id}'",
                session=SessionDetail(session_id=session_id, port=sess.port, steps_count=cnt, is_active=True)
            ).model_dump()

        @self.mcp.tool(description="List all running browser sessions")
        async def list_sessions() -> Dict[str, Any]:
            sessions = await self.session_manager.list_sessions(self.active_session_id)
            return SessionListResult(
                success=True,
                count=len(sessions),
                active_session_id=self.active_session_id,
                sessions=sessions
            ).model_dump()

        @self.mcp.tool(description="Get details and step history for a session")
        async def get_session_info(session_id: Optional[str] = None) -> Dict[str, Any]:
            target_id = session_id or self.active_session_id
            sess = await self.session_manager.get_session(target_id) if target_id else None
            if not sess:
                return SessionResponse(success=False, message="Session not found").model_dump()
            async with sess._lock:
                steps = list(sess.last_steps)
            return SessionResponse(
                success=True,
                session_id=sess.id,
                message=f"Retrieved session '{sess.id}' info",
                session=SessionDetail(
                    session_id=sess.id,
                    port=sess.port,
                    steps_count=len(steps),
                    is_active=(self.active_session_id == sess.id),
                    steps=steps
                )
            ).model_dump()

        @self.mcp.tool(description="Update step history for a session")
        async def update_session(steps: List[Step], session_id: Optional[str] = None) -> Dict[str, Any]:
            target_id = session_id or self.active_session_id
            if not target_id:
                return SessionResponse(success=False, message="No active session").model_dump()
            step_objs = steps
            await self.session_manager.update_session_steps(target_id, step_objs)
            
            test_id = f"session_{target_id}"
            test = Test(id=test_id, name=f"Recorded Test for session {target_id}", steps=step_objs)
            if await self.test_store.get(test_id):
                await self.test_store.update(test)
            else:
                await self.test_store.create(test)

            return SessionResponse(success=True, session_id=target_id, message=f"Session '{target_id}' steps updated").model_dump()

        @self.mcp.tool(description="Save session recorded steps as a reusable test or persist to disk")
        async def save_session(
            session_id: Optional[str] = None,
            test_id: Optional[str] = None,
            save_to_disk: bool = True
        ) -> Dict[str, Any]:
            target_id = session_id or self.active_session_id
            if not target_id:
                return SaveSessionResult(success=False, test_id="", step_count=0, saved_to_disk=False, message="No active session").model_dump()

            sess = await self.session_manager.get_session(target_id)
            if not sess:
                return SaveSessionResult(success=False, test_id="", step_count=0, saved_to_disk=False, message=f"Session '{target_id}' not found").model_dump()

            async with sess._lock:
                steps = list(sess.last_steps)

            tid = test_id or f"session_{sess.id}"
            test = Test(id=tid, name=f"Saved from session {sess.id}", steps=steps)

            if await self.test_store.get(tid):
                await self.test_store.update(test)
            else:
                await self.test_store.create(test)

            file_path = None
            if save_to_disk:
                p = await self.test_store.save(tid)
                file_path = str(p)

            return SaveSessionResult(
                success=True,
                test_id=tid,
                step_count=len(steps),
                saved_to_disk=save_to_disk,
                path=file_path,
                message=f"Saved session '{target_id}' with {len(steps)} steps"
            ).model_dump()
