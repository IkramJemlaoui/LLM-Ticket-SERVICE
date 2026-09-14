from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

@dataclass(frozen=True)
class Settings:
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "").rstrip("/")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "500"))
    redact_before_cloud: bool = _as_bool(os.getenv("REDACT_BEFORE_CLOUD", "true"), True)
    max_input_chars: int = int(os.getenv("MAX_INPUT_CHARS", "3000"))
    retrieval_top_k: int = int(os.getenv("RETRIEVAL_TOP_K", "3"))
    prompt_version: str = os.getenv("PROMPT_VERSION", "v1")
