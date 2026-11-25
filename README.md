# Ghostgotchi

A ghost Tamagotchi that runs on an M5Stack StickS3 (ESP32-S3) and
mirrors to a web twin. One ghost, two bodies — both talk to Gemini Live
for voice conversation (French/Spanish only) and sync pet state through
a tiny cloud store.

## Build the gadget firmware

Requires [PlatformIO Core](https://docs.platformio.org/en/latest/core/installation/index.html) or the PlatformIO IDE extension for VS Code.

```sh
cd gadget
cp include/secrets.h.example include/secrets.h
# Edit secrets.h with your Wi-Fi credentials
pio run -e sticks3           # compile
pio run -e sticks3 -t upload # flash (hold side button ~2 s first)
pio device monitor           # serial monitor
```

## Project layout

```
gadget/          PlatformIO firmware (StickS3, Arduino framework)
  src/           app entry point (main.cpp)
  include/       shared headers; secrets.h.example → copy to secrets.h

.kiro/
  specs/ghostgotchi/   requirements, design, tasks
  steering/
    product.md   ghost persona bible (source of truth for the prompt)
    tech.md      Gemini Live + state-machine constraints
  hooks/
    on-save-build-check.md   Kiro hook: build check on firmware save
```

## Licence

MIT — see `LICENSE`.
