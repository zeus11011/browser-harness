import asyncio
from typing import Any
from selenium.webdriver.remote.webdriver import WebDriver

from .base import SeleniumCommand
from ..errors import AppError

class NavigateCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        url = self.step.value
        if not url:
            raise AppError("Navigate command requires a 'value' containing the target URL")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, driver.get, url)
        return None

class RefreshCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, driver.refresh)
        return None

class BackCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, driver.back)
        return None

class ForwardCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, driver.forward)
        return None
