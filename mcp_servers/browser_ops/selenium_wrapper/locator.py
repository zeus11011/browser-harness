from selenium.webdriver.common.by import By
from ..models.step import Locator
from ..errors import InvalidLocatorError

def to_by(loc: Locator) -> tuple[str, str]:
    """Convert a Locator model instance into a (By strategy, value) tuple for Selenium."""
    strategy = loc.by.lower().strip()
    match strategy:
        case "css":
            return (By.CSS_SELECTOR, loc.value)
        case "xpath":
            return (By.XPATH, loc.value)
        case "id":
            return (By.ID, loc.value)
        case "name":
            return (By.NAME, loc.value)
        case "class_name" | "class":
            return (By.CLASS_NAME, loc.value)
        case "tag_name" | "tag":
            return (By.TAG_NAME, loc.value)
        case "link_text" | "link":
            return (By.LINK_TEXT, loc.value)
        case "partial_link_text":
            return (By.PARTIAL_LINK_TEXT, loc.value)
        case _:
            raise InvalidLocatorError(loc.by)
