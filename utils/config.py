import os
from dataclasses import dataclass
from typing import Any, Optional

from dotenv import find_dotenv, load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel

load_dotenv(find_dotenv(usecwd=True))

# provider -> (startswith prefixes, contains keywords, api-key env vars in priority order)
_PROVIDERS: dict[str, tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]] = {
    "google_genai": (("gemini",), ("google",), ("GEMINI_API_KEY", "GOOGLE_API_KEY")),
    "anthropic": (("claude",), ("anthropic",), ("ANTHROPIC_API_KEY",)),
    "openai": (("gpt", "o1", "o3"), ("openai",), ("OPENAI_API_KEY",)),
    "groq": ((), ("groq",), ("GROQ_API_KEY",)),
}


@dataclass
class LLMConfig:
    """LLM configuration resolved from explicit args and/or environment variables."""

    provider: str
    model_name: str
    api_key: Optional[str] = None
    temperature: Optional[float] = None


def _infer_provider(
    model_name: str, explicit_provider: Optional[str] = None
) -> tuple[str, str]:
    """Infer (provider, clean_model_name) from a 'provider:model' string or name prefix."""
    if explicit_provider:
        provider = explicit_provider.lower().strip()
        model = (
            model_name.split(":", 1)[1]
            if model_name.startswith(f"{provider}:")
            else model_name
        )
        return provider, model

    if ":" in model_name:
        provider, model = model_name.split(":", 1)
        return provider.lower().strip(), model

    lower = model_name.lower().strip()
    for provider, (starts, contains, _) in _PROVIDERS.items():
        if any(lower.startswith(p) for p in starts) or any(
            k in lower for k in contains
        ):
            return provider, model_name

    return "google_genai", model_name  # default fallback


def _get_api_key_for_provider(
    provider: str, explicit_api_key: Optional[str] = None
) -> Optional[str]:
    if explicit_api_key:
        return explicit_api_key
    for env_var in _PROVIDERS.get(provider, ((), (), ()))[2]:
        if key := os.getenv(env_var):
            return key
    return os.getenv("LLM_API_KEY")


def load_llm_config(
    model_name: Optional[str] = None,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: Optional[float] = None,
) -> LLMConfig:
    """Resolve LLM config from explicit args, falling back to LLM_MODEL/LLM_NAME/MODEL_NAME,
    LLM_PROVIDER, provider-specific API key env vars (or LLM_API_KEY), and LLM_TEMPERATURE.
    """
    raw_model = (
        model_name
        or os.getenv("LLM_MODEL")
        or os.getenv("LLM_NAME")
        or os.getenv("MODEL_NAME")
        or "gemini-2.5-flash"
    )
    resolved_provider, clean_model = _infer_provider(
        raw_model, provider or os.getenv("LLM_PROVIDER")
    )
    resolved_api_key = _get_api_key_for_provider(resolved_provider, api_key)

    if temperature is None and (env_temp := os.getenv("LLM_TEMPERATURE")):
        try:
            temperature = float(env_temp)
        except ValueError:
            pass

    return LLMConfig(resolved_provider, clean_model, resolved_api_key, temperature)


_PROVIDER_LABELS: dict[str, str] = {
    "google_genai": "Gemini/Google",
    "anthropic": "Anthropic",
    "openai": "OpenAI",
    "groq": "Groq",
}


def get_llm(
    model_name: Optional[str] = None,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: Optional[float] = None,
    **kwargs: Any,
) -> BaseChatModel:
    """Instantiate a LangChain chat model configured for use with deepagents."""
    config = load_llm_config(model_name, provider, api_key, temperature)
    if config.temperature is not None:
        kwargs["temperature"] = config.temperature

    env_vars = _PROVIDERS.get(config.provider, ((), (), ()))[2]
    if not config.api_key and env_vars:
        label = _PROVIDER_LABELS.get(config.provider, config.provider)
        raise ValueError(
            f"{label} API key not found. Set {' or '.join(env_vars)}, or LLM_API_KEY."
        )

    from langchain.chat_models import init_chat_model

    init_args: dict[str, Any] = {
        "model": config.model_name,
        "model_provider": config.provider,
        **kwargs,
    }
    if config.api_key:
        init_args["api_key"] = config.api_key
    return init_chat_model(**init_args)
