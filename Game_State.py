from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class GameState:

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
        if not self.sequence:
            return "∅"
        ordered = sorted(self.sequence)
        return " ".join(str(value) for value in ordered)

    def getStats(self) -> dict[Literal['1', '2', '3', '4', 'U', 'A', 'Uw', 'Aw'], int]:
    
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

        return self.user_turn

    def incrementHumanWins(self) -> None:
        self.userWins += 1

    def incrementAiWins(self) -> None:
        self.aiWins += 1