"""
LLM Service

Performance notes
-----------------
1. The ChatOllama client is built ONCE per (max_tokens) variant and cached.
   Previously every tool/agent constructed its own LLMService, which meant
   6+ HTTP clients and 6+ "Initializing Ollama model..." passes on startup.

2. `num_predict` is now passed to the constructor. The old code used
   `self.llm.bind(options={"num_predict": max_tokens})` — langchain-ollama
   builds the `options` dict itself, so that nested key was silently
   dropped and the model generated until its own default limit. That alone
   was responsible for a large part of the slow responses.

3. `keep_alive` stops Ollama unloading the model between questions.

4. `stream()` yields tokens as they are produced so the UI shows the first
   word in ~1s instead of waiting for the whole answer.
"""

from functools import lru_cache
from typing import Iterator, Optional

from langchain_ollama import ChatOllama

from app.config.settings import settings
from app.config.logging_config import logger


@lru_cache(maxsize=8)
def _build_client(max_tokens: int, temperature: float) -> ChatOllama:
    """
    Cached ChatOllama factory. Cached on (max_tokens, temperature) so the
    underlying HTTP session and model handle are reused across requests.
    """
    logger.info(
        f"Building Ollama client (model={settings.MODEL_NAME}, "
        f"num_predict={max_tokens})"
    )
    return ChatOllama(
        model=settings.MODEL_NAME,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=temperature,
        num_predict=max_tokens,
        num_ctx=settings.NUM_CTX,
        keep_alive=settings.OLLAMA_KEEP_ALIVE,
    )


class LLMService:
    """
    Thin wrapper over ChatOllama. Construction is free — all real state
    lives in the module-level cache above, so it is safe to instantiate
    this class anywhere.
    """

    DEFAULT_TEMPERATURE = 0.2

    def __init__(self, temperature: Optional[float] = None):
        self.temperature = (
            self.DEFAULT_TEMPERATURE if temperature is None else temperature
        )

    def _client(self, max_tokens: int) -> ChatOllama:
        return _build_client(max_tokens, self.temperature)

    def invoke(
        self,
        prompt: str,
        question: str = "",
        max_tokens: int = 1100,
    ) -> str:
        """
        Blocking call. Returns the full answer as a string.
        """
        logger.info(f"LLM invoke (num_predict={max_tokens})")

        try:
            response = self._client(max_tokens).invoke(prompt)
            return response.content
        except Exception as exc:
            logger.exception("LLM Error")
            return f"Error: {exc}"

    def stream(
        self,
        prompt: str,
        max_tokens: int = 1100,
    ) -> Iterator[str]:
        """
        Streaming call. Yields text chunks as the model produces them.
        """
        logger.info(f"LLM stream (num_predict={max_tokens})")

        try:
            for chunk in self._client(max_tokens).stream(prompt):
                text = getattr(chunk, "content", "")
                if text:
                    yield text
        except Exception as exc:
            logger.exception("LLM Streaming Error")
            yield f"\n\n[Error: {exc}]"

    def warmup(self) -> None:
        """
        Fire a 1-token request so Ollama loads the model weights before the
        first real user question. Called once at API startup.
        """
        try:
            logger.info("Warming up model...")
            self._client(1).invoke("ok")
            logger.info("Model warm.")
        except Exception:
            logger.warning("Warmup failed (is Ollama running?)")
