import asyncio
from typing import Any
from selenium.webdriver.remote.webdriver import WebDriver

from .base import SeleniumCommand
from ..selenium_wrapper.locator import to_by
from ..errors import MissingLocatorError, AppError

class VerifyTextCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("verify_text")
        expected = self.step.value or ""
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            actual = driver.find_element(by, val).text
            if expected not in actual:
                raise AppError(f"Expected text '{expected}' not found in actual text '{actual}'")
        await loop.run_in_executor(None, _action)
        return None

class VerifyAttributeCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("verify_attribute")
        expected = self.step.value or ""
        attr_name = (self.step.params or {}).get("attribute", "")
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            actual = driver.find_element(by, val).get_attribute(attr_name)
            if actual != expected:
                raise AppError(f"Attribute '{attr_name}' mismatch: expected '{expected}', got '{actual}'")
        await loop.run_in_executor(None, _action)
        return None

class VerifyTitleCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        expected = self.step.value or ""
        loop = asyncio.get_running_loop()
        def _action():
            actual = driver.title
            if expected not in actual:
                raise AppError(f"Page title mismatch: expected '{expected}', got '{actual}'")
        await loop.run_in_executor(None, _action)
        return None

class VerifyUrlCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        expected = self.step.value or ""
        loop = asyncio.get_running_loop()
        def _action():
            actual = driver.current_url
            if expected not in actual:
                raise AppError(f"URL mismatch: expected '{expected}', got '{actual}'")
        await loop.run_in_executor(None, _action)
        return None

class VerifyExistsCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("verify_exists")
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elems = driver.find_elements(by, val)
            if not elems:
                raise AppError(f"Element matching {val} does not exist in DOM")
        await loop.run_in_executor(None, _action)
        return None

class VerifyVisibleCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("verify_visible")
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elem = driver.find_element(by, val)
            if not elem.is_displayed():
                raise AppError(f"Element {val} exists but is not visible")
        await loop.run_in_executor(None, _action)
        return None

class VerifyEnabledCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("verify_enabled")
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elem = driver.find_element(by, val)
            if not elem.is_enabled():
                raise AppError(f"Element {val} is disabled")
        await loop.run_in_executor(None, _action)
        return None

class VerifySelectedCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("verify_selected")
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elem = driver.find_element(by, val)
            if not elem.is_selected():
                raise AppError(f"Element {val} is not selected")
        await loop.run_in_executor(None, _action)
        return None

class VerifyCssCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("verify_css")
        expected = self.step.value or ""
        prop_name = (self.step.params or {}).get("property", "")
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            actual = driver.find_element(by, val).value_of_css_property(prop_name)
            if actual != expected:
                raise AppError(f"CSS prop '{prop_name}' mismatch: expected '{expected}', got '{actual}'")
        await loop.run_in_executor(None, _action)
        return None

class VerifyCountCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("verify_count")
        expected_cnt = int(self.step.value or "0")
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            actual_cnt = len(driver.find_elements(by, val))
            if actual_cnt != expected_cnt:
                raise AppError(f"Element count mismatch for {val}: expected {expected_cnt}, got {actual_cnt}")
        await loop.run_in_executor(None, _action)
        return None
