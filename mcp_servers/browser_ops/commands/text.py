import asyncio
from typing import Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys

from .base import SeleniumCommand
from ..selenium_wrapper.locator import to_by
from ..errors import MissingLocatorError, AppError

class TypeTextCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("type_text")
        text = self.step.value or ""
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elem = driver.find_element(by, val)
            elem.send_keys(text)
        await loop.run_in_executor(None, _action)
        return None

class ClearCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("clear")
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elem = driver.find_element(by, val)
            elem.clear()
        await loop.run_in_executor(None, _action)
        return None

class SubmitCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("submit")
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elem = driver.find_element(by, val)
            elem.submit()
        await loop.run_in_executor(None, _action)
        return None

class PressKeyCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("press_key")
        key_name = (self.step.value or "").upper().strip()
        key_attr = getattr(Keys, key_name, key_name)
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elem = driver.find_element(by, val)
            elem.send_keys(key_attr)
        await loop.run_in_executor(None, _action)
        return None

class UploadFileCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("upload_file")
        file_path = self.step.value or ""
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elem = driver.find_element(by, val)
            elem.send_keys(file_path)
        await loop.run_in_executor(None, _action)
        return None
