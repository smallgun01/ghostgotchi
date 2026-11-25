# Design — Ghostgotchi

## Overview

Two front ends, one ghost — literally. The StickS3 gadget is the
star; the web twin is the testable fallback. Both talk to Gemini
Live through a single session per conversation, and both sync to
ONE pet state in a tiny cloud store (decided 2026-11-24: "one
ghost, two bodies"). The ghost's personality lives in one system
prompt, mirrored in the steering doc `product.md` (the persona
bible) so the prompt and the steering file cannot drift apart
silently.

```
StickS3 ──WebSocket──> Gemini Live (STT + LLM + TTS, one session)
   │                        └─ persona = system prompt (see §2)
   ├─ pet state client (NVS = offline cache)
   └─ face rendering (3 moods + Longing indicator)

Web twin ──mic──> tiny token relay ──> Gemini Live (same persona)
   └─ pet state client (localStorage = offline cache)

        both clients ──> Ghost state service (tiny cloud store:
                         Longing + lastFedAt — the ONE ghost)
```

## 1. Conversation: one Gemini Live connection

- No STT → LLM → TTS relay chain. Gemini Live handles all three in
  a single session; the persona is only the session's system prompt.
- Session language follows the user: French in → French out,
  Spanish in → Spanish out. Chinese/English input is understood but
  never answered in.
- Push-to-talk on both front ends (gadget button; web mic button).
  Sessions are short (a minute or two = one feeding).
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
- **Persistence:** the cloud state service is the single source of
  truth (one ghost, two bodies — decided 2026-11-24). Clients keep
  a local cache (NVS on the gadget, localStorage in the web twin)
  for offline moments and reconcile to the cloud copy on reconnect;
  conflicts resolve last-write-wins by timestamp. The stored state
  is only Longing + lastFedAt — Mood is always derived, never
  stored.
- **Invariants (enforced, see steering/tech.md):**
  - Longing never goes below 0 or above 100.
  - Mood is always derived from Longing, never set directly.
  - A conversation of under ~10 seconds does not count as a feeding.
  - Both front ends converge to the same Longing after a sync.

## 4. Faces (gadget screen)

- Three pixel-art faces (Content / Okay / Crying) + a Longing meter
  (bar or dots). Crude-cute on purpose; drawn in code, no assets.
- The moving-trailing-stop lesson from the user's other project
  applies here too: the face changes only on a confirmed Mood
  change, not on every Longing tick, so it does not flicker.

## 5. Pre-existing code (disclosure)

- The Gemini Live transport is ported from the user's own POC
  branch `poc/gemini-live-transport-p1a`, which already proved
  ESP32 ↔ Gemini Live audio streaming. Porting, not inventing.
- The submission MUST disclose this reuse (see requirements §6).
  The hackathon requires a new project; the entrant's own
  pre-existing code may be incorporated if disclosed.

## 6. Web twin + token relay

- Browser cannot hold the Gemini API key. A minimal relay (serverless
  or the user's Oracle Cloud free tier) mints ephemeral tokens.
- Relay rules: short-lived tokens only, per-IP/session rate limit,
  no token reuse across sessions. If the relay is down, the web twin
  shows a clear "ghost is asleep" state instead of a stack trace.

## 7. Kiro usage (what the judges will see)

- Specs: this folder (`requirements.md`, `design.md`, `tasks.md`).
- Steering: `/.kiro/steering/product.md` (persona bible) and
  `/.kiro/steering/tech.md` (session + state-machine rules).
- Hooks: at least one — on-save build check for firmware
  (see `/.kiro/hooks/on-save-build-check.md`).
- MCP: at least one server actually used (e.g. GitHub MCP for repo
  work) and named in the "How I used Kiro" write-up with a concrete
  example.

## 8. Testing strategy

- **F2 done when:** push-to-talk round trip works end to end on the
  gadget (speak → ghost answers in the same language).
- **F4 done when:** Longing survives a reboot; Mood changes only at
  thresholds; a 5-second "hello" does not count as a feeding.
- **W1 done when:** a stranger can open the deployed link, allow
  the mic, and get a French/Spanish answer with no key in the page
  source (view-source check).
- **S2 done when:** the 3-minute video shows the gadget crying in
  French, being fed a conversation, and turning happy — plus the web
  twin on screen for judges.
