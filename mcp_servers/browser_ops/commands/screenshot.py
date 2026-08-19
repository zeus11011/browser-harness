import asyncio
import base64
from typing import Any
from selenium.webdriver.remote.webdriver import WebDriver

from .base import SeleniumCommand
from ..selenium_wrapper.locator import to_by
from ..errors import AppError

class ScreenshotCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        loop = asyncio.get_running_loop()
        if self.step.locator:
            by, val = to_by(self.step.locator)
            def _elem_shot():
                elem = driver.find_element(by, val)
                return elem.screenshot_as_png
            png_bytes = await loop.run_in_executor(None, _elem_shot)
        else:
            png_bytes = await loop.run_in_executor(None, lambda: driver.get_screenshot_as_png())

        file_path = None
        if self.step.params and "path" in self.step.params:
            file_path = str(self.step.params["path"])
        elif self.step.value:
            file_path = self.step.value

        if file_path:
            def _write():
                with open(file_path, "wb") as f:
                    f.write(png_bytes)
            await loop.run_in_executor(None, _write)
            return file_path

        b64 = base64.b64encode(png_bytes).decode("utf-8")
        return b64
