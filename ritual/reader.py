"""Reader: build a tarot prompt and call the LLM for the reading."""

from __future__ import annotations

from pathlib import Path

from llm.client import LLMClient
from ritual.deck import DrawnCard

_PROMPT_DIR = Path(__file__).parent.parent / "llm" / "prompts"


class Reader:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm
        with open(_PROMPT_DIR / "reading_system.txt") as f:
            self.system_prompt = f.read()

    def read(self, question: str, drawn: list[DrawnCard]) -> str:
        cards_text = "\n".join(
            f"- {dc.card.name} ({dc.orientation}): {dc.meaning}"
            for dc in drawn
        )
        user_prompt = (
            f"Question: {question.strip() or '(no question — open reading)'}\n\n"
            f"Cards drawn:\n{cards_text}\n\n"
            "Give a short reading in your voice (≤120 words)."
        )
        try:
            return self.llm.complete(self.system_prompt, user_prompt)
        except Exception as e:
            return self._fallback(drawn, error=str(e))

    @staticmethod
    def _fallback(drawn: list[DrawnCard], error: str = "") -> str:
        lines = ["the cards are loud today, but my voice is small."]
        for dc in drawn:
            lines.append(f"  {dc.card.name} ({dc.orientation}): {dc.meaning}.")
        lines.append("sit with them. I will speak again later.")
        return "\n".join(lines)
