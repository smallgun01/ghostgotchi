# Hook — on-save build check (create in the Kiro UI)

Kiro's hook format is version-specific, so this file describes the
hook to create rather than shipping a JSON file that may not load.
Create it in Kiro under **Agent Hooks** (or the equivalent in the
Kiro version the user installs for F1):

- **Name:** `ghostgotchi-on-save-build`
- **Trigger:** on file save, matching any of:
  - `gadget/src/**/*.cpp`
  - `gadget/src/**/*.h`
  - `gadget/include/**/*.h`
- **Action:** `pio run -d gadget -e sticks3`
  Report pass/fail in the chat. Do NOT auto-commit on success.
- **Why it exists:** the gadget is the riskiest part of the build;
  catching a broken build at save time is cheaper than catching it
  on demo day. It is also the concrete "hooks" example for the
  "How I used Kiro" write-up.

## Second hook (optional, create only if the first works)

- **Name:** `ghostgotchi-persona-sync-reminder`
- **Trigger:** on change to `/.kiro/steering/product.md`
  (the persona bible).
- **Action:** remind the agent to update the Gemini Live system
  prompt to match, so prompt and bible cannot drift apart.
- **Why:** the persona bible is the single source of truth for the
  ghost's voice (see `steering/product.md`).
