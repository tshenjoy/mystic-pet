"""Platform adapter: returns the OS-specific backend.

Each backend implements the same surface (see linux.py for the interface).
Linux is the primary target during MVP. macOS and Windows are stubs.
"""

import sys


def get_backend():
    if sys.platform.startswith("linux"):
        from platform_adapter import linux
        return linux
    if sys.platform == "darwin":
        from platform_adapter import macos
        return macos
    if sys.platform.startswith("win"):
        from platform_adapter import windows
        return windows
    raise RuntimeError(f"unsupported platform: {sys.platform}")
