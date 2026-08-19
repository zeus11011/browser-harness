import asyncio
from typing import Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .base import SeleniumCommand
from ..selenium_wrapper.locator import to_by
from ..errors import MissingLocatorError

class WaitCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("wait")
        timeout_ms = 10000
        if self.step.params and "timeout" in self.step.params:
            try:
                timeout_ms = int(self.step.params["timeout"])
            except ValueError:
                pass
        timeout_sec = timeout_ms / 1000.0
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            WebDriverWait(driver, timeout_sec).until(
                EC.presence_of_element_located((by, val))
            )
        await loop.run_in_executor(None, _action)
        return None

class SleepCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        ms = 1000
        if self.step.value:
            try:
                ms = int(self.step.value)
            except ValueError:
                pass
        await asyncio.sleep(ms / 1000.0)
        return None
