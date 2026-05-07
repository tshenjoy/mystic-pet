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
  - Corrected Quartz coordinate conversion in `window_tracker.py`
  - `kCGWindowBounds` Y is now correctly interpreted as the **top** of the window (not bottom)
  - New formula: `top = screen_h - y - h` (was incorrectly `top = screen_h - (y + h)`)
  - This fixes the issue where cat moved in opposite direction when window was moved

- **Animation Direction Sync (Issue #2)**: Fixed animation direction flip timing
  - Moved direction flip BEFORE `cat.update()` call to prevent 1-frame desync
  - Cat animation now correctly faces the direction of movement

### Changed
- Switched from `BypassWindowManagerHint` to native macOS window management
- Overlay window now only covers the cat (not fullscreen) to improve compatibility
- Window tracker now consistently uses Quartz method for coordinate reporting
- Added `NSFloatingWindowLevel` for proper window layering on macOS

### Technical Details
- **Files Modified**:
  - `main.py`: Added `NSApplicationActivationPolicyAccessory` setup
  - `pet/overlay.py`: Rewrote macOS window handling, click detection, and coordinate conversion
  - `pet/window_tracker.py`: Fixed Quartz coordinate conversion for window bounds
  - `pet/pet_widget.py`: Fixed direction flip timing in update loop

- **Key Insight**: macOS Quartz coordinate system has origin at bottom-left, while the app uses top-left coordinates. The `kCGWindowBounds` Y value represents the **top** of the window in Quartz coordinates, not the bottom as previously assumed.
