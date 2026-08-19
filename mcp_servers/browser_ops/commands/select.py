import asyncio
from typing import Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import Select as SeleniumSelect

from .base import SeleniumCommand
from ..selenium_wrapper.locator import to_by
from ..errors import MissingLocatorError, AppError

class SelectByTextCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("select_by_text")
        text = self.step.value or ""
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elem = driver.find_element(by, val)
            sel = SeleniumSelect(elem)
            sel.select_by_visible_text(text)
        await loop.run_in_executor(None, _action)
        return None

class SelectByValueCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("select_by_value")
        val_str = self.step.value or ""
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elem = driver.find_element(by, val)
            sel = SeleniumSelect(elem)
            sel.select_by_value(val_str)
        await loop.run_in_executor(None, _action)
        return None

class SelectByIndexCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("select_by_index")
        try:
            idx = int(self.step.value or "0")
        except ValueError:
            raise AppError(f"Invalid index value: {self.step.value}")
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elem = driver.find_element(by, val)
            sel = SeleniumSelect(elem)
            sel.select_by_index(idx)
        await loop.run_in_executor(None, _action)
        return None

class DeselectCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("deselect")
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elem = driver.find_element(by, val)
            sel = SeleniumSelect(elem)
            sel.deselect_all()
        await loop.run_in_executor(None, _action)
        return None
