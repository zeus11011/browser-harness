class AppError(Exception):
    """Base application exception for browser_ops."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def to_string_clean(self) -> str:
        return self.message

class MissingLocatorError(AppError):
    def __init__(self, step_type: str):
        super().__init__(f"Step '{step_type}' requires a locator")

class InvalidLocatorError(AppError):
    def __init__(self, by: str, details: str = ""):
        msg = f"Invalid locator strategy '{by}'"
        if details:
            msg += f": {details}"
        super().__init__(msg)

class ElementNotFoundError(AppError):
    def __init__(self, locator_str: str):
        super().__init__(f"Element not found: {locator_str}")

class CommandExecutionError(AppError):
    def __init__(self, step_type: str, reason: str):
        super().__init__(f"Command '{step_type}' failed: {reason}")
