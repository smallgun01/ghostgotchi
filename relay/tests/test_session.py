"""
Integration tests for relay/session.py using a fake Gemini provider.
No real API key needed.
"""
import asyncio
import json
import struct
import unittest

import websockets.asyncio.client as ws_client
from websockets.asyncio.server import serve

from relay.session import make_handler


# ---- Fake provider --------------------------------------------------------

class FakeProvider:
    """Fires one 10ms silent PCM chunk then turn_complete, immediately."""

    provider_id = "fake"

    def __init__(self, system_prompt: str):
        self._on_audio = None
        self._on_turn_complete = None
        self._on_error = None
        self._connected = False

    def on_audio(self, cb): self._on_audio = cb
    def on_transcript(self, cb): pass
    def on_tool_call(self, cb): pass
    def on_tool_calls_complete(self, cb): pass
    def on_interrupted(self, cb): pass
    def on_turn_complete(self, cb): self._on_turn_complete = cb
    def on_error(self, cb): self._on_error = cb

    async def connect(self):
        self._connected = True

    async def close(self):
        self._connected = False

    async def send_audio(self, frame): pass

    async def start_turn(self):
        # Emit one tiny silent PCM chunk at 24kHz (480 bytes = 10ms)
        from relay.fast_voice import AudioFrame, CLIENT_OUTPUT_RATE_HZ
        silent = b"\x00" * 480
        if self._on_audio:
            await _maybe_await(self._on_audio(AudioFrame(silent, CLIENT_OUTPUT_RATE_HZ)))
        # Then signal turn complete
        from relay.fast_voice import TurnCompleteEvent
        if self._on_turn_complete:
            await _maybe_await(self._on_turn_complete(TurnCompleteEvent(cancelled=False)))

    async def end_turn(self): pass

    async def inject_text(self, text): pass
    async def send_tool_result(self, call_id, result): pass
    async def cancel_response(self): pass


async def _maybe_await(val):
    import inspect
    if inspect.isawaitable(val):
        await val


def _make_opus_bundle(pcm_silent_bytes: int = 320) -> bytes:
    """Build a minimal valid Kai Opus bundle with one silent packet."""
    # We can't encode real Opus without PyAV, so for testing we fake the wire format.
    # 0x02 | u16LE(len) | <fake_opus_packet>
    # DeviceOpusCodec.decode_uplink will raise DeviceProtocolError on a fake packet,
    # but the session handles that gracefully (logs and continues).
    fake_packet = b"\xfc" + b"\x00" * 3   # minimal Opus-like bytes
    return bytes([0x02]) + struct.pack("<H", len(fake_packet)) + fake_packet


# ---- Helpers ---------------------------------------------------------------

SECRET = "test-ghost-secret-12345"


def _handler():
    return make_handler(
        ghost_secret=SECRET,
        provider_factory=lambda system_prompt: FakeProvider(system_prompt),
    )


async def _run_server_and(coro):
    """Start relay on a random port, run coro(uri), return result."""
    handler = _handler()
    async with serve(handler, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]
        uri = f"ws://127.0.0.1:{port}/ws"
        return await asyncio.wait_for(coro(uri), timeout=10.0)


# ---- Tests -----------------------------------------------------------------

class TestSessionAuth(unittest.IsolatedAsyncioTestCase):

    async def test_unauthorized_no_token(self):
        async def run(uri):
            try:
                async with ws_client.connect(uri) as ws:
                    await ws.recv()
                    return "connected"
            except Exception:
                return "rejected"
        result = await _run_server_and(run)
        self.assertEqual(result, "rejected")

    async def test_wrong_token(self):
        async def run(uri):
            try:
                async with ws_client.connect(
                    uri, additional_headers={"Authorization": "Bearer wrong-token"}
                ) as ws:
                    await ws.recv()
                    return "connected"
            except Exception:
                return "rejected"
        result = await _run_server_and(run)
        self.assertEqual(result, "rejected")


class TestSessionPTT(unittest.IsolatedAsyncioTestCase):

    async def test_ptt_roundtrip(self):
        """hello → ptt_start → Opus frames → ptt_end → turn_complete received."""
        messages_received = []

        async def run(uri):
            async with ws_client.connect(
                uri, additional_headers={"Authorization": f"Bearer {SECRET}"}
            ) as ws:
                # hello
                await ws.send(json.dumps({"type": "hello", "codecs": ["opus"], "lang": "fr"}))
                # ptt_start
                await ws.send(json.dumps({"type": "ptt_start"}))
                # a few fake Opus frames (session handles decode errors gracefully)
                for _ in range(3):
                    await ws.send(_make_opus_bundle())
                # ptt_end
                await ws.send(json.dumps({"type": "ptt_end"}))
                # collect messages until turn_complete or timeout
                while True:
                    msg = await asyncio.wait_for(ws.recv(), timeout=8.0)
                    messages_received.append(msg)
                    if isinstance(msg, str):
                        data = json.loads(msg)
                        if data.get("type") == "turn_complete":
                            break

        await _run_server_and(run)
        # Confirm we got turn_complete
        controls = [json.loads(m) for m in messages_received if isinstance(m, str)]
        types = [c["type"] for c in controls]
        self.assertIn("turn_complete", types)

    async def test_no_crash_on_empty_ptt(self):
        """ptt_start immediately followed by ptt_end (no audio) → turn_complete, no crash."""
        async def run(uri):
            async with ws_client.connect(
                uri, additional_headers={"Authorization": f"Bearer {SECRET}"}
            ) as ws:
                await ws.send(json.dumps({"type": "hello", "codecs": ["opus"]}))
                await ws.send(json.dumps({"type": "ptt_start"}))
                await ws.send(json.dumps({"type": "ptt_end"}))
                while True:
                    msg = await asyncio.wait_for(ws.recv(), timeout=8.0)
                    if isinstance(msg, str) and json.loads(msg).get("type") == "turn_complete":
                        return "ok"

        result = await _run_server_and(run)
        self.assertEqual(result, "ok")


if __name__ == "__main__":
    unittest.main()
