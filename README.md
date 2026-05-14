# Mystic Pet

A tiny cat-witch desktop companion. Whispers cursed thoughts at you all day.
Click to enter ritual mode for a tarot reading powered by an LLM.

> Status: pre-alpha. Linux-only during initial development.

## What it does

- Lives quietly on your desktop as a small transparent overlay.
- **Idle mode:** randomly whispers delulu / cursed / lore-coded one-liners.
- **Ritual mode:** click the pet → curtain animation → ask a question → 3 cards drawn → LLM-generated reading in pet's voice.

See `IMPLEMENTATION_PLAN.md` for the full design and roadmap.
See `idea_bucket.md` for the broader idea exploration that led here.

## Status

- Currently scaffolding Phase 1 MVP (Linux only).
- Cross-platform support planned for later phases.

## Dev Setup (Linux)

```bash
# Use Python 3.11 or 3.12 — PyQt6 has no wheels for 3.13/3.14 yet.
python3.12 -m venv .venv
source .venv/bin/activate            # or activate.csh on tcsh
pip install --upgrade pip
# --only-binary required: pip 26 may try to build PyQt6 from source otherwise
pip install --only-binary=:all: -r requirements.txt
pip install --only-binary=:all: pytest

# AMD internal LLM gateway: ensure your shell has these env vars
# (already in ~/.cshrc): ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL,
# ANTHROPIC_CUSTOM_HEADERS

python -m pytest -q                  # run scaffold tests
python main.py                       # launch the pet
```

## Project Layout

```
config/             defaults + user settings (YAML)
pet/                overlay window, sprite renderer, state machine
whisper/            idle whisper library + scheduler
ritual/             tarot ceremony window, deck, LLM reader
llm/                Anthropic client wrapper, prompt templates
persistence/        SQLite schema + reading log
platform_adapter/   per-OS backends (linux now, mac/win stubs)
assets/             pet sprites, deck art, sfx (mostly empty for MVP)
tests/              pytest scaffolding tests
```

## License

TBD.

## History

This repo previously hosted a desktop cat pet experiment. That work is preserved on:

- `archive/cat-pet-v1` — last canonical state on remote main
- `archive/cat-pet-v1-wip` — local WIP at time of pivot

The `main` branch was reset to start the Mystic Pet project.
