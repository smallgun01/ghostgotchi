# Requirements — Ghostgotchi

## Introduction

Ghostgotchi is a Tamagotchi that died, came back as a ghost, and now
lives in an ESP32-S3 desk gadget. It only speaks French and Spanish.
The only way to feed it is to practise speaking with it every day.
A web twin (same ghost, same persona) lets judges play with it
without the hardware. Category: **Frankenstein**. Deadline:
**2026-12-05 06:00 Taipei** (2026-12-04 14:00 PT). Submit by
2026-12-03; keep 2026-12-04 as buffer.

## Glossary

- **Ghost / pet:** the Tamagotchi ghost. One stat only: Longing.
- **Longing （想念值）:** rises with time since the last conversation,
  falls when the user talks with it.
- **Feeding:** one real spoken conversation in French or Spanish
  (a minute or two), not a button press.
- **Mood:** Content / Okay / Crying, derived from Longing only.
- **Web twin:** the browser version of the same ghost, for judges.
- **v1:** the ghost talks. **v2:** longing meter + faces (a real pet).

## Requirements

### Requirement 1 — The ghost talks (v1)

**User Story:** As a language learner, I want to press a button on
the gadget, speak French or Spanish, and hear the ghost answer in
that language, so that speaking practice feels like visiting a pet.

#### Acceptance Criteria

1. WHEN the user presses talk on the gadget, THE Ghostgotchi_System
   SHALL open one Gemini Live session (STT + LLM + TTS in a single
   connection) and respond in the ghost's voice.
2. WHEN the user speaks French, THE Ghostgotchi_System SHALL answer
   in French; WHEN the user speaks Spanish, THE Ghostgotchi_System
   SHALL answer in Spanish; it SHALL NOT answer in Chinese or
   English (it understands Chinese input but never replies in it).
3. WHEN the ghost replies, THE Ghostgotchi_System SHALL gently model
   the correct sentence back instead of lecturing (conversation
   partner, not teacher).
4. WHEN the Gemini Live session fails, THE Ghostgotchi_System SHALL
   show a sad face and a one-line error, and SHALL NOT crash or
   require a reboot.

### Requirement 2 — One stat: Longing

**User Story:** As the ghost's owner, I want the ghost to miss me
when I ignore it, so that daily practice has an emotional reason to
happen.

#### Acceptance Criteria

1. THE Ghostgotchi_System SHALL maintain a single Longing value that
   rises with elapsed time since the last conversation and falls
   after a conversation.
2. THE Ghostgotchi_System SHALL persist Longing across reboots
   and across front ends: the single source of truth SHALL be a
   tiny cloud state service shared by the gadget and the web twin
   (one ghost, two bodies); local copies (NVS on the gadget,
   localStorage in the web twin) SHALL serve only as offline
   caches and SHALL reconcile to the cloud copy on reconnect.
3. THE Ghostgotchi_System SHALL derive Mood from Longing only:
   low = Content, mid = Okay, maxed = Crying.
4. WHEN Longing is maxed and the user picks the ghost up,
   THE Ghostgotchi_System SHALL greet the user with a French
   sentence of dramatic longing before anything else.
5. WHEN the user feeds the ghost on either front end, THE
   Ghostgotchi_System SHALL lower the same shared Longing, so the
   other front end shows the fed ghost too.

### Requirement 3 — Three faces

**User Story:** As the owner, I want to see at a glance how the
ghost feels, so the desk gadget works even when I do not talk to it.

#### Acceptance Criteria

1. THE Ghostgotchi_System SHALL render three mood faces on the
   gadget screen: Content, Okay, Crying.
2. THE Ghostgotchi_System SHALL show a Longing indicator alongside
   the face.
3. THE Ghostgotchi_System SHALL use simple, deliberately crude-cute
   pixel art (no external image assets required).

### Requirement 4 — Web twin (judge-testable)

**User Story:** As a hackathon judge without the hardware, I want to
open a link, speak into my microphone, and play with the same ghost,
so I can evaluate the entry.

#### Acceptance Criteria

1. THE Ghostgotchi_System SHALL provide a deployed web app (not
   localhost) that offers the same persona and the same
   Longing/Mood machine as the gadget.
2. THE Ghostgotchi_System SHALL mint ephemeral Gemini tokens via a
   tiny server-side relay; the Gemini API key SHALL NOT appear in
   any client-side code or bundle.
3. THE Ghostgotchi_System SHALL rate-limit the relay so one visitor
   cannot drain the owner's API quota.
4. IF the firmware is not ready, THE Ghostgotchi_System SHALL still
   be submittable on the web twin alone (gadget = demo-video star,
   web twin = testable app link).

### Requirement 5 — Kiro-native build

**User Story:** As the entrant, I want the project to be visibly
built with Kiro, so it passes the rules' Kiro-usage bar.

#### Acceptance Criteria

1. THE Ghostgotchi_System SHALL be developed in Kiro, with this
   spec (`/.kiro/specs/ghostgotchi/`), steering docs
   (`/.kiro/steering/`), at least one hook, and at least one MCP
   server actually used.
2. THE Ghostgotchi_System SHALL keep `/.kiro/` at the repo root and
   NOT in `.gitignore`.
3. THE Ghostgotchi_System SHALL be a new project started after
   2026-10-30, in a public GitHub repo with a detectable
   open-source licence.

### Requirement 6 — Submission-ready

**User Story:** As the entrant, I want every submission artefact
ready by 2026-12-03, so the deadline morning is not a scramble.

#### Acceptance Criteria

1. THE Ghostgotchi_System SHALL ship with an English Devpost
   description, a "How I used Kiro" write-up (one concrete example
   per Kiro feature: specs, steering, hooks, MCP), and a demo video
   of 3 minutes or less on YouTube.
2. THE Ghostgotchi_System SHALL disclose in the submission that its
   Gemini Live transport derives from the entrant's own
   pre-hackathon POC (`poc/gemini-live-transport-p1a`).
3. THE Ghostgotchi_System SHALL present all submission materials in
   English (or with English translation), including video narration
   or subtitles.
