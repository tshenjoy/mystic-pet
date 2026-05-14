# Mystic Pet — Current Status

Last update: 2026-05-14

## Where we are

**Phase 1 (MVP Skeleton): scaffold complete, integration verification pending.**

## What's done

- Repo housekeeping: forked from old `desktop-pet` cat experiment. Old work
  preserved on `archive/cat-pet-v1` and `archive/cat-pet-v1-wip`. New `main`
  reset and pushed.
- Repo renamed: `desktop-pet` → `mystic-pet` on GitHub and locally.
- Project scaffold (40 files, ~1100 lines) committed and pushed:
  - PyQt6 transparent overlay window with placeholder pet sprite
  - Whisper system: YAML library (3 categories, ~36 lines) + jittered scheduler
  - Ritual ceremony: QDialog with question input, card draw, LLM-backed reader
  - LLM client wired for AMD internal gateway (respects ANTHROPIC_BASE_URL +
    ANTHROPIC_CUSTOM_HEADERS)
  - SQLite reading log
  - Tarot deck loader with 15-card starter Major Arcana set
  - System prompts for tarot persona ("cat-witch") and whisper voice
  - Per-OS platform adapter (Linux primary; macOS/Win stubbed)
  - Default settings YAML + user override loader
- Dev environment verified on Linux:
  - Python 3.12 venv
  - All deps install with `pip install --only-binary=:all: -r requirements.txt`
  - 7/7 pytest scaffold tests pass
  - `import main` clean, no errors

## What's not done

- Live launch test: `python main.py` not yet exercised against the X display.
- LLM end-to-end test: ritual flow not yet exercised against the AMD gateway.
- Speech bubble UI: whispers currently print to stdout. Need a small popup
  next to the pet.
- Reading log wiring: `Reader.read()` does not yet call `log_reading()`.
- Daily cap enforcement on rituals (3/day from settings).
- Settings UI: no in-app way to change frequency / mute / position yet.
- Real art assets: pet is a programmatic purple blob with a tiny black hat.
- No real animation — only the placeholder pixmap, no per-state sprites.
- No sound effects.
- Cross-platform backends: only Linux stub functions exist; no real
  screen-share detection, idle detection, or mimicry triggers yet.

## Open decisions

- Cat-witch detailed visual brief — silhouette, color palette, hat style, etc.
  (Needed before art commission or asset creation.)
- Live2D / Spine / Godot / hand-drawn for animation pipeline (under discussion).
- Whether to publish a tiny backend proxy when going beyond AMD-internal use.

## Key file references

- `IMPLEMENTATION_PLAN.md` — full roadmap, architecture, phased plan
- `idea_bucket.md` — brainstorm history that led to this concept
- `README.md` — project intro + dev setup
- `main.py` — entry point (run after scaffold setup to launch the pet)
- `config/default_settings.yaml` — all tunable defaults
- `llm/prompts/reading_system.txt` — pet's tarot persona prompt
