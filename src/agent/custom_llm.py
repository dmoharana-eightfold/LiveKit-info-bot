"""Custom Groq LLM - Extends LiveKit's OpenAI plugin to use Groq's API."""

import os
import logging
import httpx
from livekit.plugins.openai import LLM as OpenAILLM

logger = logging.getLogger("agent.llm")

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class CustomGroqLLM(OpenAILLM):
    """Groq LLM wrapper using OpenAI-compatible API."""
    
    def __init__(
        self,
        *,
        model: str = "llama-3.3-70b-versatile",
        api_key: str | None = None,
        temperature: float | None = None,
        timeout: httpx.Timeout | None = None,
    ) -> None:
        groq_api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY required (argument or env var)")
        
        super().__init__(
            model=model,
            api_key=groq_api_key,
            base_url=GROQ_BASE_URL,
            temperature=temperature,
            timeout=timeout or httpx.Timeout(connect=15.0, read=30.0, write=5.0, pool=5.0),
        )
        self._model_name = model
        logger.info(f"Groq LLM initialized: {model}")
    
    @property
    def model(self) -> str:
        return self._model_name
    
    @property
    def provider(self) -> str:
        return "groq"
