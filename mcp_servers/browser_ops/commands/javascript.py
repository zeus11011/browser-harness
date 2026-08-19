import asyncio
from typing import Any
from selenium.webdriver.remote.webdriver import WebDriver

from .base import SeleniumCommand
from ..selenium_wrapper.locator import to_by
from ..errors import MissingLocatorError, AppError

class ExecuteJavascriptCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        script = self.step.value
        if not script:
            raise AppError("execute_javascript requires a 'value' containing script string")
        loop = asyncio.get_running_loop()
        res = await loop.run_in_executor(None, driver.execute_script, script)
        return str(res) if res is not None else None

class ScrollCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        x = 0
        y = 0
        if self.step.params:
            x = int(self.step.params.get("x", 0))
            y = int(self.step.params.get("y", 0))
        script = f"window.scrollBy({x}, {y});"
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, driver.execute_script, script)
        return None

class ScrollIntoViewCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("scroll_into_view")
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elem = driver.find_element(by, val)
            driver.execute_script("arguments[0].scrollIntoView(true);", elem)
        await loop.run_in_executor(None, _action)
        return None
