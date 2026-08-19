import socket
import uuid
import asyncio
from typing import Dict, List, Optional
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
try:
    # pyrefly: ignore [missing-import]
    from webdriver_manager.chrome import ChromeDriverManager
    _HAS_WDM = True
except ImportError:
    _HAS_WDM = False

from ..models.step import Step
from ..errors import AppError

class SessionInfo(BaseModel):
    id: str
    port: int
    steps_count: int
    is_active: bool

class Session:
    def __init__(self, session_id: str, driver: webdriver.Chrome, port: int):
        self.id = session_id
        self.driver = driver
        self.port = port
        self.last_steps: List[Step] = []
        self._lock = asyncio.Lock()

def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

class SessionManager:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.sessions: Dict[str, Session] = {}
        self._lock = asyncio.Lock()

    async def create_session(self) -> Session:
        async with self._lock:
            session_id = str(uuid.uuid4())
            port = find_free_port()

            options = ChromeOptions()
            if self.headless:
                options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--start-maximized")

            # Run blocking Selenium driver initialization in a thread pool
            loop = asyncio.get_running_loop()
            try:
                def _init_driver():
                    if _HAS_WDM:
                        service = ChromeService(ChromeDriverManager().install(), port=port)
                    else:
                        service = ChromeService(port=port)
                    return webdriver.Chrome(service=service, options=options)
                
                driver = await loop.run_in_executor(None, _init_driver)
            except Exception as e:
                raise AppError(f"Failed to launch ChromeDriver: {e}")

            session = Session(session_id, driver, port)
            self.sessions[session_id] = session
            return session

    async def get_session(self, session_id: str) -> Optional[Session]:
        async with self._lock:
            return self.sessions.get(session_id)

    async def get_or_create_session(self, session_id: Optional[str] = None) -> Session:
        async with self._lock:
            if session_id and session_id in self.sessions:
                return self.sessions[session_id]
            if self.sessions:
                return next(iter(self.sessions.values()))
        # If no active session, release lock before create_session
        return await self.create_session()

    async def list_sessions(self, active_id: Optional[str] = None) -> List[SessionInfo]:
        async with self._lock:
            res = []
            for sid, sess in self.sessions.items():
                async with sess._lock:
                    cnt = len(sess.last_steps)
                res.append(SessionInfo(
                    id=sid,
                    port=sess.port,
                    steps_count=cnt,
                    is_active=(active_id == sid)
                ))
            return res

    async def update_session_steps(self, session_id: str, steps: List[Step]) -> None:
        async with self._lock:
            sess = self.sessions.get(session_id)
            if not sess:
                raise AppError(f"Session '{session_id}' not found")
            async with sess._lock:
                sess.last_steps = list(steps)

    async def close_session(self, session_id: str) -> None:
        async with self._lock:
            sess = self.sessions.pop(session_id, None)
            if sess:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, sess.driver.quit)

    async def close_all(self) -> None:
        async with self._lock:
            sessions = list(self.sessions.values())
            self.sessions.clear()
            loop = asyncio.get_running_loop()
            for sess in sessions:
                try:
                    await loop.run_in_executor(None, sess.driver.quit)
                except Exception:
                    pass
