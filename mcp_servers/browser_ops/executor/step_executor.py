import time
import asyncio
import base64
from selenium.webdriver.remote.webdriver import WebDriver
from ..commands.registry import CommandRegistry
from ..models.step import Step
from ..models.response import StepResult

class StepExecutor:
    def __init__(self):
        self.registry = CommandRegistry()

    async def execute_step(self, driver: WebDriver, step: Step) -> StepResult:
        start_time = time.time()
        try:
            cmd = self.registry.parse(step)
            val = await cmd.execute(driver)
            duration_ms = int((time.time() - start_time) * 1000)

            screenshot_val = str(val) if isinstance(val, str) and val else None

            return StepResult(
                step_id=step.id,
                status="success",
                duration_ms=duration_ms,
                error=None,
                screenshot=screenshot_val,
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            err_msg = str(e)
            
            # Try capturing screenshot on failure
            screenshot_b64 = None
            try:
                loop = asyncio.get_running_loop()
                png_bytes = await loop.run_in_executor(None, lambda: driver.get_screenshot_as_png())
                screenshot_b64 = base64.b64encode(png_bytes).decode("utf-8")
            except Exception:
                pass

            return StepResult(
                step_id=step.id,
                status="failed",
                duration_ms=duration_ms,
                error=err_msg,
                screenshot=screenshot_b64,
            )
