from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from .step_executor import StepExecutor
from ..models.test import Test
from ..models.response import ExecutionResponse, StepResult

class TestExecutor:
    __test__ = False
    def __init__(self, step_executor: Optional[StepExecutor] = None):
        self.step_executor = step_executor or StepExecutor()

    async def execute_test(
        self, driver: WebDriver, test: Test, session_id: Optional[str] = None
    ) -> ExecutionResponse:
        results = []
        overall_success = True

        for step in test.steps:
            res = await self.step_executor.execute_step(driver, step)
            results.append(res)
            if res.status != "success":
                overall_success = False
                if not test.continue_on_failure:
                    break

        return ExecutionResponse(
            success=overall_success,
            session_id=session_id,
            results=results,
        )
