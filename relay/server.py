"""
Run: python -m relay.server
Required env: GHOST_SECRET, GEMINI_API_KEY
Optional env: GEMINI_MODEL, RELAY_HOST (default 0.0.0.0), RELAY_PORT (default 8765)
"""
from __future__ import annotations
import asyncio
import os
import logging
from websockets.asyncio.server import serve
from relay.session import make_handler

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    host = os.environ.get("RELAY_HOST", "0.0.0.0")
    port = int(os.environ.get("RELAY_PORT", "8765"))
    handler = make_handler()
    async with serve(handler, host, port):
        logging.getLogger("ghostgotchi.relay").info(
            "Ghostgotchi relay listening on ws://%s:%d/ws", host, port
        )
        await asyncio.get_event_loop().create_future()


if __name__ == "__main__":
    asyncio.run(main())
