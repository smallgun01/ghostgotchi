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
- Rationale: the Gemini Live transport (F2) is ported from the
  owner's own PlatformIO/Kai POC (`poc/gemini-live-transport-p1a`);
  staying in the same ecosystem avoids a rewrite.

## Conversation

- One Gemini Live session per conversation: STT + LLM + TTS in a
  single connection. Never build a STT → LLM → TTS relay chain.
- Persona = the session's system prompt, derived from
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
  cloud state service (task B1) is the single source of truth for
  Longing + lastFedAt. Clients cache locally (NVS on the gadget,
  localStorage in the web twin) for offline moments and reconcile
  to the cloud copy on reconnect, last-write-wins by timestamp.
  After a sync, both front ends MUST show the same Longing.
- Faces change only on a confirmed Mood change, never on every
  Longing tick (no flicker).

## Keys and the web twin

- The Gemini API key NEVER appears in client-side code or bundles.
  The web twin uses a tiny server-side relay that mints short-lived
  ephemeral tokens, with a per-IP/session rate limit.
- If the relay is down, the web twin shows "ghost is asleep", not a
  stack trace.

## Repo and submission rules (from the Kiroween rules, read 2026-11-23)

- New project started after 2026-10-30; public GitHub repo;
  detectable open-source licence; `/.kiro/` at the root and NOT in
  `.gitignore`.
- The Gemini Live transport derives from the entrant's own
  pre-hackathon POC (`poc/gemini-live-transport-p1a`) — disclose
  this in the Devpost submission.
- All submission materials in English (or with English translation).
  Demo video ≤ 3 minutes, public on YouTube.
- Category: Frankenstein. Deadline 2026-12-05 06:00 Taipei;
  submit by 2026-12-03.

