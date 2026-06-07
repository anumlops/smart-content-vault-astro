import logging
import os

from .providers import (
    KIMI_MODEL,
    DEEPSEEK_MODEL,
    LLMError,
    RateLimitError,
    TimeoutError,
    InvalidResponseError,
    call_llm,
)
from .validator import ValidationError, validate_analysis_response

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self._deepseek_model = os.getenv("OPENROUTER_MODEL", DEEPSEEK_MODEL)
        self._kimi_model = KIMI_MODEL

    def analyze(self, content: str, title: str | None = None) -> dict:
        last_error = ""

        models_to_try = [
            (self._deepseek_model, "DeepSeek", 1),
            (self._kimi_model, "Kimi K2.6", 1),
        ]

        for model_name, model_label, retries in models_to_try:
            for attempt in range(1, retries + 1):
                try:
                    logger.info(
                        "LLM attempt %d/%d with %s", attempt, retries, model_label
                    )
                    raw = call_llm(content, title, model=model_name)
                    validated = validate_analysis_response(raw)
                    logger.info(
                        "Analysis successful with %s on attempt %d",
                        model_label,
                        attempt,
                    )
                    return validated
                except (TimeoutError, RateLimitError, InvalidResponseError, LLMError) as e:
                    last_error = f"{model_label} attempt {attempt}: {e}"
                    logger.warning(last_error)
                    if attempt < retries:
                        logger.info("Retrying %s...", model_label)
                    else:
                        logger.warning(
                            "Exhausted retries for %s, %s",
                            model_label,
                            "falling back" if model_name != models_to_try[-1][0] else "marking failed",
                        )
                except ValidationError as e:
                    last_error = f"{model_label} attempt {attempt}: validation failed - {e}"
                    logger.warning(last_error)
                    if attempt < retries:
                        logger.info("Retrying %s after validation failure...", model_label)
                    else:
                        logger.warning(
                            "Exhausted retries for %s after validation failure, %s",
                            model_label,
                            "falling back" if model_name != models_to_try[-1][0] else "marking failed",
                        )

        raise LLMError(f"All providers exhausted. Last error: {last_error}")
