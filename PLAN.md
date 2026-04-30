# Desktop Pet Cat — Project Plan

## Overview

Windows desktop pet app. A cat walks on top of active windows, stalks, plays with trash can, chases mouse cursor. Users upload a single photo of their cat to customize appearance.

## Target Platform
- **Deploy:** Windows 10/11
- **Develop:** Linux (sync to Windows for visual testing + packaging)
- Python 3.10+

## Development Workflow

```
Linux (dev machine)                    Windows (test machine)
───────────────────                    ─────────────────────
Edit code                             
Write unit tests                       
  (state machine, color               
   extraction, sprite gen —            
   all platform-independent)           
         │                             
         └── git push ───────────────► git pull
                                            │
                                       python main.py  (visual test)
                                            │
                                       Iterate until good
                                            │
                                       PyInstaller → .exe (release)
```

### What Can Be Tested on Linux
- State machine logic (pure Python, no Win32)
- Image processing pipeline (face detect, color extract, sprite gen)
- Sprite rendering in isolation (PyQt6 works on Linux)
- Unit tests for all non-Win32 modules

### What Requires Windows
- Window tracking (`pywin32` — Win32 API only)
- Overlay positioning on active windows
- System tray behavior
- Final .exe packaging
- Full integration testing

### Sync Method
Git repo. Push from Linux, pull on Windows. Simple.

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| GUI / Overlay | **PyQt6** | Transparent frameless windows, good sprite rendering, system tray support built-in. Works on Linux too for partial testing |
| Window Tracking | **pywin32** (`win32gui`, `win32api`) | Access Win32 API for active window position, size, move/resize events |
| Image Processing | **Pillow (PIL)** | Face crop, color extraction, sprite recoloring, compositing — lightweight, no ML dependency |
| Face Detection | **OpenCV** (`cv2`) with Haar cascades | Detect cat face region from uploaded photo. Haar cascade for cats exists (`haarcascade_frontalcatface.xml`) |
| Color Extraction | **Pillow + sklearn** (KMeans) | Extract dominant fur colors from photo |
| Packaging | **PyInstaller** (Windows only) | Single .exe distribution |
| Animation Engine | Custom (built on QTimer + QPixmap) | Simple state machine, frame-based sprite rendering |

## Architecture

```
desktop-pet/
├── main.py                  # Entry point, system tray setup
├── pet/
│   ├── __init__.py
│   ├── window.py            # Transparent overlay window (PyQt6)
│   ├── pet_widget.py        # Cat sprite rendering + animation
│   ├── state_machine.py     # Animation state machine
│   ├── window_tracker.py    # Track active window position/size
│   └── cursor_tracker.py    # Track mouse cursor for chase behavior
├── customization/
│   ├── __init__.py
│   ├── importer.py          # Upload flow: face detect → color extract → generate sprites
│   ├── face_detector.py     # Cat face detection + crop
│   ├── color_extractor.py   # Dominant color extraction from fur
│   └── sprite_generator.py  # Recolor template + composite face → output sprite sheet
├── assets/
│   ├── template/            # Default cat sprite sheets (all animations)
│   │   ├── walk/            # walk_01.png ... walk_08.png
│   │   ├── stalk/           # stalk_01.png ... stalk_06.png
│   │   ├── trash_can/       # trash_01.png ... trash_10.png
│   │   ├── chase/           # chase_01.png ... chase_06.png
│   │   └── idle/            # idle_01.png ... idle_04.png
│   ├── objects/             # Trash can sprite, other interactables
│   └── metadata.json        # Per-frame anchor points (head_x, head_y, head_angle, head_scale)
├── config/
│   ├── settings.py          # User preferences (speed, size, behavior toggles)
│   └── defaults.json        # Default config values
├── cache/                   # Generated custom sprite sheets stored here
├── requirements.txt
└── README.md
```

## Core Features (v1)

### 1. Window Border Walking
- Track currently active (foreground) window via `GetForegroundWindow()`
- Poll window rect every ~100ms (or use `SetWinEventHook` via ctypes)
- Cat sprite walks left/right along top edge of active window
- Handle edge cases: window moves, resizes, minimizes, closes
- Cat transitions to new window when active window changes

### 2. Predefined Animations
| Animation | Trigger | Behavior |
|-----------|---------|----------|
| **Walk** | Default | Walks back and forth on window top border |
| **Stalk** | Random timer | Crouches low, slow creep, butt wiggle, pounce |
| **Trash Can** | Random timer | Trash can appears, cat bats at it, knocks it over |
| **Chase Cursor** | Cursor near cat | Cat runs toward mouse cursor, paws at it |
| **Idle** | After walk | Sits, looks around (transition state between actions) |

### 3. State Machine
```
                    ┌──────────┐
              ┌────►│   IDLE   │◄────┐
              │     └──┬───┬───┘     │
              │        │   │         │
         done │   random  cursor    │ done
              │   timer   nearby    │
              │        │   │         │
        ┌─────┴──┐  ┌──▼───▼──┐  ┌──┴──────┐
        │  WALK  │  │  STALK  │  │  CHASE  │
        └────────┘  └─────────┘  └─────────┘
              │
         random timer
              │
        ┌─────▼────┐
        │ TRASH CAN│
        └──────────┘
```

### 4. Custom Cat Image Upload
**One-time processing pipeline at import:**

```
User selects cat photo
       │
       ▼
  ┌─────────────────┐
  │ Detect cat face  │  ← OpenCV Haar cascade (frontalcatface)
  │ region + crop    │
  └────────┬────────┘
           ▼
  ┌─────────────────┐
  │ Extract dominant │  ← KMeans on non-face body pixels
  │ fur colors (3-5) │
  └────────┬────────┘
           ▼
  ┌─────────────────┐
  │ Recolor template │  ← HSL shift template sprites to match fur colors
  │ body sprites     │
  └────────┬────────┘
           ▼
  ┌─────────────────┐
  │ Composite face   │  ← Paste cropped face at head anchor per frame
  │ onto each frame  │    (using metadata.json: x, y, angle, scale)
  └────────┬────────┘
           ▼
  Cache generated sprite sheet in cache/
```

### 5. System Tray
- Right-click menu:
  - Upload Cat Photo
  - Reset to Default Cat
  - Settings (speed, size)
  - Exit
- Left-click: toggle pet visibility

## Implementation Phases

### Phase 1: Skeleton (days 1-3)
- [ ] PyQt6 transparent overlay window
- [ ] Basic sprite rendering with QTimer animation loop
- [ ] Window tracking (active window position)
- [ ] Cat walks on top border of active window

### Phase 2: Animations (days 4-7)
- [ ] State machine implementation
- [ ] Walk animation (left/right patrol)
- [ ] Stalk animation (random trigger)
- [ ] Trash can interaction
- [ ] Chase cursor behavior
- [ ] Idle transitions

### Phase 3: Customization (days 8-12)
- [ ] Cat face detection from uploaded photo
- [ ] Dominant color extraction
- [ ] Template sprite recoloring
- [ ] Face compositing per frame
- [ ] Upload UI via system tray

### Phase 4: Polish (days 13-16)
- [ ] System tray with full menu
- [ ] Settings persistence
- [ ] Handle edge cases (multi-monitor, fullscreen, taskbar)
- [ ] PyInstaller packaging
- [ ] Template sprite art (or placeholder art)

## Sprite Template Requirements

Each animation needs a sprite sheet with per-frame metadata:

```json
{
  "walk": {
    "frames": 8,
    "fps": 10,
    "anchors": [
      {"head_x": 45, "head_y": 12, "head_angle": 0, "head_scale": 1.0},
      ...
    ]
  },
  "stalk": { ... },
  "trash_can": { ... },
  "chase": { ... },
  "idle": { ... }
}
```

**Anchor points** define where the user's cat face gets composited onto each frame. These are hand-authored once for the template.

## Dependencies

```
# Core (both platforms)
PyQt6>=6.5
Pillow>=10.0
opencv-python>=4.8
scikit-learn>=1.3
numpy>=1.24

# Windows only
pywin32>=306          # conditional install, Windows only

# Packaging (Windows only)
pyinstaller>=6.0
```

### Setup Commands

**Linux (dev):**
```bash
pip install PyQt6 Pillow opencv-python scikit-learn numpy pytest
```

**Windows (test + package):**
```bash
pip install PyQt6 Pillow opencv-python scikit-learn numpy pywin32 pyinstaller
```

## Conditional Import Pattern

```python
# pet/window_tracker.py
import sys

if sys.platform == "win32":
    import win32gui
    import win32api
else:
    win32gui = None  # Linux: module not available, skip window tracking
```

This prevents import errors on Linux. Win32-dependent features simply won't run during Linux-side testing. All other modules (state machine, image pipeline, sprite rendering) work cross-platform.

## Open Items / Risks

1. **Sprite art** — Need template cat sprites for all animations. Options: commission pixel art, use free assets, or draw simple ones
2. **Cat face detection accuracy** — Haar cascade for cats is decent but not perfect. May need fallback manual crop UI
3. **Performance on older machines** — 100ms polling + transparent window + sprite rendering. Profile early
4. **Multi-monitor DPI** — Different scaling per monitor can offset pet position. Handle in Phase 4
5. **Linux dev limitation** — Cannot test window tracking or overlay positioning on Linux. Must sync to Windows for those. Keep Win32 code isolated to minimize round-trips
