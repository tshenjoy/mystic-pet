# Changelog

## [Unreleased]

### Fixed
- **macOS Focus Stealing (Issue #3)**: The app no longer becomes the active application when running on macOS
  - Set `NSApplicationActivationPolicyAccessory` to prevent app from appearing in Dock or menu bar
  - Added native macOS window configuration to ignore mouse events and prevent window activation
  - Window now uses `setIgnoresMouseEvents_(True)` and `setCanBecomeKeyWindow_(False)`
  - Added Stage Manager compatibility with `NSWindowCollectionBehaviorCanJoinAllSpaces`
  - Changed from fullscreen overlay to cat-sized window to prevent interfering with other apps
  - Added delayed show with previous app re-activation to avoid focus stealing
  - Fixed CGEventTap coordinate conversion (macOS uses bottom-left origin)

- **Window Tracking Coordinate Fix (Issue #1)**: Fixed cat positioning relative to active window
  - **Final fix**: kCGWindowBounds.Y is already in **top-left coordinates** (not bottom-left as Apple docs suggest)
  - Simplified formula: `top = y` (use directly without screen_h conversion)
  - This fixes the issue where cat moved in opposite direction when window was moved
  - Cat now correctly sits on top of the active window border

- **Animation Direction Sync (Issue #2)**: Fixed animation direction flip timing
  - Moved direction flip BEFORE `cat.update()` call to prevent 1-frame desync
  - Cat animation now correctly faces the direction of movement

### Changed
- Switched from `BypassWindowManagerHint` to native macOS window management
- Overlay window now only covers the cat (not fullscreen) to improve compatibility
- Window tracker now uses simplified Quartz method (removed complex AX API)
- Added `NSFloatingWindowLevel` for proper window layering on macOS

### Technical Details
- **Files Modified**:
  - `main.py`: Added `NSApplicationActivationPolicyAccessory` setup
  - `pet/overlay.py`: Rewrote macOS window handling, click detection, and coordinate conversion
  - `pet/window_tracker.py`: Simplified to use direct Y value as top coordinate
  - `pet/pet_widget.py`: Fixed direction flip timing in update loop

- **Key Insight**: Testing revealed that `kCGWindowBounds.Y` is already in top-left coordinates on this system, contrary to Apple's documentation. The simplified formula `top = y` works correctly.
