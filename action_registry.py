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

COMMANDS_BY_ACTION_TYPE: dict[str, tuple[str | None, ...]] = {
    "terminal": ("execute",),
    "app_control": ("open", "focus", "close"),
    "file_write": (None,),
    "file_read": (None,),
    "open_url": (None,),
    "browser_control": (
        "scroll",
        "back",
        "forward",
        "reload",
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
    "browser_control": (
        "scroll:{direction,amount}; extract_dom:{purpose,query,include_links,"
        "include_elements,max_links}; click_element:{ai_id}; "
        "type_element:{ai_id,enter}"
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


def normalize_action_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize legacy/model-created action shapes to the canonical contract."""
    data = dict(payload)
    args = data.get("args") if isinstance(data.get("args"), dict) else {}
    data["args"] = dict(args)

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

    return data


def _first_string(*sources: Mapping[str, Any], keys: tuple[str, ...]) -> str | None:
    for source in sources:
        for key in keys:
            value = source.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None
