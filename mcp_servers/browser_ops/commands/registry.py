from typing import Dict, Type
from .base import SeleniumCommand
from .click import ClickCommand, DoubleClickCommand, RightClickCommand, HoverCommand, DragAndDropCommand, ClickFromImageCommand
from .text import TypeTextCommand, ClearCommand, SubmitCommand, PressKeyCommand, UploadFileCommand
from .select import SelectByTextCommand, SelectByValueCommand, SelectByIndexCommand, DeselectCommand
from .navigation import NavigateCommand, RefreshCommand, BackCommand, ForwardCommand
from .wait import WaitCommand, SleepCommand
from .javascript import ExecuteJavascriptCommand, ScrollCommand, ScrollIntoViewCommand
from .browser import SwitchFrameCommand, SwitchWindowCommand, AcceptAlertCommand, DismissAlertCommand
from .screenshot import ScreenshotCommand
from .verify import (
    VerifyTextCommand, VerifyAttributeCommand, VerifyTitleCommand, VerifyUrlCommand,
    VerifyExistsCommand, VerifyVisibleCommand, VerifyEnabledCommand, VerifySelectedCommand,
    VerifyCssCommand, VerifyCountCommand
)
from ..models.step import Step
from ..errors import AppError

COMMAND_REGISTRY: Dict[str, Type[SeleniumCommand]] = {
    "click": ClickCommand,
    "double_click": DoubleClickCommand,
    "right_click": RightClickCommand,
    "hover": HoverCommand,
    "drag_and_drop": DragAndDropCommand,
    "click_from_image": ClickFromImageCommand,
    "type_text": TypeTextCommand,
    "clear": ClearCommand,
    "submit": SubmitCommand,
    "press_key": PressKeyCommand,
    "upload_file": UploadFileCommand,
    "select_by_text": SelectByTextCommand,
    "select_by_value": SelectByValueCommand,
    "select_by_index": SelectByIndexCommand,
    "deselect": DeselectCommand,
    "navigate": NavigateCommand,
    "refresh": RefreshCommand,
    "back": BackCommand,
    "forward": ForwardCommand,
    "wait": WaitCommand,
    "sleep": SleepCommand,
    "execute_javascript": ExecuteJavascriptCommand,
    "scroll": ScrollCommand,
    "scroll_into_view": ScrollIntoViewCommand,
    "switch_frame": SwitchFrameCommand,
    "switch_window": SwitchWindowCommand,
    "accept_alert": AcceptAlertCommand,
    "dismiss_alert": DismissAlertCommand,
    "screenshot": ScreenshotCommand,
    "verify_text": VerifyTextCommand,
    "verify_attribute": VerifyAttributeCommand,
    "verify_title": VerifyTitleCommand,
    "verify_url": VerifyUrlCommand,
    "verify_exists": VerifyExistsCommand,
    "verify_visible": VerifyVisibleCommand,
    "verify_enabled": VerifyEnabledCommand,
    "verify_selected": VerifySelectedCommand,
    "verify_css": VerifyCssCommand,
    "verify_count": VerifyCountCommand,
}

class CommandRegistry:
    def parse(self, step: Step) -> SeleniumCommand:
        step_type = step.step_type.lower().strip()
        cmd_cls = COMMAND_REGISTRY.get(step_type)
        if not cmd_cls:
            raise AppError(f"Unknown step type '{step.step_type}'")
        return cmd_cls(step)
