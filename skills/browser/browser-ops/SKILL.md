---
name: browser-ops
description: >-
  Perform browser automation via the browser_ops Python MCP server with Selenium WebDriver. Use when the user asks to navigate websites, click elements, type text, take screenshots, execute JavaScript, verify web pages, or manage browser sessions.
---

# browser_ops Skill

## Overview

`browser_ops` is a Python-based Selenium automation server that exposes full browser automation capabilities to AI agents via the Model Context Protocol (MCP). It controls Chrome via Selenium WebDriver and FastMCP, enabling agents to execute single actions, run complex browser flows, record step history, and save reusable tests.

---

## Prerequisites & Setup

| Component             | Requirement                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------------- |
| **Python**            | Python 3.10+                                                                                |
| **Selenium & Chrome** | Google Chrome installed & matching `chromedriver`                                           |
| **Python Packages**   | Dependencies in `requirements.txt` (`selenium`, `webdriver-manager`, `fastmcp`, `pydantic`) |

## Locator Model

All element-targeting tools accept a `Locator` object with `by` and `value` fields:

```json
{
  "by": "<strategy>",
  "value": "<selector>"
}
```

### Supported Locator Strategies (`by`)

| Strategy            | Description            | Example `value`                                       |
| ------------------- | ---------------------- | ----------------------------------------------------- |
| `css`               | CSS Selector           | `#submit-btn`, `div.container > button`               |
| `xpath`             | XPath Expression       | `//input[@name='email']`, `//button[text()='Submit']` |
| `id`                | Element ID attribute   | `username`, `login-form`                              |
| `name`              | Element name attribute | `password`, `user_email`                              |
| `class_name`        | Class name             | `btn-primary`, `nav-item`                             |
| `tag_name`          | HTML tag               | `input`, `button`, `h1`                               |
| `link_text`         | Exact hyperlink text   | `Sign In`                                             |
| `partial_link_text` | Partial hyperlink text | `Sign`                                                |

---

## Available MCP Tools

### 1. Navigation & Page Controls

- **`navigate(url)`**: Navigate active browser session to destination URL.
- **`refresh()`**: Refresh current page.
- **`back()`**: Navigate backward in history.
- **`forward()`**: Navigate forward in history.

### 2. Mouse & Click Actions

- **`click(locator)`**: Click element matching locator.
- **`click_from_image(x, y)`**: Click element at `(x, y)` viewport coordinates and return its XPath.
- **`double_click(locator)`**: Double-click element.
- **`right_click(locator)`**: Right-click (context click) element.
- **`hover(locator)`**: Move mouse cursor over element.
- **`drag_and_drop(source, target)`**: Drag `source` locator element onto `target` locator element.

### 3. Text Input & Forms

- **`type_text(locator, value)`**: Type text into input/textarea element.
- **`clear(locator)`**: Clear input element content.
- **`submit(locator)`**: Submit form containing target element.
- **`press_key(locator, value)`**: Press special key (`ENTER`, `TAB`, `ESCAPE`, `BACKSPACE`, etc.).
- **`upload_file(locator, value)`**: Send local file path to file input element.

### 4. Select / Dropdown Actions

- **`select_by_text(locator, value)`**: Select option by visible text.
- **`select_by_value(locator, value)`**: Select option by option `value` attribute.
- **`select_by_index(locator, value)`**: Select option by index.
- **`deselect(locator)`**: Clear multi-select dropdown options.

### 5. Wait & Timing

- **`wait(locator, timeout_ms)`**: Wait until element is present in DOM (default timeout 10000ms).
- **`sleep(ms)`**: Pause execution for `ms` milliseconds.

### 6. JavaScript & Scrolling

- **`execute_javascript(script)`**: Execute arbitrary JS in browser context and return result.
- **`scroll(x, y)`**: Scroll page by X and Y pixel offsets (e.g. `x=0, y=500`).
- **`scroll_into_view(locator)`**: Scroll until target element is in viewport.

### 7. Frames, Windows & Alerts

- **`switch_frame(locator)`**: Switch context into iframe element.
- **`switch_window(value)`**: Switch active tab/window by window handle or title.
- **`accept_alert()`**: Accept JS alert/confirm dialog.
- **`dismiss_alert()`**: Dismiss JS alert/confirm dialog.

### 8. Screenshot

- **`screenshot(locator, path)`**: Take screenshot of full page (or specific element if `locator` provided). Saves to `path` if provided, otherwise returns base64 PNG string.

### 9. Verifications & Assertions

- **`verify_text(locator, value)`**: Assert element contains expected text.
- **`verify_attribute(locator, attribute, expected_value)`**: Assert element attribute value matches.
- **`verify_title(value)`**: Assert page title contains expected string.
- **`verify_url(value)`**: Assert current URL contains expected string.
- **`verify_exists(locator)`**: Assert element exists in DOM.
- **`verify_visible(locator)`**: Assert element is visible on page.
- **`verify_enabled(locator)`**: Assert element is enabled.
- **`verify_selected(locator)`**: Assert checkbox/radio/option is selected.
- **`verify_css(locator, property_name, expected_value)`**: Assert computed CSS property matches.
- **`verify_count(locator, expected_count)`**: Assert element count matches expected integer.

### 10. Session Management

- **`create_session(headless)`**: Launch a new Chrome browser session and set as active.
- **`delete_session(session_id)`**: Quit browser and remove session.
- **`switch_session(session_id)`**: Set target session as active.
- **`list_sessions()`**: List all running sessions.
- **`get_session_info(session_id)`**: Retrieve details and recorded step history for session.
- **`save_session(session_id, test_id, save_to_disk)`**: Save session recorded steps to disk as a JSON test file.

---

## Workflow Examples

### Example 1: Basic Web Search Flow

```json
// 1. Navigate
{ "name": "navigate", "arguments": { "url": "https://example.com" } }

// 2. Type Search Query
{ "name": "type_text", "arguments": { "locator": { "by": "name", "value": "q" }, "value": "Automation" } }

// 3. Press Enter
{ "name": "press_key", "arguments": { "locator": { "by": "name", "value": "q" }, "value": "ENTER" } }

// 4. Verify Results & Screenshot
{ "name": "wait", "arguments": { "locator": { "by": "css", "value": "#results" } } }
{ "name": "screenshot", "arguments": { "path": "results.png" } }
```

### Example 2: Form Verification

```json
{ "name": "navigate", "arguments": { "url": "https://app.example.com/login" } }
{ "name": "type_text", "arguments": { "locator": { "by": "id", "value": "email" }, "value": "user@example.com" } }
{ "name": "click", "arguments": { "locator": { "by": "css", "value": "button[type='submit']" } } }
{ "name": "verify_text", "arguments": { "locator": { "by": "class_name", "value": "welcome-msg" }, "value": "Welcome back" } }
```

---

## Best Practices for AI Agents

1. **Automatic Session Handling**: `browser_ops` automatically creates and manages active sessions on demand. You do not need to call `create_session` explicitly unless managing multiple concurrent browsers.
2. **Explicit Locators**: Prefer resilient locator strategies (`id`, `css`, `xpath`) over fragile text matches.
3. **Wait Before Acting**: Use `wait(locator)` before clicking or reading elements on dynamic SPA/AJAX pages.
4. **Saving Reusable Flows**: When completing a multi-step user flow, use `save_session()` to persist the step sequence as a JSON test file in `tests/` for future replay.
