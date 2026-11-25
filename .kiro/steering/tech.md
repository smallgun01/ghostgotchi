---
inclusion: always
---

# Tech steering — Ghostgotchi

## Toolchain (decided 2026-11-24 — do not re-open)

- **PlatformIO + Arduino framework. ESP-IDF is NOT used.**
  Every agent working on this project must assume PlatformIO;
  never propose or install ESP-IDF.
- Hardware: M5StickS3 (ESP32-S3-PICO-1-N8R8, 8 MB flash, 8 MB octal PSRAM).
- Platform pin: `pioarduino` 55.03.312-1 (Arduino-ESP32 3.x — the
  stock `espressif32` platform is stuck on 2.x and must NOT be used).
- PlatformIO env name: `sticks3` (matches Kai v0.12.0 and Amusant).
- Build command: `& "$env:USERPROFILE\.platformio\penv\Scripts\pio.exe" run -e sticks3 -d gadget` (pio is not in PATH; use full path).
- Flash command: same with `-t upload` appended (hold side button ~2 s first).
- Core lib_deps (pinned, change deliberately):
  `M5Unified@0.2.23`, `M5GFX@0.2.30`, `WebSockets@2.7.3`,
  `ArduinoJson@7.4.3`, `codec-opus` (pschatzmann, fixed-point build).
- Rationale: the gadget firmware reuses Kai v0.12.0's audio and
  voice_codec modules verbatim; the relay derives from Grok-Amusant.

## Architecture (decided 2026-11-25 — do not re-open)

- **Relay architecture.** The relay holds the Gemini Live session
  and the Gemini API key. Neither the gadget nor the browser ever
  sees the key. There is no ephemeral-token layer.
- **Gadget protocol:** Kai device protocol unchanged — ptt_start /
  Opus binary frames / ptt_end. The relay translates to Gemini Live.
- **Browser protocol:** browser connects to the relay via WebSocket
  directly (same `/ws` endpoint or a sibling). No token relay, no
  key in the client.
- **Ghost state:** Longing + lastFedAt live in the relay process
  (task B1 merged into relay). No separate cloud service.
- **One relay process** handles: gadget WebSocket, browser
  WebSocket, Gemini Live sessions, ghost state store.
- Relay language: Python (derived from Grok-Amusant's relay +
  fast_voice/gemini.py at https://github.com/smallgun01/Grok-Amusant).
- Deployment: owner's existing server (Oracle Cloud free tier or
  equivalent).

## Conversation

- One Gemini Live session per conversation: STT + LLM + TTS in a
  single relay-to-Gemini connection. The gadget and browser stream
  audio to the relay; the relay proxies it to Gemini.
- Persona = the Gemini Live system prompt on the relay, derived from
  `steering/product.md`. Prompt and persona bible must stay in sync
  (see the hook).
- Push-to-talk on both front ends. Sessions are short (1–2 min =
  one feeding). Session failure → sad face + one-line error, no
  crash, no reboot.

## Pet state machine (invariants — do not break these)

- Longing is the ONLY stat (0–100). It rises with wall-clock time
  since the last conversation and falls per minute of real
  conversation. Never below 0, never above 100.
- Mood is ALWAYS derived from Longing (0–33 Content, 34–66 Okay,
  67–100 Crying). Never set Mood directly.
- A conversation under ~10 seconds does NOT count as a feeding.
- Persistence: ONE ghost, two bodies (decided 2026-11-24). The
  relay's ghost state store is the single source of truth for
  Longing + lastFedAt. Clients cache locally (NVS on the gadget,
  localStorage in the web twin) for offline moments and reconcile
  to the relay copy on reconnect, last-write-wins by timestamp.
  After a sync, both front ends MUST show the same Longing.
- Faces change only on a confirmed Mood change, never on every
  Longing tick (no flicker).

## Keys

- The Gemini API key lives ONLY on the relay (server-side env var).
  Never in gadget firmware, never in browser code or bundles.
- If the relay is down, both clients show "ghost is asleep", not a
  stack trace.
- Per-IP/session rate limit enforced on the relay.

## Repo and submission rules (from the Kiroween rules, read 2026-11-23)

- New project started after 2026-10-30; public GitHub repo;
  detectable open-source licence; `/.kiro/` at the root and NOT in
  `.gitignore`.
- The relay derives from Grok-Amusant (https://github.com/smallgun01/Grok-Amusant),
  the owner's own pre-hackathon project; the gadget firmware reuses
  Kai v0.12.0 audio modules. Disclose both in the Devpost submission.
- All submission materials in English (or with English translation).
  Demo video ≤ 3 minutes, public on YouTube.
- Category: Frankenstein. Deadline 2026-12-05 06:00 Taipei;
  submit by 2026-12-03.
