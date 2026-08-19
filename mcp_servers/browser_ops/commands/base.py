from abc import ABC, abstractmethod
from typing import Any
from selenium.webdriver.remote.webdriver import WebDriver
from ..models.step import Step
from ..errors import AppError

class SeleniumCommand(ABC):
    def __init__(self, step: Step):
        self.step = step

    @abstractmethod
    async def execute(self, driver: WebDriver) -> Any:
        """Execute the command against the Selenium WebDriver instance."""
        pass
