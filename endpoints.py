from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EndpointSpec:
    service: str
    name: str
    method: str
    path: str
    internal: bool = False

    def url(self, base_url: str) -> str:
        return f"{base_url.rstrip('/')}{self.path}"


class JarvisCoreEndpoints:
    HEALTH = EndpointSpec(
        service="jarvis-core",
        name="health",
        method="GET",
        path="/health",
    )
    INTERNAL_CONVERSATION_RESPOND = EndpointSpec(
        service="jarvis-core",
        name="internal_conversation_respond",
        method="POST",
        path="/internal/conversation/respond",
        internal=True,
    )

    INTERNAL_CHAT_REQUEST = EndpointSpec(
        service="jarvis-core",
        name="internal_chat_request",
        method="POST",
        path="/internal/chat/request",
        internal=True,
    )
    INTERNAL_CHAT_STREAM = EndpointSpec(
        service="jarvis-core",
        name="internal_chat_stream",
        method="POST",
        path="/internal/chat/stream",
        internal=True,
    )
    INTERNAL_CHAT_MODEL_CONFIG = EndpointSpec(
        service="jarvis-core",
        name="internal_chat_model_config",
        method="POST",
        path="/internal/chat/model-config",
        internal=True,
    )
    INTERNAL_CHAT_MODEL_CONFIG_LIST = EndpointSpec(
        service="jarvis-core",
        name="internal_chat_model_config_list",
        method="GET",
        path="/internal/chat/model-config",
        internal=True,
    )
    INTERNAL_CHAT_MODEL_CONFIG_UPDATE = EndpointSpec(
        service="jarvis-core",
        name="internal_chat_model_config_update",
        method="PUT",
        path="/internal/chat/model-config/{model_config_id}",
        internal=True,
    )
    INTERNAL_CHAT_MODEL_CONFIG_DELETE = EndpointSpec(
        service="jarvis-core",
        name="internal_chat_model_config_delete",
        method="DELETE",
        path="/internal/chat/model-config/{model_config_id}",
        internal=True,
    )
    INTERNAL_CHAT_MODEL_SELECTION = EndpointSpec(
        service="jarvis-core",
        name="internal_chat_model_selection",
        method="POST",
        path="/internal/chat/model-selection",
        internal=True,
    )
    INTERNAL_CHAT_MODEL_SELECTION_GET = EndpointSpec(
        service="jarvis-core",
        name="internal_chat_model_selection_get",
        method="GET",
        path="/internal/chat/model-selection",
        internal=True,
    )
    INTERNAL_CHAT_PERSONA = EndpointSpec(
        service="jarvis-core",
        name="internal_chat_persona",
        method="POST",
        path="/internal/chat/persona",
        internal=True,
    )
    INTERNAL_CHAT_PERSONA_LIST = EndpointSpec(
        service="jarvis-core",
        name="internal_chat_persona_list",
        method="GET",
        path="/internal/chat/persona",
        internal=True,
    )
    INTERNAL_CHAT_PERSONA_UPDATE = EndpointSpec(
        service="jarvis-core",
        name="internal_chat_persona_update",
        method="PUT",
        path="/internal/chat/persona/{user_persona_id}",
        internal=True,
    )
    INTERNAL_CHAT_PERSONA_SELECT = EndpointSpec(
        service="jarvis-core",
        name="internal_chat_persona_select",
        method="POST",
        path="/internal/chat/persona/select",
        internal=True,
    )
    INTERNAL_CHAT_MEMORY = EndpointSpec(
        service="jarvis-core",
        name="internal_chat_memory",
        method="POST",
        path="/internal/chat/memory",
        internal=True,
    )
    INTERNAL_CHAT_MEMORY_LIST = EndpointSpec(
        service="jarvis-core",
        name="internal_chat_memory_list",
        method="GET",
        path="/internal/chat/memory",
        internal=True,
    )
    INTERNAL_AUDIO_SPEECH = EndpointSpec(
        service="jarvis-core",
        name="internal_audio_speech",
        method="POST",
        path="/internal/audio/speech",
        internal=True,
    )
    INTERNAL_AUDIO_SPEECH_PCM = EndpointSpec(
        service="jarvis-core",
        name="internal_audio_speech_pcm",
        method="POST",
        path="/internal/audio/speech/pcm",
        internal=True,
    )
    INTERNAL_AUDIO_SPEECH_MODELS = EndpointSpec(
        service="jarvis-core",
        name="internal_audio_speech_models",
        method="GET",
        path="/internal/audio/speech/models",
        internal=True,
    )
    INTERNAL_CLIENT_RUNTIME_PROFILE = EndpointSpec(
        service="jarvis-core",
        name="internal_client_runtime_profile",
        method="PUT",
        path="/internal/client/runtime-profile",
        internal=True,
    )
    INTERNAL_CLIENT_RUNTIME_PROFILE_GET = EndpointSpec(
        service="jarvis-core",
        name="internal_client_runtime_profile_get",
        method="GET",
        path="/internal/client/runtime-profile",
        internal=True,
    )
    INTERNAL_TODOS = EndpointSpec(
        service="jarvis-core",
        name="internal_todos",
        method="POST",
        path="/internal/todos",
        internal=True,
    )
    INTERNAL_TODOS_LIST = EndpointSpec(
        service="jarvis-core",
        name="internal_todos_list",
        method="GET",
        path="/internal/todos",
        internal=True,
    )
    INTERNAL_TODO_DETAIL = EndpointSpec(
        service="jarvis-core",
        name="internal_todo_detail",
        method="GET",
        path="/internal/todos/{todo_id}",
        internal=True,
    )
    INTERNAL_TODO_UPDATE = EndpointSpec(
        service="jarvis-core",
        name="internal_todo_update",
        method="PATCH",
        path="/internal/todos/{todo_id}",
        internal=True,
    )
    INTERNAL_TODO_DELETE = EndpointSpec(
        service="jarvis-core",
        name="internal_todo_delete",
        method="DELETE",
        path="/internal/todos/{todo_id}",
        internal=True,
    )
    INTERNAL_DEEPTHINK_PLAN = EndpointSpec(
        service="jarvis-core",
        name="internal_deepthink_plan",
        method="POST",
        path="/internal/deepthink/plan",
        internal=True,
    )
    INTERNAL_DEEPTHINK_EXECUTE = EndpointSpec(
        service="jarvis-core",
        name="internal_deepthink_execute",
        method="POST",
        path="/internal/deepthink/execute",
        internal=True,
    )

    @classmethod
    def all(cls) -> tuple[EndpointSpec, ...]:
        return (
            cls.HEALTH,
            cls.INTERNAL_CONVERSATION_RESPOND,
            cls.INTERNAL_CHAT_REQUEST,
            cls.INTERNAL_CHAT_STREAM,
            cls.INTERNAL_CHAT_MODEL_CONFIG,
            cls.INTERNAL_CHAT_MODEL_CONFIG_LIST,
            cls.INTERNAL_CHAT_MODEL_CONFIG_UPDATE,
            cls.INTERNAL_CHAT_MODEL_CONFIG_DELETE,
            cls.INTERNAL_CHAT_MODEL_SELECTION,
            cls.INTERNAL_CHAT_MODEL_SELECTION_GET,
            cls.INTERNAL_CHAT_PERSONA,
            cls.INTERNAL_CHAT_PERSONA_LIST,
            cls.INTERNAL_CHAT_PERSONA_UPDATE,
            cls.INTERNAL_CHAT_PERSONA_SELECT,
            cls.INTERNAL_CHAT_MEMORY,
            cls.INTERNAL_CHAT_MEMORY_LIST,
            cls.INTERNAL_AUDIO_SPEECH,
            cls.INTERNAL_AUDIO_SPEECH_PCM,
            cls.INTERNAL_CLIENT_RUNTIME_PROFILE,
            cls.INTERNAL_CLIENT_RUNTIME_PROFILE_GET,
            cls.INTERNAL_TODOS,
            cls.INTERNAL_TODOS_LIST,
            cls.INTERNAL_TODO_DETAIL,
            cls.INTERNAL_TODO_UPDATE,
            cls.INTERNAL_TODO_DELETE,
            cls.INTERNAL_DEEPTHINK_PLAN,
            cls.INTERNAL_DEEPTHINK_EXECUTE,
        )

    @classmethod
    def for_controller(cls) -> tuple[EndpointSpec, ...]:
        return tuple(endpoint for endpoint in cls.all() if endpoint.internal)


class JarvisGatewayEndpoints:
    HEALTH = EndpointSpec(
        service="jarvis-gateway",
        name="health",
        method="GET",
        path="/health",
    )
    LOGIN = EndpointSpec(
        service="jarvis-gateway",
        name="login",
        method="POST",
        path="/auth/login",
    )
    LOGOUT = EndpointSpec(
        service="jarvis-gateway",
        name="logout",
        method="POST",
        path="/auth/logout",
    )
    VALIDATE = EndpointSpec(
        service="jarvis-gateway",
        name="validate",
        method="GET",
        path="/auth/validate",
    )

    @classmethod
    def all(cls) -> tuple[EndpointSpec, ...]:
        return (
            cls.HEALTH,
            cls.LOGIN,
            cls.LOGOUT,
            cls.VALIDATE,
        )
