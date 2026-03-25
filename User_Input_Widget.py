from typing import Any, Callable, Literal

from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout

from Game_State import GameState

class UserInputWidget(QWidget):
    """Widget for user as himself playing flow"""

    def __init__(
            self,
            doUserAction: Callable[
                [
                    Literal[
                        "TAKE1", "TAKE2",
                        "TAKE3", "TAKE4",
                        "SPLIT2", "SPLIT4"
                    ]
                ],
                None
            ],
            getTurn: Callable[[], bool],
            gameStateChangeSubscriber: Callable[
                [
                    Callable[..., Any],
                    Literal["SendValue", "Execute"]
                ], None
            ],
            getGameState: Callable[[], GameState]
        ):
        """:param Callable[Literal[\
            "TAKE1",\
            "TAKE2",\
            "TAKE3",\
            "TAKE4",\
            "SPLIT2",\
            "SPLIT4"\
        ]], None] doUserAction:
        Function, that accepts one of 6 defined game action names,
        which player can use when it is his turn"""

        super().__init__()

        self._doUserAction = doUserAction
        self._getTurn = getTurn
        self._gameStateChangeSubscriber = gameStateChangeSubscriber
        self._getGameState = getGameState

        self.actionOptions = QGridLayout()
        self.setLayout(self.actionOptions)

        self.takeOne = QPushButton("Izgūt 1")
        self.takeOne.clicked.connect(self._takeOne)
        self.actionOptions.addWidget(self.takeOne, 0, 0)

        self.takeTwo = QPushButton("Izgūt 2")
        self.takeTwo.clicked.connect(self._takeTwo)
        self.actionOptions.addWidget(self.takeTwo, 0, 1)

        self.takeThree = QPushButton("Izgūt 3")
        self.takeThree.clicked.connect(self._takeThree)
        self.actionOptions.addWidget(self.takeThree, 0, 2)

        self.takeFour = QPushButton("Izgūt 4")
        self.takeFour.clicked.connect(self._takeFour)
        self.actionOptions.addWidget(self.takeFour, 0, 3)

        self.splitTwo = QPushButton("Sadalīt 2 → 1, 1")
        self.splitTwo.clicked.connect(self._splitTwo)
        self.actionOptions.addWidget(self.splitTwo, 1, 0, 1, 2)

        self.splitFour = QPushButton("Sadalīt 4 → 2, 2")
        self.splitFour.clicked.connect(self._splitFour)
        self.actionOptions.addWidget(self.splitFour, 1, 2, 1, 2)

        self._gameStateChangeSubscriber(self.updateAvailability, "SendValue")
        self._gameStateChangeSubscriber(self.refreshFromState, "Execute")
        self.refreshFromState()

    def updateAvailability(self, isActive: bool) -> None:
     
        self.refreshFromState()

    def refreshFromState(self) -> None:
        state = self._getGameState()
        counts = state.getStats()
        enabled = not state.is_finished and state.getTurn()

        self.takeOne.setEnabled(enabled and counts['1'] > 0)
        self.takeTwo.setEnabled(enabled and counts['2'] > 0)
        self.takeThree.setEnabled(enabled and counts['3'] > 0)
        self.takeFour.setEnabled(enabled and counts['4'] > 0)
        self.splitTwo.setEnabled(enabled and counts['2'] > 0)
        self.splitFour.setEnabled(enabled and counts['4'] > 0)

    def _takeOne(self):
        self._doUserAction("TAKE1")

    def _takeTwo(self):
        self._doUserAction("TAKE2")

    def _takeThree(self):
        self._doUserAction("TAKE3")

    def _takeFour(self):
        self._doUserAction("TAKE4")

    def _splitTwo(self):
        self._doUserAction("SPLIT2")

    def _splitFour(self):
        self._doUserAction("SPLIT4")
