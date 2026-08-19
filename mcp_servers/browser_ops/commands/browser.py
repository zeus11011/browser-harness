import asyncio
from typing import Any
from selenium.webdriver.remote.webdriver import WebDriver

from .base import SeleniumCommand
from ..selenium_wrapper.locator import to_by
from ..errors import MissingLocatorError, AppError

class SwitchFrameCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("switch_frame")
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elem = driver.find_element(by, val)
            driver.switch_to.frame(elem)
        await loop.run_in_executor(None, _action)
        return None

class SwitchWindowCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        target = self.step.value
        if not target:
            raise AppError("switch_window requires a 'value' target handle or title")
        loop = asyncio.get_running_loop()
        def _action():
            handles = driver.window_handles
            if target in handles:
                driver.switch_to.window(target)
                return
            for h in handles:
                driver.switch_to.window(h)
                if driver.title == target or target in driver.current_url:
                    return
            raise AppError(f"Window target '{target}' not found among open windows")
        await loop.run_in_executor(None, _action)
        return None

class AcceptAlertCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        loop = asyncio.get_running_loop()
        def _action():
            alert = driver.switch_to.alert
            alert.accept()
        await loop.run_in_executor(None, _action)
        return None

class DismissAlertCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        loop = asyncio.get_running_loop()
        def _action():
            alert = driver.switch_to.alert
            alert.dismiss()
        await loop.run_in_executor(None, _action)
        return None
