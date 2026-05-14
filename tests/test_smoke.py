"""Import smoke test — confirms scaffold modules at least load."""


def test_imports():
    from config import settings  # noqa: F401
    from pet import overlay, pet_widget, sprite_renderer, state_machine  # noqa: F401
    from whisper import library, scheduler  # noqa: F401
    from ritual import ceremony_window, deck, reader  # noqa: F401
    from llm import client  # noqa: F401
    from persistence import db, reading_log  # noqa: F401
    from platform_adapter import get_backend  # noqa: F401
