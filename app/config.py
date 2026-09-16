from dataclasses import dataclass, field
import os
from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _provider_name() -> str:
    return os.getenv("LLM_PROVIDER", "ollama").strip().lower()


def _provider_base_url() -> str:
    provider = _provider_name()
    if provider == "ollama":
        return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1").rstrip("/")
    if provider == "openai":
        return os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    return os.getenv("LLM_BASE_URL", "").rstrip("/")


def _provider_api_key() -> str:
    provider = _provider_name()
    if provider == "ollama":
        # Ollama's local OpenAI-compatible endpoint ignores this placeholder.
        return os.getenv("OLLAMA_API_KEY", "ollama")
    if provider == "openai":
        return os.getenv("OPENAI_API_KEY", "")
    return os.getenv("LLM_API_KEY", "")


def _provider_model() -> str:
    provider = _provider_name()
    if provider == "ollama":
        return os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b-instruct")
    if provider == "openai":
        return os.getenv("OPENAI_MODEL", "")
    return os.getenv("LLM_MODEL", "")


def _provider_timeout_seconds() -> int:
    configured = os.getenv("LLM_TIMEOUT_SECONDS")
    if configured:
        return int(configured)
    return 60 if _provider_name() == "ollama" else 45


@dataclass(frozen=True)
class Settings:
    # Real inference is the normal application mode. Tests opt in to ``mock``
    # explicitly so the product can never look AI-powered while silently using
    # deterministic rules.
    llm_provider: str = field(default_factory=_provider_name)
    llm_base_url: str = field(default_factory=_provider_base_url)
    llm_api_key: str = field(default_factory=_provider_api_key)
    llm_model: str = field(default_factory=_provider_model)
    azure_openai_endpoint: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/"))
    azure_openai_api_key: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", ""))
    azure_openai_deployment: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_DEPLOYMENT", ""))
    azure_openai_api_version: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"))
    llm_temperature: float = field(default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.2")))
    llm_max_tokens: int = field(default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "900")))
    llm_timeout_seconds: int = field(default_factory=_provider_timeout_seconds)
    allow_mock_fallback: bool = field(default_factory=lambda: _as_bool(os.getenv("ALLOW_MOCK_FALLBACK", "false"), False))
    redact_before_cloud: bool = field(default_factory=lambda: _as_bool(os.getenv("REDACT_BEFORE_CLOUD", "true"), True))
    max_input_chars: int = field(default_factory=lambda: int(os.getenv("MAX_INPUT_CHARS", "3000")))
    retrieval_top_k: int = field(default_factory=lambda: int(os.getenv("RETRIEVAL_TOP_K", "3")))
    retrieval_min_score: float = field(default_factory=lambda: float(os.getenv("RETRIEVAL_MIN_SCORE", "0.08")))
    max_agent_steps: int = field(default_factory=lambda: int(os.getenv("MAX_AGENT_STEPS", "6")))
    require_human_approval: bool = field(default_factory=lambda: _as_bool(os.getenv("REQUIRE_HUMAN_APPROVAL", "true"), True))
    prompt_version: str = field(default_factory=lambda: os.getenv("PROMPT_VERSION", "v2-cross-department"))
