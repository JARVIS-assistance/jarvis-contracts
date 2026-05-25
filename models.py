from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from .action_registry import CONTRACT_VERSION, ClientActionType


class PlanStep(BaseModel):
    id: str = Field(..., description="Step identifier")
    action: str = Field(..., description="Planned action description")
    reasoning: str = Field(..., description="Why this step is needed")


class PlanRequest(BaseModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    session_id: str
    user_input: str
    task_type: Literal["general", "analysis", "execution"] = "general"


class ExecuteRequest(BaseModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    request_id: str
    action: str
    target: str
    value: Optional[str] = None


class ExecuteResult(BaseModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    request_id: str
    success: bool
    action: str
    detail: str
    output: dict[str, Any] = Field(default_factory=dict)


class VerifyRequest(BaseModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    request_id: str
    check: str
    expected: str
    actual: str


class VerifyResult(BaseModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    request_id: str
    passed: bool
    detail: str


class ErrorResponse(BaseModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    error_code: str
    message: str
    request_id: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)


# ── Client Action contracts ────────────────────────────────


class ClientAction(BaseModel):
    """클라이언트 PC에서 실행할 수 있는 액션 단위.

    클라이언트는 이 객체를 받아서 type에 따라 논리 작업(터미널, 파일, 앱)과
    물리 제어(마우스, 키보드, 화면 캡처)를 수행한다.
    """

    type: ClientActionType = Field(
        ..., description="Canonical action type the client should execute"
    )
    command: Optional[str] = Field(
        default=None,
        description="Shell command, app command, hotkey combo (e.g. 'ctrl,c'), or search query",
    )
    target: Optional[str] = Field(
        default=None,
        description="File path, app name, URL, or coordinate string",
    )
    payload: Optional[str] = Field(
        default=None,
        description="Content body — file content, clipboard text, keyboard text, etc.",
    )
    args: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Extra parameters. Common keys:\n"
            "  terminal: {cwd, env, timeout}\n"
            "  mouse_click: {x, y, button, clicks}\n"
            "  mouse_drag: {start_x, start_y, end_x, end_y}\n"
            "  keyboard_type: {enter: true/false}\n"
            "  hotkey: {keys: 'ctrl,a'}\n"
            "  screenshot: {region: [x,y,w,h] or null for full screen}\n"
            "  web_search: {max_results: 3}\n"
            "  calendar_control: {provider, calendar_id, title, start, end, timezone, location, notes}\n"
            "  browser_control/extract_dom: {purpose, query, include_links, include_elements, max_links}\n"
            "  browser_control/click_element: {ai_id}\n"
            "  browser_control/type_element: {ai_id, enter}"
        ),
    )
    description: str = Field(
        ..., description="Human-readable explanation of what this action does",
    )
    requires_confirm: bool = Field(
        default=True,
        description="If true, client must ask user confirmation before executing",
    )
    step_id: Optional[str] = Field(
        default=None,
        description="Related plan step id, if tied to a specific step",
    )


class ClientActionV2(BaseModel):
    """ActionContract v2 action using capability-style names.

    This is the compiler-facing contract. Controller validates this contract and
    adapts it to the existing v1 ClientAction queue only after validation.
    """

    name: str = Field(
        ...,
        description="Capability action name, e.g. browser.search or app.open",
    )
    target: Optional[str] = Field(
        default=None,
        description="Concrete app, URL, element target, or runtime target.",
    )
    payload: Optional[str] = Field(
        default=None,
        description="Primary text payload such as typed text or command output.",
    )
    args: dict[str, Any] = Field(default_factory=dict)
    description: str = Field(default="Client action")
    requires_confirm: bool = False
    step_id: Optional[str] = None


class ClientActionPlan(BaseModel):
    """Compiler output for a user turn."""

    contract_version: str = Field(default=CONTRACT_VERSION)
    mode: Literal["direct", "direct_sequence", "needs_plan", "no_action"] = "no_action"
    goal: str | None = None
    actions: list[ClientActionV2] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: str | None = None


class ClientActionValidationIssue(BaseModel):
    code: str
    message: str
    action_index: int | None = None
    action_name: str | None = None
    field: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


# ── Todo contracts ─────────────────────────────────────────


TodoStatus = Literal["open", "completed", "cancelled", "archived"]
CalendarSyncStatus = Literal["none", "linked", "pending", "synced", "failed"]


class TodoCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    priority: int = Field(default=3, ge=1, le=5)
    due_at: datetime | None = None
    remind_at: datetime | None = None
    timezone: str | None = Field(default=None, max_length=64)
    calendar_provider: str | None = Field(default=None, max_length=80)
    calendar_id: str | None = Field(default=None, max_length=200)
    calendar_event_id: str | None = Field(default=None, max_length=200)
    chat_id: str | None = None
    source_message_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TodoUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TodoStatus | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    due_at: datetime | None = None
    remind_at: datetime | None = None
    timezone: str | None = Field(default=None, max_length=64)
    calendar_provider: str | None = Field(default=None, max_length=80)
    calendar_id: str | None = Field(default=None, max_length=200)
    calendar_event_id: str | None = Field(default=None, max_length=200)
    calendar_sync_status: CalendarSyncStatus | None = None
    metadata: dict[str, Any] | None = None


class TodoResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str | None = None
    status: TodoStatus
    priority: int
    due_at: datetime | None = None
    remind_at: datetime | None = None
    timezone: str | None = None
    calendar_provider: str | None = None
    calendar_id: str | None = None
    calendar_event_id: str | None = None
    calendar_sync_status: CalendarSyncStatus
    chat_id: str | None = None
    source_message_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class TodoListResponse(BaseModel):
    items: list[TodoResponse] = Field(default_factory=list)


# ── DeepThink contracts ────────────────────────────────────


class DeepThinkStepPayload(BaseModel):
    id: str = Field(..., description="Plan step identifier (e.g. s1, s2)")
    title: str = Field(..., description="Short step title")
    description: str = Field(..., description="What this step should accomplish")


class DeepThinkPlanRequest(BaseModel):
    """controller → core: AI를 사용해 플랜 생성 요청."""

    contract_version: str = Field(default=CONTRACT_VERSION)
    request_id: str
    message: str = Field(..., min_length=1, description="Original user message")


class DeepThinkPlanResponse(BaseModel):
    """core → controller: AI가 생성한 플랜."""

    contract_version: str = Field(default=CONTRACT_VERSION)
    request_id: str
    goal: str
    steps: list[DeepThinkStepPayload] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class DeepThinkRequest(BaseModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    request_id: str
    message: str = Field(..., min_length=1, description="Original user message")
    plan_steps: list[DeepThinkStepPayload] = Field(
        default_factory=list,
        description="Planned steps — from AI planning or controller",
    )
    execution_context: list[str] = Field(
        default_factory=list,
        description="Prior server/client execution results to inject into the step context",
    )


class DeepThinkStepResult(BaseModel):
    step_id: str
    title: str
    status: Literal["completed", "failed", "skipped"]
    content: str
    actions: list[ClientAction] = Field(
        default_factory=list,
        description="Executable actions produced by this step",
    )


class DeepThinkResponse(BaseModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    request_id: str
    steps: list[DeepThinkStepResult] = Field(default_factory=list)
    summary: str = Field(..., description="Brief summary of the deep thinking result")
    content: str = Field(..., description="Full deep thinking response")
    actions: list[ClientAction] = Field(
        default_factory=list,
        description="Aggregated client actions from all steps, ready for execution",
    )


class ClientActionEnvelope(BaseModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    action_id: str
    request_id: str
    action: ClientAction


class ClientActionResultRequest(BaseModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    status: Literal["completed", "failed", "rejected", "timeout"]
    output: dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class ClientActionResult(BaseModel):
    contract_version: str = Field(default=CONTRACT_VERSION)
    action_id: str
    request_id: str
    status: Literal["queued", "completed", "failed", "rejected", "timeout"]
    output: dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
