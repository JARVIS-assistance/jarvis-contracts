from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


CONTRACT_VERSION = "1.0"


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

    type: Literal[
        # ── 논리 작업 ──
        "terminal",        # 터미널/쉘 명령 실행
        "app_control",     # 앱 실행/종료/포커스
        "file_write",      # 파일 쓰기/생성
        "file_read",       # 파일 읽기
        "open_url",        # URL/파일을 OS 기본 앱으로 열기
        "browser_control", # 사용자 브라우저/웹뷰 조작
        "web_search",      # 웹 검색 수행
        "notify",          # 사용자 알림
        "clipboard",       # 클립보드 복사
        # ── 물리 제어 ──
        "mouse_click",     # 지정 좌표 클릭
        "mouse_drag",      # 드래그 앤 드롭
        "keyboard_type",   # 텍스트 타이핑 (현재 활성 창)
        "hotkey",          # 단축키 입력 (예: ctrl+c, alt+tab)
        "screenshot",      # 스크린샷 촬영 요청 (화면 분석용)
    ] = Field(..., description="Action type the client should execute")
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
            "  web_search: {max_results: 3}"
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
