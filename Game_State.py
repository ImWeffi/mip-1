from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class GameState:
    """Frontend-friendly game state container."""

    sequence: tuple[int, ...] = field(default_factory=tuple)
    user_score: int = 0
    ai_score: int = 0
    user_turn: bool = True
    algorithm: Literal["minmax", "alphabeta"] | None = None
    is_finished: bool = False
    winner_text: str = ""
    userWins: int = 0
    aiWins: int = 0

    def getNumberRow(self) -> str:
        """Returns game number row."""
        if not self.sequence:
            return "∅"
        ordered = sorted(self.sequence)
        return " ".join(str(value) for value in ordered)

    def getStats(self) -> dict[Literal['1', '2', '3', '4', 'U', 'A', 'Uw', 'Aw'], int]:
        """Returns game statistics. `1`, `2`, `3` and `4` stands for the number count in the row,
        `U` for user score, `A` for AI score."""
        return {
            '1': self.sequence.count(1),
            '2': self.sequence.count(2),
            '3': self.sequence.count(3),
            '4': self.sequence.count(4),
            'U': self.user_score,
            'A': self.ai_score,
            'Uw': self.userWins,
            'Aw': self.aiWins,
        }

    def getTurn(self) -> bool:
        """Returns boolean. If true -> it is user turn now, otherwise it is AI turn."""
        return self.user_turn

    def incrementHumanWins(self) -> None:
        self.userWins += 1

    def incrementAiWins(self) -> None:
        self.AiWins += 1