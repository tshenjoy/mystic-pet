# Mystic Pet — Implementation Plan

Working name: **Mystic Pet** (final name TBD).
Concept: Concept A from `idea_bucket.md` — chaotic mystic companion with idle whispers + tarot ritual mode + contextual mimicry.

Existing repo to evolve: `/home/shihatan/mess/desktop/desktop-pet/`

---

## 0. Repo Housekeeping

Goals: preserve existing work as archive; start clean dev branch.

Steps:
1. `cd /home/shihatan/mess/desktop/desktop-pet`
2. Rename current `main` → `archive/cat-pet-v1` (keeps history, signals dead branch).
3. Push archive branch to remote.
4. Create new orphan-or-fresh branch `main-mystic` (or just `main` reset). Decision needed: do we want a clean-slate `main` and old `main` lives only as `archive/cat-pet-v1`? Recommend yes — new product, clean history.
5. Optionally rename repo on remote (`desktop-pet` → `mystic-pet`).

**Decision needed from user before executing:**
- Confirm rename old main → `archive/cat-pet-v1`
- Confirm clean reset of new main vs branching from old main and gutting

---

## 1. Tech Stack (reuse decision)

**Keep:**
- Python 3.x + PyQt6 (mature, transparent windows work on Linux/Win/macOS)
- Pillow (image processing)
- System tray pattern from existing `main.py`
- Transparent overlay window pattern from `pet/overlay.py`
- State machine pattern from `pet/state_machine.py`
- Window tracker concept (will repurpose for screen-share detection, not window-walking)

**Drop:**
- Cat-specific behaviors (border-walking, photo-upload recoloring, sprite recoloring pipeline)
- Window-edge collision logic
- Cat anatomy assumptions in sprite renderer

**Add:**
- LLM client (Anthropic SDK) for whispers + tarot readings
- Audio playback (QSoundEffect or pygame.mixer for tiny sound FX)
- Tarot card asset loader + ceremony renderer
- Local persistence (JSON or SQLite) for: pet memory, daily reading log, settings, library of pre-written whispers
- Screen-share detector (Linux: detect `gnome-shell` / Zoom processes / fullscreen video apps; Win/macOS: platform-specific later)
- Contextual mimicry hooks (key-press detector, audio device change, password-field heuristic — TBD)

**New requirements.txt additions:**
```
anthropic>=0.30
pyyaml>=6.0
# Linux-only audio backend
PyQt6-Multimedia>=6.5
# Process detection
psutil>=5.9
```

---

## 2. MVP Scope (Phase 1)

**Principle:** ship a vertical slice that proves the *feel*, not breadth. Single animation reused across all states. Text/voice carries personality.

**MVP must have:**
1. Pet appears as transparent overlay on desktop. Draggable to any position.
2. Single idle animation loop (e.g. one breathing-blob sprite).
3. System tray menu: show/hide, settings, quit.
4. **Idle whispers:** every N minutes (configurable), pet shows speech bubble with random line. First version pulls from local YAML library only — no LLM yet.
5. **Tarot ritual:** click pet → modal/overlay opens → "what brings you, traveler?" prompt → user types question → 3 cards drawn from hardcoded deck → LLM call returns reading → display in pet's voice → close.
6. Local SQLite log of all readings (date, question, cards, response).
7. Settings file (YAML) for: whisper frequency, LLM model, API key, position, mute audio.

**MVP must NOT have (defer):**
- Multiple animations (skip till Phase 2)
- Mimicry (typing-along, password-cover, etc. — Phase 3)
- Screen-share detection (Phase 3)
- Multiple decks / skins (Phase 4)
- Cross-platform (Phase 5)
- Audio FX beyond optional single chime (Phase 2)

**Definition of done for MVP:**
- Pet runs on Linux.
- Idle whispers fire at expected cadence.
- Full ritual flow completes: click → question → cards → reading → close.
- LLM key configurable, no hardcoded secret.
- Settings persist across restarts.

---

## 3. Architecture

```
mystic_pet/
├── main.py                      # Entry point, app lifecycle, tray
├── config/
│   ├── settings.py              # Load/save YAML settings
│   └── default_settings.yaml    # Defaults
├── pet/
│   ├── overlay.py               # Transparent always-on-top window (reuse)
│   ├── pet_widget.py            # The pet sprite + speech bubble (adapt)
│   ├── sprite_renderer.py       # Animation loop (reuse, simplify)
│   └── state_machine.py         # idle / whispering / ritual states
├── whisper/
│   ├── library.py               # Loads YAML of pre-written lines
│   ├── scheduler.py             # QTimer-based whisper cadence
│   └── lines/                   # Whisper YAML files (delulu.yaml, cursed.yaml, lore.yaml)
├── ritual/
│   ├── ceremony_window.py       # Ritual modal UI
│   ├── deck.py                  # Card definitions + draw logic
│   ├── reader.py                # LLM client wrapper, builds prompt
│   └── decks/
│       └── default/             # 78 card images + meanings YAML
├── llm/
│   ├── client.py                # Anthropic SDK wrapper, retries, timeouts
│   └── prompts/
│       ├── reading_system.txt   # System prompt for tarot persona
│       └── whisper_system.txt   # (Phase 2) for LLM whispers
├── persistence/
│   ├── db.py                    # SQLite init + schema
│   └── reading_log.py           # Insert/query past readings
├── assets/
│   ├── pet/
│   │   └── idle.gif             # Single MVP animation
│   ├── decks/                   # Card art
│   └── sfx/                     # Optional sound effects
└── tests/
```

---

## 4. Module Notes

### `pet/overlay.py`
Reuse existing pattern. Strip cat-specific code. Just: frameless, transparent, always-on-top, draggable, click-emits-signal.

### `pet/sprite_renderer.py`
Simplify radically. MVP: load one GIF, loop frames at fixed FPS. Don't build state-based sprite switching yet. State machine can call `set_animation('idle')` but only one path exists for now.

### `whisper/library.py`
Loads YAML files like:
```yaml
- "Mercury cooked for you today."
- "I think your cursor is anxious."
- "the moon owes you a snack."
```
Returns random line on demand. Categorized by type (delulu / cursed / lore) for easy A/B later.

### `whisper/scheduler.py`
QTimer fires every N min (jittered ±20% so it doesn't feel mechanical). Emits signal → pet shows speech bubble for K seconds.

### `ritual/ceremony_window.py`
New window (QDialog or full-screen translucent). Contains:
- Question input
- Card spread area (3 slots)
- Reading text area
- Close button
- Optional candle/curtain animation (skip for MVP, just a fade)

### `ritual/deck.py`
Card data: name, image path, upright meaning, reversed meaning, themes. MVP: shuffle + draw 3, randomize upright/reversed.

### `ritual/reader.py`
Builds prompt:
```
System: [tarot persona prompt]
User: Question: {q}
Cards drawn:
- {card1.name} ({orientation}): {meaning}
- {card2.name}: ...
Give a short reading in pet's voice (≤120 words).
```
Returns string.

### `llm/client.py`
Wraps `anthropic.Anthropic()`. Reads API key from settings (or env var). Timeout 15s. Retry once on transient error. Falls back to canned reading on failure.

### `persistence/db.py`
SQLite, single file under `~/.local/share/mystic-pet/`. Schema:
```sql
CREATE TABLE readings (
  id INTEGER PRIMARY KEY,
  ts TIMESTAMP,
  question TEXT,
  cards TEXT,         -- JSON
  reading TEXT,
  model TEXT
);
CREATE TABLE settings_kv (k TEXT PRIMARY KEY, v TEXT);
```

---

## 5. Phased Roadmap

### Phase 1 — MVP Skeleton (target: 1–2 weeks)
- Repo housekeeping (Section 0)
- New project skeleton (directory layout + empty modules)
- Reuse + simplify `overlay.py` + `pet_widget.py`
- Single idle animation playing
- Tray menu working
- Idle whisper system with hardcoded YAML library
- Ritual window + LLM reading flow
- Settings + DB
- Basic README + run instructions

**Verify:** can launch on Linux, see pet, get whispers, complete a ritual.

### Phase 2 — Personality & Polish (1–2 weeks)
- Add 4–6 sprite states (idle, blink, talk, sleep, ritual-pose, stretch)
- LLM-generated whispers (mix with library; rate-limited)
- Sound effects (whisper chime, card flip, curtain swoosh)
- Better ceremony UI (curtain animation, card flip animation)
- Pet voice/personality style guide → encode in system prompts
- Onboarding flow (first-launch: name your pet, pick whisper frequency)

**Verify:** vibe test with 3–5 friends; iterate on whisper tone + reading length.

### Phase 3 — Smart Companion Behaviors (2–3 weeks)
- Screen-share detection (Linux first: detect Zoom / fullscreen / screencast)
- Pet hides when share detected, "I waited" line on return
- Basic mimicry hooks:
  - Pet types-along when keyboard activity detected
  - Pet covers eyes when password field focused (Linux: AT-SPI accessibility API; risky, may defer)
  - Pet pulls headset when audio device changes
- "Missed you" return animation when user comes back from idle

**Verify:** mimicry reads as delightful, not creepy. Privacy doc clarifies what's monitored.

### Phase 4 — Content & Skins (ongoing)
- AI-generate full 78-card tarot deck (Midjourney) with consistent style
- Premium decks (cottagecore, cyberpunk, retro)
- Outfit/skin swaps for pet
- Whisper packs (seasonal, holiday, etc.)
- Pet "lore" system: progressive lore drops over weeks

### Phase 5 — Cross-Platform
- Windows: replace Linux-specific process/window detection
- macOS: same; existing project has `pyobjc` hooks worth borrowing
- Build/package: PyInstaller for Win, py2app or PyInstaller for macOS, AppImage for Linux
- Auto-update channel (Phase 6+)

### Phase 6 — Distribution
- Landing page
- Install instructions
- Free tier (limited daily readings, library whispers only) vs paid (unlimited LLM, premium decks)
- Telemetry (opt-in, anonymous: feature usage only, never content)

---

## 6. Cross-Platform Strategy

- **Stick to PyQt6 abstractions** wherever possible — gets free portability.
- **Isolate platform-specific code** behind a single `platform/` module:
  ```
  platform/
  ├── __init__.py        # detects OS, exports correct backend
  ├── linux.py
  ├── macos.py
  └── windows.py
  ```
- Linux backend: psutil + xdotool for active-window info; D-Bus for media + idle.
- macOS backend: borrow from existing project's `pyobjc` work.
- Windows backend: `pywin32` for active-window + idle.
- Each backend implements same interface: `get_active_window()`, `is_screen_sharing()`, `get_idle_seconds()`, `is_password_field_focused()` (best-effort).

---

## 7. Testing Approach

- **Unit tests** for: whisper scheduler timing, deck draw randomness, prompt builder, settings load/save, DB inserts.
- **Manual smoke test checklist** for each release (Linux, then Win, then macOS):
  - Pet appears, draggable, persists position
  - Whisper fires within expected window
  - Tray menu functions
  - Ritual completes end-to-end with valid + invalid LLM responses
  - Settings persist
  - Mute / hide / quit clean
- **Defer integration testing of LLM** — mock API in tests; manual exploratory testing for prompt quality.

---

## 8. Risk & Open Questions

| Risk | Mitigation |
|------|-----------|
| LLM cost runaway | Per-day reading cap; cache? No, readings are single-use. Just cap. |
| API key handling | Settings UI to input; store in OS keychain via `keyring` package, not plaintext YAML |
| Password-field detection on Linux | Hard. Defer or use heuristic (window title contains "password"). |
| Whisper feels spammy | Default frequency very low (every 30–60 min). User-adjustable. |
| Pet looks ugly with one sprite | Lean on personality + speech bubbles; sprite quality less critical at MVP |
| Cross-platform window detection | Start Linux-only; structure code so backends pluggable |

**Resolved decisions:**
1. **Branch strategy:** Archive old `main` → `archive/cat-pet-v1`, reset new `main` for fresh history. ✅
2. **Project name:** Rename repo `desktop-pet` → `mystic-pet`. ✅
3. **Pet aesthetic:** **Cat-witch hybrid.** Tiny cat in witch hat / cloak. Future support for user-customizable cat appearance (colors, patterns, accessories). ✅
4. **LLM cost model:** **3 readings/day cap, affordable model** (e.g. Claude Haiku or GPT-4o-mini).
   - **Security note:** static key in shipped binary is trivially extractable → cost blows up regardless of cap.
   - **MVP approach:** **BYOK (Bring Your Own Key)** — user pastes their own Anthropic key in settings. Zero backend, no abuse risk, unblocked dev.
   - **Phase 4/5 approach:** add a thin **backend proxy** (Cloudflare Worker / Lambda) that holds shared key + enforces per-device cap. Required before non-technical public release.
5. **Free vs paid plan:** Resolved — single tier for MVP. Cap (3/day) IS the limit. No paywall code in MVP. Revisit Phase 6.
6. **Whisper frequency default:** **60 min**, user-customizable in settings (range: e.g. 15 min – 4 hr).

**Remaining open questions:**
- A. Cat-witch detailed brief: silhouette? color palette? hat style? cloaked vs visible body? — needed when commissioning art.
- B. BYOK vs proxy: confirm BYOK for MVP is acceptable.
- C. Specific model choice: `claude-haiku-4-5` vs `claude-sonnet-4-6` for readings? (Haiku much cheaper, may be fine for tarot vibes.)

---

## 9. Immediate Next Steps (after plan approval)

1. Answer open questions in Section 8.
2. Execute repo housekeeping (Section 0).
3. Create skeleton directory layout (empty modules + `__init__.py` files).
4. Port + simplify `overlay.py` and `pet_widget.py`.
5. Get a placeholder GIF (Aseprite quick sketch, or AI-generated, or any free sprite) and confirm overlay can render it.
6. Build whisper system end-to-end with library YAML.
7. Build ritual flow end-to-end with one hardcoded deck.
8. Run Phase 1 verify checklist.
