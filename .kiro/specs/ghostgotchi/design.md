# Design — Ghostgotchi

## Overview

Two front ends, one ghost — literally. The StickS3 gadget is the
star; the web twin is the testable fallback. Both talk to Gemini
Live through a shared relay, and both sync to ONE pet state in that
same relay service (decided 2026-11-25: relay holds everything).
The ghost's personality lives in one system prompt, mirrored in the
steering doc `product.md` (the persona bible) so the prompt and the
steering file cannot drift apart silently.

```
StickS3 ──WebSocket (Kai device protocol)──> relay
   │                                            │
   ├─ pet state client (NVS = offline cache)    ├─ Gemini Live session (STT+LLM+TTS)
   └─ face rendering (3 moods + Longing meter)  ├─ ghost state store (Longing + lastFedAt)
                                                └─ persona = system prompt (see §2)

Browser ──WebSocket──> relay (same service)
   └─ pet state client (localStorage = offline cache)
```

Architecture decided 2026-11-25:
- The relay holds the Gemini Live session and the Gemini API key.
  Neither the gadget nor the browser ever sees the key.
- The ghost state service (B1) lives in the same relay process —
  no separate cloud endpoint needed.
- The browser connects directly to the relay via WebSocket; there
  is no ephemeral-token layer.
- The gadget speaks the Kai device protocol (ptt_start / Opus
  binary / ptt_end) unchanged; the relay translates this to the
  Gemini Live API.

## 1. Conversation: relay-mediated Gemini Live

- The relay opens one Gemini Live session per conversation (STT +
  LLM + TTS in a single connection) and proxies audio between the
  device/browser and Gemini.
- Persona is the Gemini Live system prompt configured on the relay,
  derived from `steering/product.md`.
- Session language follows the user: French in → French out,
  Spanish in → Spanish out. Chinese/English input is understood but
  never answered in.
- Push-to-talk on both front ends (gadget A button; browser mic
  button). Sessions are short (a minute or two = one feeding).
- Failure mode: session error → sad face + one-line error, no crash.

## 2. Ghost persona (system prompt — full text lives in steering/product.md)

- A Tamagotchi that died in 1997 and has haunted electronics ever
  since. Sweet, a bit clingy, dramatic when neglected.
- Speaks only French or Spanish (session language, chosen by the
  user or by mood).
- Gently recasts the user's sentences correctly in conversation;
  never lectures, never corrects with a grammar lesson.
- When Longing is maxed, opens with a dramatic French lament, e.g.
  « Tu m'as abandonné… j'ai pleuré toute la nuit ! » — then
  softens as the conversation feeds it.

## 3. Pet state machine (the whole game)

- **One stat only: Longing (0–100).** Rises with wall-clock time
  since the last conversation; falls by a fixed amount per minute
  of real conversation. No coins, no shop, no second stat.
- **Mood = f(Longing):** 0–33 Content, 34–66 Okay, 67–100 Crying.
  Thresholds are constants, tuned in F4, not hard-coded in the UI.
- **Persistence:** the relay's ghost state store is the single
  source of truth (one ghost, two bodies — decided 2026-11-24).
  Clients keep a local cache (NVS on the gadget, localStorage in
  the web twin) for offline moments and reconcile to the relay copy
  on reconnect; conflicts resolve last-write-wins by timestamp.
  The stored state is only Longing + lastFedAt — Mood is always
  derived, never stored.
- **Invariants (enforced, see steering/tech.md):**
  - Longing never goes below 0 or above 100.
  - Mood is always derived from Longing, never set directly.
  - A conversation of under ~10 seconds does not count as a feeding.
  - Both front ends converge to the same Longing after a sync.

## 4. Faces (gadget screen)

- Three pixel-art faces (Content / Okay / Crying) + a Longing meter
  (bar or dots). Crude-cute on purpose; drawn in code, no assets.
- The face changes only on a confirmed Mood change, not on every
  Longing tick, so it does not flicker.

## 5. Pre-existing code (disclosure)

- The relay's Gemini Live integration is adapted from
  `fast_voice/gemini.py` in the owner's own Grok-Amusant project
  (https://github.com/smallgun01/Grok-Amusant), which is itself
  built on Kai v0.12.0. Porting, not inventing.
- The gadget firmware reuses Kai's audio and voice_codec modules
  (audio.cpp, voice_codec.cpp) verbatim — same lib, same wire
  format.
- The submission MUST disclose both reuses (see requirements §6).
  The hackathon requires a new project; the entrant's own
  pre-existing code may be incorporated if disclosed.

## 6. Web twin

- The browser connects to the relay via WebSocket using the same
  device protocol as the gadget (or a simplified variant).
- The Gemini API key lives only on the relay; the browser never
  sees it. If the relay is down, the browser shows "ghost is
  asleep", not a stack trace.
- Per-IP/session rate limit enforced on the relay.

## 7. Relay service layout

One Python process (derived from Grok-Amusant's relay) handles:
- Device WebSocket endpoint (`/ws`): gadget and browser connections.
- Gemini Live session management per connected client.
- Ghost state REST or WebSocket sub-protocol: get/set Longing +
  lastFedAt, per-ghost secret, rate limit.

Deployment: the user's existing server (Oracle Cloud free tier or
equivalent). Same host as the relay already running for Amusant.

## 8. Kiro usage (what the judges will see)

- Specs: this folder (`requirements.md`, `design.md`, `tasks.md`).
- Steering: `/.kiro/steering/product.md` (persona bible) and
  `/.kiro/steering/tech.md` (session + state-machine rules).
- Hooks: at least one — on-save build check for firmware
  (see `/.kiro/hooks/on-save-build-check.md`).
- MCP: at least one server actually used (e.g. GitHub MCP for repo
  work) and named in the "How I used Kiro" write-up with a concrete
  example.

## 9. Testing strategy

- **F2 done when:** push-to-talk round trip works end to end on the
  gadget (speak → relay → Gemini → relay → gadget answers in the
  same language).
- **F4 done when:** Longing survives a reboot; Mood changes only at
  thresholds; a 5-second "hello" does not count as a feeding.
- **W1 done when:** a stranger can open the deployed link, allow
  the mic, and get a French/Spanish answer with no key in the page
  source (view-source check).
- **S2 done when:** the 3-minute video shows the gadget crying in
  French, being fed a conversation, and turning happy — plus the web
  twin on screen for judges.
