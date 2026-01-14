"""
Employee Directory Voice Agent

Run with: python src/agent.py start
"""

import asyncio
import logging
from dotenv import load_dotenv

from livekit import rtc
from livekit.agents import (
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    cli,
    inference,
    metrics,
    room_io,
)
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from agent.assistant import Assistant
from agent.custom_llm import CustomGroqLLM
from agent.metrics_handler import send_metrics_to_frontend, send_usage_summary

load_dotenv(".env")
logger = logging.getLogger("agent")

server = AgentServer()


def prewarm(proc: JobProcess) -> None:
    """Prewarm VAD model to reduce first-request latency."""
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("VAD model loaded")


server.setup_fnc = prewarm


@server.rtc_session()
async def run_agent(ctx: JobContext) -> None:
    """Handle a voice agent session."""
    ctx.log_context_fields = {"room": ctx.room.name}
    logger.info(f"Starting session in room: {ctx.room.name}")

    assistant = Assistant(room=ctx.room)
    usage_collector = metrics.UsageCollector()

    session = AgentSession(
        stt="assemblyai/universal-streaming:en",
        llm=CustomGroqLLM(model="llama-3.3-70b-versatile"),
        tts=inference.TTS(
            model="cartesia/sonic-3",
            voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    @session.on("metrics_collected")
    def on_metrics(ev: MetricsCollectedEvent) -> None:
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)
        asyncio.create_task(send_metrics_to_frontend(assistant, ev.metrics))

    async def on_shutdown() -> None:
        summary = usage_collector.get_summary()
        logger.info(f"Usage Summary: {summary}")
        await send_usage_summary(assistant, summary)

    ctx.add_shutdown_callback(on_shutdown)

    await session.start(
        agent=assistant,
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )
    await ctx.connect()
    logger.info(f"Session started: {ctx.room.name}")


if __name__ == "__main__":
    cli.run_app(server)
