from whisper.library import WhisperLibrary


def test_library_loads():
    lib = WhisperLibrary()
    assert lib.categories, "expected at least one category yaml"


def test_random_returns_string():
    lib = WhisperLibrary()
    line = lib.random()
    assert isinstance(line, str) and line


def test_random_by_category():
    lib = WhisperLibrary()
    cat = lib.categories[0]
    line = lib.random(cat)
    assert isinstance(line, str) and line
