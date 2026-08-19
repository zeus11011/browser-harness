import asyncio
from typing import Any, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains

from .base import SeleniumCommand
from ..selenium_wrapper.locator import to_by
from ..errors import MissingLocatorError, AppError

class ClickCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("click")
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elem = driver.find_element(by, val)
            elem.click()
        await loop.run_in_executor(None, _action)
        return None

class DoubleClickCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("double_click")
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elem = driver.find_element(by, val)
            ActionChains(driver).double_click(elem).perform()
        await loop.run_in_executor(None, _action)
        return None

class RightClickCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("right_click")
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elem = driver.find_element(by, val)
            ActionChains(driver).context_click(elem).perform()
        await loop.run_in_executor(None, _action)
        return None

class HoverCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("hover")
        by, val = to_by(self.step.locator)
        loop = asyncio.get_running_loop()
        def _action():
            elem = driver.find_element(by, val)
            ActionChains(driver).move_to_element(elem).perform()
        await loop.run_in_executor(None, _action)
        return None

class DragAndDropCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        if not self.step.locator:
            raise MissingLocatorError("drag_and_drop")
        target_dict = (self.step.params or {}).get("target")
        if not target_dict:
            raise AppError("drag_and_drop requires a 'target' locator in params")
        from models.step import Locator
        target_loc = Locator(**target_dict)
        
        src_by, src_val = to_by(self.step.locator)
        tgt_by, tgt_val = to_by(target_loc)
        loop = asyncio.get_running_loop()
        def _action():
            src_elem = driver.find_element(src_by, src_val)
            tgt_elem = driver.find_element(tgt_by, tgt_val)
            ActionChains(driver).drag_and_drop(src_elem, tgt_elem).perform()
        await loop.run_in_executor(None, _action)
        return None

def click_from_image(driver: WebDriver, x: int, y: int, img_w: Optional[int] = None, img_h: Optional[int] = None) -> str:
    """Finds element at (x, y) image or viewport coordinates in browser, clicks it, and returns its XPath."""
    js_script = """
        const x_in = arguments[0];
        const y_in = arguments[1];
        const img_w = arguments[2];
        const img_h = arguments[3];

        let x = x_in;
        let y = y_in;

        if (img_w && img_h) {
            x = (x_in / img_w) * window.innerWidth;
            y = (y_in / img_h) * window.innerHeight;
        }

        const dpr = window.devicePixelRatio || 1;
        let elem = document.elementFromPoint(x, y);

        if (!elem && dpr !== 1) {
            elem = document.elementFromPoint(x / dpr, y / dpr);
        }

        if (!elem) {
            return null;
        }
        function getElementXPath(element) {
            if (element.id && element.id !== '') {
                return '//*[@id="' + element.id + '"]';
            }
            if (element === document.body) {
                return '/html/body';
            }
            let ix = 0;
            const siblings = element.parentNode ? element.parentNode.childNodes : [];
            for (let i = 0; i < siblings.length; i++) {
                const sibling = siblings[i];
                if (sibling === element) {
                    return getElementXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                }
                if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                    ix++;
                }
            }
            return null;
        }
        return [getElementXPath(elem), elem];
    """
    res = driver.execute_script(js_script, x, y, img_w, img_h)
    if not res:
        raise AppError(f"No element found at coordinates ({x}, {y})")
    xpath, elem = res[0], res[1]
    if elem:
        try:
            elem.click()
        except Exception:
            driver.execute_script("arguments[0].click();", elem)
    return xpath

class ClickFromImageCommand(SeleniumCommand):
    async def execute(self, driver: WebDriver) -> Any:
        x = None
        y = None
        img_w = None
        img_h = None
        if self.step.params:
            x = self.step.params.get("x")
            y = self.step.params.get("y")
            img_w = self.step.params.get("img_w") or self.step.params.get("img_width") or self.step.params.get("width")
            img_h = self.step.params.get("img_h") or self.step.params.get("img_height") or self.step.params.get("height")
        if (x is None or y is None) and self.step.value:
            parts = str(self.step.value).split(",")
            if len(parts) >= 2:
                x, y = parts[0].strip(), parts[1].strip()
            if len(parts) == 4:
                img_w, img_h = parts[2].strip(), parts[3].strip()

        if x is None or y is None:
            raise AppError("click_from_image requires 'x' and 'y' coordinates in params or value (e.g. 'x,y')")

        x_int = int(x)
        y_int = int(y)
        img_w_int = int(img_w) if img_w is not None else None
        img_h_int = int(img_h) if img_h is not None else None
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, click_from_image, driver, x_int, y_int, img_w_int, img_h_int)


