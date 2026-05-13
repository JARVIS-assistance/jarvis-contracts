from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal, Mapping, TypeAlias

CONTRACT_VERSION = "1.0"

ClientActionType: TypeAlias = Literal[
    "terminal",
    "app_control",
    "file_write",
    "file_read",
    "open_url",
    "browser",
    "browser_control",
    "web_search",
    "calendar_control",
    "notify",
    "clipboard",
    "mouse_click",
    "mouse_drag",
    "keyboard_type",
    "hotkey",
    "screenshot",
]

ClientActionV2Name: TypeAlias = Literal[
    "browser.open",
    "browser.navigate",
    "browser.search",
    "browser.extract_dom",
    "browser.click",
    "browser.type",
    "browser.select_result",
    "open_url",
    "app.open",
    "app.focus",
    "app.close",
    "file.read",
    "file.write",
    "keyboard.type",
    "keyboard.hotkey",
    "mouse.click",
    "mouse.drag",
    "screen.screenshot",
    "clipboard.copy",
    "clipboard.paste",
    "terminal.run",
    "notification.show",
    "web_search",
    "calendar.open",
    "calendar.create",
    "calendar.update",
    "calendar.delete",
]

COMMANDS_BY_ACTION_TYPE: dict[str, tuple[str | None, ...]] = {
    "terminal": ("execute",),
    "app_control": ("open", "focus", "close"),
    "file_write": (None,),
    "file_read": (None,),
    "open_url": (None,),
    "browser": ("open", "navigate", "search"),
    "browser_control": (
        "scroll",
        "back",
        "forward",
        "reload",
        "new_tab",
        "new_window",
        "close_tab",
        "focus_address_bar",
        "search",
        "extract_dom",
        "click_element",
        "type_element",
        "select_result",
    ),
    "web_search": (None,),
    "calendar_control": (
        "open",
        "list_events",
        "create_event",
        "update_event",
        "delete_event",
    ),
    "notify": (None,),
    "clipboard": ("copy", "paste"),
    "mouse_click": (None,),
    "mouse_drag": (None,),
    "keyboard_type": (None,),
    "hotkey": (None,),
    "screenshot": (None,),
}

ACTION_TYPE_DESCRIPTIONS: dict[str, str] = {
    "terminal": "Run a shell command in the user's configured shell.",
    "app_control": "Open, focus, or close a local application.",
    "file_write": "Write or create a local file.",
    "file_read": "Read a local file.",
    "open_url": "Open a URL or file path with a browser or OS handler.",
    "browser": "Open, navigate, or search with the user's configured browser.",
    "browser_control": "Control the active browser tab or extract DOM candidates.",
    "web_search": "Server-side web search. Frontend must not convert this to a browser action.",
    "calendar_control": "Control the user's configured calendar app or provider.",
    "notify": "Show a local notification.",
    "clipboard": "Copy to or paste from the clipboard.",
    "mouse_click": "Click at screen coordinates.",
    "mouse_drag": "Drag between screen coordinates.",
    "keyboard_type": "Type text into the active focused window.",
    "hotkey": "Press a keyboard shortcut.",
    "screenshot": "Capture the screen for visual analysis.",
}

ACTION_TYPE_ARGS: dict[str, str] = {
    "terminal": "{cwd, env, timeout, elevated}",
    "app_control": "{bundle_id?, wait_for_focus?}",
    "file_write": "{encoding?, overwrite?}",
    "file_read": "{encoding?, max_bytes?}",
    "open_url": "{browser?, query?}",
    "browser": "{browser?, url?, query?, search_engine?}",
    "browser_control": (
        "scroll:{direction,amount}; search:{query,new_tab?}; "
        "new_tab:{url?}; new_window:{url?}; close_tab:{}; focus_address_bar:{}; "
        "extract_dom:{purpose,query,include_links,"
        "include_elements,max_links}; click_element:{ai_id}; "
        "type_element:{ai_id,enter}; select_result:{index}"
    ),
    "web_search": "{max_results}",
    "calendar_control": "{provider, calendar_id, title, start, end, timezone, location, notes}",
    "notify": "{level?}",
    "clipboard": "{}",
    "mouse_click": "{x, y, button, clicks}",
    "mouse_drag": "{start_x, start_y, end_x, end_y}",
    "keyboard_type": "{enter}",
    "hotkey": "{keys}",
    "screenshot": "{region}",
}

ACTION_TYPE_ALIASES: dict[str, str] = {
    "launch_app": "app_control",
    "open_app": "app_control",
    "run_app": "app_control",
    "type_text": "keyboard_type",
    "keyboard_input": "keyboard_type",
}

# Action types the small LLM may emit directly from user intent.
ACTION_INTENT_ACTION_TYPES: tuple[str, ...] = (
    "app_control",
    "open_url",
    "browser_control",
    "calendar_control",
    "terminal",
    "keyboard_type",
    "hotkey",
    "mouse_click",
    "mouse_drag",
    "screenshot",
    "clipboard",
    "notify",
)

ACTION_REGISTRY: dict[str, dict[str, Any]] = {
    action_type: {
        "type": action_type,
        "commands": list(commands),
        "description": ACTION_TYPE_DESCRIPTIONS[action_type],
        "args": ACTION_TYPE_ARGS.get(action_type, "{}"),
        "direct_intent": action_type in ACTION_INTENT_ACTION_TYPES,
    }
    for action_type, commands in COMMANDS_BY_ACTION_TYPE.items()
}

ACTION_V2_CAPABILITIES: dict[str, dict[str, Any]] = {
    "browser.open": {
        "name": "browser.open",
        "namespace": "browser",
        "description": "Open the user's configured browser, optionally at a URL.",
        "args": "{url?, browser?}",
        "requires_confirm": False,
        "v1": "browser/open or open_url",
    },
    "browser.navigate": {
        "name": "browser.navigate",
        "namespace": "browser",
        "description": "Navigate the active/default browser to a concrete URL.",
        "args": "{url, browser?}",
        "requires_confirm": False,
        "v1": "open_url",
    },
    "browser.search": {
        "name": "browser.search",
        "namespace": "browser",
        "description": "Open deterministic search results for a query.",
        "args": "{query, browser?, search_engine?}",
        "requires_confirm": False,
        "v1": "open_url",
    },
    "browser.extract_dom": {
        "name": "browser.extract_dom",
        "namespace": "browser",
        "description": "Extract clickable/input DOM candidates from the active tab.",
        "args": "{purpose?, query?, include_links?, include_elements?, max_links?}",
        "requires_confirm": False,
        "v1": "browser_control/extract_dom",
    },
    "browser.click": {
        "name": "browser.click",
        "namespace": "browser",
        "description": "Click a known browser DOM element by ai_id.",
        "args": "{ai_id}",
        "requires_confirm": False,
        "v1": "browser_control/click_element",
    },
    "browser.type": {
        "name": "browser.type",
        "namespace": "browser",
        "description": "Type text into a known browser DOM input by ai_id.",
        "args": "{ai_id, text, enter?}",
        "requires_confirm": False,
        "v1": "browser_control/type_element",
    },
    "browser.select_result": {
        "name": "browser.select_result",
        "namespace": "browser",
        "description": "Open the Nth result on the current browser search results page.",
        "args": "{index}",
        "requires_confirm": False,
        "v1": "browser_control/select_result",
    },
    "open_url": {
        "name": "open_url",
        "namespace": "browser",
        "description": "Open a concrete URL with the user's browser or OS handler.",
        "args": "{url, browser?}",
        "requires_confirm": False,
        "v1": "open_url",
    },
    "app.open": {
        "name": "app.open",
        "namespace": "app",
        "description": "Open a concrete local application.",
        "args": "{bundle_id?, executable?, wait_for_focus?}",
        "requires_confirm": False,
        "v1": "app_control/open",
    },
    "app.focus": {
        "name": "app.focus",
        "namespace": "app",
        "description": "Focus a concrete local application.",
        "args": "{bundle_id?, executable?}",
        "requires_confirm": False,
        "v1": "app_control/focus",
    },
    "app.close": {
        "name": "app.close",
        "namespace": "app",
        "description": "Close a concrete local application.",
        "args": "{bundle_id?, executable?}",
        "requires_confirm": False,
        "v1": "app_control/close",
    },
    "file.read": {
        "name": "file.read",
        "namespace": "file",
        "description": "Read a local file from an allowed path.",
        "args": "{path, encoding?, max_bytes?}",
        "requires_confirm": False,
        "v1": "file_read",
    },
    "file.write": {
        "name": "file.write",
        "namespace": "file",
        "description": "Write text to a local file under an allowed path.",
        "args": "{path, text, encoding?, overwrite?}",
        "requires_confirm": True,
        "v1": "file_write",
    },
    "keyboard.type": {
        "name": "keyboard.type",
        "namespace": "keyboard",
        "description": "Type text into the currently focused UI.",
        "args": "{text, enter?}",
        "requires_confirm": False,
        "v1": "keyboard_type",
    },
    "keyboard.hotkey": {
        "name": "keyboard.hotkey",
        "namespace": "keyboard",
        "description": "Press a keyboard shortcut.",
        "args": "{keys}",
        "requires_confirm": False,
        "v1": "hotkey",
    },
    "mouse.click": {
        "name": "mouse.click",
        "namespace": "mouse",
        "description": "Click screen coordinates.",
        "args": "{x, y, button?, clicks?}",
        "requires_confirm": True,
        "v1": "mouse_click",
    },
    "mouse.drag": {
        "name": "mouse.drag",
        "namespace": "mouse",
        "description": "Drag between screen coordinates.",
        "args": "{start_x, start_y, end_x, end_y}",
        "requires_confirm": True,
        "v1": "mouse_drag",
    },
    "screen.screenshot": {
        "name": "screen.screenshot",
        "namespace": "screen",
        "description": "Capture the screen or a region.",
        "args": "{region?}",
        "requires_confirm": False,
        "v1": "screenshot",
    },
    "clipboard.copy": {
        "name": "clipboard.copy",
        "namespace": "clipboard",
        "description": "Copy text to clipboard.",
        "args": "{text}",
        "requires_confirm": False,
        "v1": "clipboard/copy",
    },
    "clipboard.paste": {
        "name": "clipboard.paste",
        "namespace": "clipboard",
        "description": "Paste from clipboard.",
        "args": "{}",
        "requires_confirm": True,
        "v1": "clipboard/paste",
    },
    "terminal.run": {
        "name": "terminal.run",
        "namespace": "terminal",
        "description": "Run a shell command in the user's configured shell.",
        "args": "{command, cwd?, env?, timeout?}",
        "requires_confirm": True,
        "v1": "terminal/execute",
    },
    "notification.show": {
        "name": "notification.show",
        "namespace": "notification",
        "description": "Show a local notification.",
        "args": "{text, level?}",
        "requires_confirm": False,
        "v1": "notify",
    },
    "web_search": {
        "name": "web_search",
        "namespace": "web_search",
        "description": "Run server-side web search without controlling the browser.",
        "args": "{query, max_results?}",
        "requires_confirm": False,
        "v1": "web_search",
    },
    "calendar.open": {
        "name": "calendar.open",
        "namespace": "calendar",
        "description": "Open the user's configured calendar.",
        "args": "{provider?}",
        "requires_confirm": False,
        "v1": "calendar_control/open",
    },
    "calendar.create": {
        "name": "calendar.create",
        "namespace": "calendar",
        "description": "Create a calendar event.",
        "args": "{provider?, calendar_id?, title, start, end, timezone?, location?, notes?}",
        "requires_confirm": True,
        "v1": "calendar_control/create_event",
    },
    "calendar.update": {
        "name": "calendar.update",
        "namespace": "calendar",
        "description": "Update a calendar event.",
        "args": "{provider?, calendar_id?, event_id, title?, start?, end?, timezone?, location?, notes?}",
        "requires_confirm": True,
        "v1": "calendar_control/update_event",
    },
    "calendar.delete": {
        "name": "calendar.delete",
        "namespace": "calendar",
        "description": "Delete a calendar event.",
        "args": "{provider?, calendar_id?, event_id}",
        "requires_confirm": True,
        "v1": "calendar_control/delete_event",
    },
}


def action_registry_payload() -> dict[str, Any]:
    """Return the canonical registry for frontend/runtime consumption."""
    return {
        "contract_version": CONTRACT_VERSION,
        "types": [deepcopy(ACTION_REGISTRY[key]) for key in COMMANDS_BY_ACTION_TYPE],
        "aliases": deepcopy(ACTION_TYPE_ALIASES),
        "rules": {
            "authoritative_source": [
                "/client/actions/pending",
                "SSE conversation.action_dispatch with backend action_id",
            ],
            "never_execute": [
                "assistant text action blocks",
                "frontend-generated embedded action ids",
                "unknown action types",
            ],
        },
        "v2": {
            "capabilities": [
                deepcopy(ACTION_V2_CAPABILITIES[key])
                for key in ACTION_V2_CAPABILITIES
            ],
            "plan_modes": ["direct", "direct_sequence", "needs_plan", "no_action"],
        },
    }


def format_action_registry_for_prompt(
    *, direct_only: bool = False, include_alias_warning: bool = True
) -> str:
    """Compact canonical action registry text for system prompts."""
    action_types = ACTION_INTENT_ACTION_TYPES if direct_only else tuple(COMMANDS_BY_ACTION_TYPE)
    lines: list[str] = []
    for action_type in action_types:
        commands = COMMANDS_BY_ACTION_TYPE[action_type]
        rendered_commands = " | ".join("null" if command is None else command for command in commands)
        lines.append(
            f"- {action_type}: commands={rendered_commands}; args={ACTION_TYPE_ARGS.get(action_type, '{}')}"
        )
    if include_alias_warning:
        lines.append(
            "- Do not invent action types. For app launch use "
            "type=app_control command=open target=<app name>. Never use launch_app."
        )
    return "\n".join(lines)


def action_v2_registry_payload() -> dict[str, Any]:
    """Return the v2 capability registry for compiler prompts and clients."""
    return {
        "contract_version": CONTRACT_VERSION,
        "capabilities": [
            deepcopy(ACTION_V2_CAPABILITIES[key])
            for key in ACTION_V2_CAPABILITIES
        ],
        "plan_modes": ["direct", "direct_sequence", "needs_plan", "no_action"],
    }


def format_action_v2_registry_for_prompt() -> str:
    lines: list[str] = []
    for name, spec in ACTION_V2_CAPABILITIES.items():
        lines.append(
            f"- {name}: args={spec.get('args', '{}')}; "
            f"requires_confirm={str(spec.get('requires_confirm', False)).lower()}; "
            f"{spec.get('description', '')}"
        )
    return "\n".join(lines)


def normalize_action_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize legacy/model-created action shapes to the canonical contract."""
    data = dict(payload)
    args = data.get("args") if isinstance(data.get("args"), dict) else {}
    data["args"] = dict(args)
    _move_top_level_args(
        data,
        keys=(
            "query",
            "search_query",
            "browser",
            "provider",
            "calendar_id",
            "timeout",
            "x",
            "y",
            "x_coordinate",
            "y_coordinate",
            "button",
            "clicks",
            "start_x",
            "start_y",
            "end_x",
            "end_y",
            "keys",
            "region",
        ),
    )

    raw_type = data.get("type")
    if isinstance(raw_type, str) and raw_type in ACTION_TYPE_ALIASES:
        data["type"] = ACTION_TYPE_ALIASES[raw_type]

    action_type = data.get("type")
    command = data.get("command")

    if action_type == "app_control":
        app_name = _first_string(
            data,
            data["args"],
            keys=("target", "app_name", "app", "name", "application"),
        )
        if isinstance(command, str) and command not in COMMANDS_BY_ACTION_TYPE["app_control"]:
            app_name = app_name or command
            command = "open"
        data["command"] = command if command in COMMANDS_BY_ACTION_TYPE["app_control"] else "open"
        if app_name and not isinstance(data.get("target"), str):
            data["target"] = app_name
        for key in ("app_name", "app", "name", "application"):
            data["args"].pop(key, None)
            data.pop(key, None)

    if action_type == "keyboard_type":
        text = _first_string(data, data["args"], keys=("payload", "text", "value"))
        data["command"] = None
        if text and not isinstance(data.get("payload"), str):
            data["payload"] = text
        for key in ("text", "value"):
            data["args"].pop(key, None)
            data.pop(key, None)

    if action_type == "open_url":
        data["command"] = None
        url = _first_string(data, data["args"], keys=("target", "url", "href"))
        if url and not isinstance(data.get("target"), str):
            data["target"] = url
        for key in ("url", "href"):
            data["args"].pop(key, None)
            data.pop(key, None)

    if action_type == "hotkey":
        data["command"] = None
        keys = _first_string(data, data["args"], keys=("keys", "hotkey", "shortcut"))
        if keys:
            data["args"]["keys"] = keys

    if action_type == "screenshot":
        data["command"] = None

    if action_type == "mouse_click":
        data["command"] = None
        _copy_number_arg(data["args"], "x", aliases=("x_coordinate",))
        _copy_number_arg(data["args"], "y", aliases=("y_coordinate",))

    if action_type == "mouse_drag":
        data["command"] = None

    return data


def _move_top_level_args(data: dict[str, Any], *, keys: tuple[str, ...]) -> None:
    args = data["args"]
    for key in keys:
        value = data.pop(key, None)
        if value is not None and key not in args:
            args["query" if key == "search_query" else key] = value


def _first_string(*sources: Mapping[str, Any], keys: tuple[str, ...]) -> str | None:
    for source in sources:
        for key in keys:
            value = source.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _copy_number_arg(args: dict[str, Any], canonical: str, *, aliases: tuple[str, ...]) -> None:
    if canonical in args:
        return
    for alias in aliases:
        value = args.get(alias)
        if isinstance(value, int | float):
            args[canonical] = value
            return
