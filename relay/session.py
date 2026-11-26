"""
Ghostgotchi relay session handler.

WebSocket /ws endpoint:
  Authenticates via Authorization: Bearer <GHOST_SECRET>
  Accepts Kai device protocol: hello / ptt_start / Opus binary / ptt_end
  Opens one Gemini Live session per PTT turn via GeminiLiveProvider
  Bridges Opus<->PCM bidirectionally via DeviceOpusCodec
  Returns {"type":"turn_complete"} when Gemini finishes

Environment variables:
  GHOST_SECRET   - per-ghost Bearer token (required)
  GEMINI_API_KEY - Gemini API key (required, never logged)
  GEMINI_MODEL   - optional, default gemini-2.0-flash-live-001
"""
from __future__ import annotations
import asyncio
import contextlib
import hmac
import json
import logging
import os
from typing import Any

from relay.fast_voice import AudioFrame, GeminiLiveProvider, ProviderError, TurnCompleteEvent
from relay.device_opus import DeviceOpusCodec, DeviceProtocolError
from relay.prompt import build_system_prompt

LOG = logging.getLogger("ghostgotchi.relay.session")


def _get_required_env(name: str) -> str:
    val = os.environ.get(name, "")
    if not val:
        raise RuntimeError(f"{name} environment variable must be set")
    return val


def make_handler(
    *,
    ghost_secret: str | None = None,
    provider_factory=None,   # injectable for tests
):
    """Return an async WebSocket handler.

    ghost_secret defaults to os.environ["GHOST_SECRET"].
    provider_factory(system_prompt) -> GeminiLiveProvider; defaults to real Gemini.
    """
    secret = ghost_secret or _get_required_env("GHOST_SECRET")

    def _default_provider_factory(system_prompt: str) -> GeminiLiveProvider:
        try:
            import google.genai as genai
            from google.genai import types as genai_types
        except ImportError:
            raise RuntimeError("google-genai is required; pip install google-genai")
        api_key = _get_required_env("GEMINI_API_KEY")
        model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-live-001")
        client = genai.Client(api_key=api_key)
        config = genai_types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            system_instruction=system_prompt,
            speech_config=genai_types.SpeechConfig(
                voice_config=genai_types.VoiceConfig(
                    prebuilt_voice_config=genai_types.PrebuiltVoiceConfig(voice_name="Charon")
                )
            ),
        )
        return GeminiLiveProvider(
            client=client,
            model=model,
            config=config,
            sdk_types=genai_types,
        )

    pf = provider_factory or _default_provider_factory

    async def handler(websocket: Any) -> None:
        # Path check
        path = getattr(websocket.request, "path", "/ws").split("?", 1)[0]
        if path != "/ws":
            await websocket.close(1008, "unknown path")
            return
        # Auth
        auth = websocket.request.headers.get("Authorization", "")
        if not hmac.compare_digest(auth, f"Bearer {secret}"):
            await websocket.close(1008, "unauthorized")
            return

        codec: DeviceOpusCodec | None = None
        provider: GeminiLiveProvider | None = None
        lang = "fr"
        ptt_open = False
        audio_queue: asyncio.Queue[bytes | None] = asyncio.Queue()
        turn_done = asyncio.Event()

        async def _send_audio_from_queue() -> None:
            """Drain outgoing audio queue → encode → send to device."""
            nonlocal codec
            while True:
                chunk = await audio_queue.get()
                if chunk is None:
                    break
                if codec is None:
                    continue
                try:
                    for bundle in codec.encode_downlink(chunk):
                        await websocket.send(bundle)
                except (DeviceProtocolError, Exception) as exc:
                    LOG.warning("downlink encode error: %s", exc)

        def on_audio(frame: AudioFrame) -> None:
            audio_queue.put_nowait(frame.data)

        def on_turn_complete(event: TurnCompleteEvent) -> None:
            audio_queue.put_nowait(None)   # sentinel: flush encoder
            turn_done.set()

        def on_error(err: ProviderError) -> None:
            LOG.warning("provider error code=%s retryable=%s", err.code, err.retryable)
            audio_queue.put_nowait(None)
            turn_done.set()

        sender_task: asyncio.Task | None = None

        try:
            async for message in websocket:
                if isinstance(message, bytes):
                    if not ptt_open or codec is None or provider is None:
                        continue
                    try:
                        pcm = codec.decode_uplink(message)
                    except DeviceProtocolError as exc:
                        LOG.warning("uplink decode error: %s", exc)
                        continue
                    if pcm:
                        await provider.send_audio(AudioFrame(pcm, 16_000))
                    continue

                try:
                    ctrl = json.loads(message)
                except (TypeError, json.JSONDecodeError):
                    continue
                if not isinstance(ctrl, dict):
                    continue
                kind = ctrl.get("type")

                if kind == "hello":
                    codecs = ctrl.get("codecs", [])
                    if "opus" in codecs:
                        try:
                            codec = DeviceOpusCodec()
                        except DeviceProtocolError as exc:
                            LOG.warning("DeviceOpusCodec unavailable: %s — audio bridging disabled", exc)
                            codec = None
                    lang = ctrl.get("lang", "fr") if ctrl.get("lang") in ("fr", "es") else "fr"

                elif kind == "ptt_start":
                    if ptt_open:
                        continue
                    ptt_open = True
                    if codec is not None:
                        codec.reset_uplink()
                    system_prompt = build_system_prompt(mood="content", language=lang)
                    provider = pf(system_prompt)
                    provider.on_audio(on_audio)
                    provider.on_turn_complete(on_turn_complete)
                    provider.on_error(on_error)
                    turn_done.clear()
                    sender_task = asyncio.create_task(_send_audio_from_queue())
                    try:
                        await provider.connect()
                        await provider.start_turn()
                    except Exception as exc:
                        LOG.error("provider connect/start_turn failed: %s", exc)
                        await websocket.send(json.dumps({"type": "state", "state": "idle"}))
                        ptt_open = False
                        provider = None
                        if sender_task:
                            audio_queue.put_nowait(None)
                            await sender_task
                            sender_task = None

                elif kind == "ptt_end":
                    if not ptt_open or provider is None:
                        continue
                    ptt_open = False
                    try:
                        await provider.end_turn()
                    except Exception as exc:
                        LOG.warning("end_turn failed: %s", exc)
                    # Wait for Gemini to finish (bounded)
                    try:
                        await asyncio.wait_for(turn_done.wait(), timeout=30.0)
                    except TimeoutError:
                        LOG.warning("turn_complete timeout; sending idle")
                    # Flush remaining encoded audio
                    if codec is not None and sender_task is not None:
                        audio_queue.put_nowait(None)
                        await sender_task
                        sender_task = None
                        try:
                            for bundle in codec.finish_downlink():
                                await websocket.send(bundle)
                        except (DeviceProtocolError, Exception) as exc:
                            LOG.warning("finish_downlink error: %s", exc)
                    await websocket.send(json.dumps({"type": "turn_complete"}))
                    # Clean up provider
                    try:
                        await provider.close()
                    except Exception:
                        pass
                    provider = None

        except Exception as exc:
            LOG.warning("session error: %s", type(exc).__name__)
        finally:
            if provider is not None:
                with contextlib.suppress(Exception):
                    await provider.close()
            if sender_task and not sender_task.done():
                audio_queue.put_nowait(None)
                with contextlib.suppress(Exception):
                    await asyncio.wait_for(sender_task, timeout=2.0)

    return handler
