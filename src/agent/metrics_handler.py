"""Metrics handler - streams metrics to frontend via data channel."""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .assistant import Assistant

logger = logging.getLogger("agent.metrics")

# Metrics field mappings by type
METRICS_FIELDS = {
    "LLM": ["prompt_tokens", "completion_tokens", "total_tokens", "tokens_per_second", "ttft", "duration"],
    "STT": ["audio_duration"],
    "TTS": ["ttfb", "duration", "audio_duration", "characters_count"],
    "EOU": ["end_of_utterance_delay", "transcription_delay"],
}


def _extract_metrics(metric, fields: list[str]) -> dict:
    """Extract and round numeric fields from a metric object."""
    data = {}
    for field in fields:
        value = getattr(metric, field, 0)
        data[field] = round(value, 4) if isinstance(value, float) else value
    return data


async def send_metrics_to_frontend(assistant: "Assistant", collected_metrics) -> None:
    """Send metrics to frontend based on type."""
    try:
        metrics_list = collected_metrics if isinstance(collected_metrics, list) else [collected_metrics]
        
        for metric in metrics_list:
            metric_type = type(metric).__name__
            
            for key, fields in METRICS_FIELDS.items():
                if key in metric_type:
                    await assistant.send_metrics_to_frontend(key.lower(), _extract_metrics(metric, fields))
                    break
    except Exception as e:
        logger.error(f"Error sending metrics: {e}")


async def send_usage_summary(assistant: "Assistant", summary) -> None:
    """Send final usage summary to frontend."""
    try:
        await assistant.send_metrics_to_frontend("usage_summary", {
            "llm_prompt_tokens": summary.llm_prompt_tokens,
            "llm_completion_tokens": summary.llm_completion_tokens,
            "tts_characters_count": summary.tts_characters_count,
            "stt_audio_duration": summary.stt_audio_duration,
        })
    except Exception as e:
        logger.error(f"Error sending usage summary: {e}")
