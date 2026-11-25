# Tasks — Ghostgotchi

Sizes are the user's hands-on hours with Kiro doing the typing.
Phasing: v1 = the ghost talks (F1–F3 + W1). v2 = it longs for you
(F4–F5 + B1 + W2–W3). Submission: S1–S2. S3 is optional.
Schedule (deadline Sat 2026-12-05 06:00 Taipei; submit 12-03):
11/24 F1 · 11/25 evening mostly blocked (16:00 school pickup +
18:00 W800 maintenance — moved up from Fri) · 11/26–27 F2+F3
(ghost talks by Fri night) · 11/28 OFF (anniversary lunch) ·
11/29 F5+W1 · 11/30 W1+B1 · 12/01 W2+W3 · 12/02 buffer ·
12/03 S1+S2, submit · 12/04 buffer / optional S3.

- [x] **F1 — New repo + Kiro setup.** Fresh public GitHub repo,
  MIT licence, `/.kiro/` from this pack at the root (NOT in
  .gitignore), gadget project skeleton builds. Kiro warm-up.
  Size S (~1 h). _Requirements: 5.1, 5.2, 5.3_
- [ ] **F2 — Port the Gemini Live transport.** Bring the p1a POC's
  WebSocket audio streaming into the new project; push-to-talk round
  trip works end to end on the gadget. Porting a proven path, not
  research. Disclose the reuse in the submission.
  Size M (~3–4 h). _Requirements: 1.1, 1.4, 6.2_
- [ ] **F3 — Ghost persona prompt.** System prompt per design §2 /
  steering/product.md: FR/ES only, in-character, gentle recasting.
  Tune until it feels like a pet, not a tutor.
  Size S (~1 h incl. tuning). _Requirements: 1.2, 1.3_
- [ ] **F4 — Pet state machine.** Longing rises over time, drops on
  conversation; mood thresholds; 10-second minimum for a feeding;
  invariants from design §3. Syncs with the cloud state service
  (B1); NVS is the offline cache, not the source of truth.
  Size S–M (~2 h). _Requirements: 2.1, 2.2, 2.3, 2.4_
- [ ] **F5 — Faces.** Three mood faces + Longing indicator on the
  gadget screen. Pixel art in code, no assets; face changes only on
  confirmed Mood change.
  Size S (~1–2 h). _Requirements: 3.1, 3.2, 3.3_
- [ ] **W1 — Web shell + token relay.** Mic capture, Gemini Live
  session via ephemeral-token relay, push-to-talk in the browser.
  Key never in client code; per-session rate limit.
  Size M (~3 h). _Requirements: 4.1, 4.2, 4.3_
- [ ] **B1 — Ghost state API.** Tiny cloud endpoint: get/set Longing
  + lastFedAt for the ONE shared ghost; per-ghost secret; rate
  limit. Can live next to the W1 token relay.
  Size S (~1–2 h). _Requirements: 2.1, 2.4_
- [ ] **W2 — Shared pet logic in web.** Same Longing/Mood machine,
  reads/writes the shared cloud state (B1); localStorage is only a
  cache. Same persona prompt.
  Size S (~1–2 h). _Requirements: 2.1, 2.2, 2.3, 4.1_
- [ ] **W3 — Haunted Tamagotchi UI.** Spooky-cute shell: egg-shaped
  frame, dark room, floating ghost; mood face + Longing meter.
  Size S–M (~2 h). _Requirements: 3.1, 3.2, 4.1_
- [ ] **S1 — Devpost texts.** English description, "How I used Kiro"
  write-up (one concrete example per feature: specs, steering,
  hooks, MCP), POC-reuse disclosure. Fluffy drafts, user approves.
  Size S–M (~2 h). _Requirements: 6.1, 6.2, 6.3_
- [ ] **S2 — Demo video ≤ 3 min.** Script: ghost cries in French →
  user feeds it a conversation → ghost happy; web twin shown for
  judges. Film, light edit, YouTube upload.
  Size M (~3 h). _Requirements: 6.1, 6.3_
- [ ] **S3 — (Optional) Blog post** for the Bonus Blog Prize +
  a #KiroweenHackathon26 social post. Size S (~1 h).

**Total: 11 core tasks + 1 optional ≈ 20–26 hands-on hours.**
**v1-only cut** (F1–F3 + W1 + S1–S2, pet loop faked by mood prompt):
roughly half that, still submittable if life intervenes.
