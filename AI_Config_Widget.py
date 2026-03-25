from typing import Callable, Literal
from Game_State import GameState

from PyQt6.QtWidgets import QFormLayout, QLabel, QRadioButton, QVBoxLayout, QWidget

class AlgorithmSelectionWidget(QWidget):
    """Subwidget (form) for algorithm selection"""
    def __init__(
        self,
        doConfigurateAi: Callable[
            [Literal["minmax", "alphabeta"]],
            None
        ],
        gameStateChangeSubscriber: Callable[
            [
                Callable[..., None],
                Literal["SendValue", "Execute"]
            ],
            None
        ],
    ):
        super().__init__()

        self._doConfigurateAi = doConfigurateAi
        self._gameStateChangeSubscriber = gameStateChangeSubscriber

        self.layout = QFormLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.algorithmLabel = QLabel("Izvēlieties algoritmu:")
        self.layout.addRow(self.algorithmLabel)

        self.radioMinMax = QRadioButton("Mini-Makss")
        self.radioMinMax.clicked.connect(self.__setMinMax)
        self.layout.addRow(self.radioMinMax)
        self.radioMinMax.click()

        self.radioAlphaBeta = QRadioButton("Alfa-Beta")
        self.radioAlphaBeta.clicked.connect(self.__setAlphaBeta)
        self.layout.addRow(self.radioAlphaBeta)

        self._gameStateChangeSubscriber(self._updateAvailability, "SendValue")

    def _updateAvailability(self, isActive: bool) -> None:
        """Updates availability of widget.
        
        :param bool isActive:
        Is responsible for widget availability when game activates and disactivates.
        If true (=> game is active), inputs are static."""

        self.radioMinMax.setDisabled(isActive)
        self.radioAlphaBeta.setDisabled(isActive)

    def __setMinMax(self):
        self._doConfigurateAi('minmax')

    def __setAlphaBeta(self):
        self._doConfigurateAi('alphabeta')

class FirstPlayerSelectionWidget(QWidget):
    """Subwidget (form) for first player selection"""
    def __init__(
        self,
        startingPlayerSetter: Callable[[Literal[0, 1]], None]
    ):
        super().__init__()

        self._startingPlayerSetter = startingPlayerSetter

        self.layout = QFormLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.firstPlayerLabel = QLabel("Pirmais soli veiks...")
        self.layout.addRow(self.firstPlayerLabel)

        self.radioHumanFirst = QRadioButton("Jūs")
        self.radioHumanFirst.clicked.connect(self.__setHumanFirst)
        self.layout.addRow(self.radioHumanFirst)
        self.radioHumanFirst.click()

        self.radioAiFirst = QRadioButton("MI")
        self.radioAiFirst.clicked.connect(self.__setAiFirst)
        self.layout.addRow(self.radioAiFirst)

    def __setHumanFirst(self):
        self._startingPlayerSetter(0)

    def __setAiFirst(self):
        self._startingPlayerSetter(1)


class AIcfgWidget(QWidget):
    """Widget for user preconfiguration for AI"""
    def __init__(
            self,
            doConfigurateAi: Callable[
                [Literal["minmax", "alphabeta"]],
                None
            ],
            gameStateChangeSubscriber: Callable[
                [
                    Callable[..., None],
                    Literal["SendValue", "Execute"]
                ],
                None
            ],
            startingPlayerSetter: Callable[[Literal[0, 1]], None]
        ):
        super().__init__()

        self._doConfigurateAi = doConfigurateAi
        self._gameStateChangeSubscriber = gameStateChangeSubscriber
        self._startingPlayerSetter = startingPlayerSetter

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.algorithmSelection = AlgorithmSelectionWidget(self._doConfigurateAi, self._gameStateChangeSubscriber)
        self.layout.addWidget(self.algorithmSelection)

        self.firstPlayerSelection = FirstPlayerSelectionWidget(self._startingPlayerSetter)
        self.layout.addWidget(self.firstPlayerSelection)

        self.aiAwaitTimePrefixText = "MI izvēlēi veltīja "
        self.aiAwaitTimePostfixText = "ms"
        self.aiAwaitTime = QLabel("")
        self.layout.addWidget(self.aiAwaitTime)