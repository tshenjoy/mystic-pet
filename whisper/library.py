"""Whisper library: load YAML files of pre-written one-liners."""

from __future__ import annotations

import random
from pathlib import Path

import yaml

_DEFAULT_DIR = Path(__file__).parent / "lines"


class WhisperLibrary:
    def __init__(self, lines_dir: Path = _DEFAULT_DIR, categories: list[str] | None = None) -> None:
        self.lines_dir = Path(lines_dir)
        self._by_category: dict[str, list[str]] = {}
        self._load(categories)

    def _load(self, categories: list[str] | None) -> None:
        for path in sorted(self.lines_dir.glob("*.yaml")):
            name = path.stem
            if categories and name not in categories:
                continue
            with open(path) as f:
                data = yaml.safe_load(f) or []
            self._by_category[name] = [str(line) for line in data]

    @property
    def categories(self) -> list[str]:
        return list(self._by_category.keys())

    def random(self, category: str | None = None) -> str:
        if category and category in self._by_category:
            pool = self._by_category[category]
        else:
            pool = [line for lines in self._by_category.values() for line in lines]
        if not pool:
            return "..."
        return random.choice(pool)
