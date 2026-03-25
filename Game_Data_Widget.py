from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QFrame
from PyQt6.QtCore import Qt
from Game_State import GameState

from typing import Any, Callable, Literal


class ScoreWidget(QWidget):
    """Play side score widget"""

    def __init__(self, isAlignedToLeft: bool):
        super().__init__()

        self.isAlignedToLeft = isAlignedToLeft

        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Shape.Box)
        self.frame.setFrameShadow(QFrame.Shadow.Plain)
        self.frame.setLineWidth(2)

        self.layout = QVBoxLayout(self.frame)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self._score = 0
        self.text = QLabel(str(self._score))
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.text)

        self.setFixedSize(45, 45)

        if self.isAlignedToLeft:
            self.setToolTip("Jūsu punkti")
            self.setStyleSheet("background-color: #f5425a;border-radius: 2px;color: white;font-weight: bold")
        else:
            self.setToolTip("MI punkti")
            self.setStyleSheet("background-color: #4293f5;border-radius: 2px;color: white;font-weight: bold")

    def updateValue(self, newValue: int):
        self._score = newValue
        self.text.setText(str(newValue))


class ScoreWrapperWidget(QWidget):
    """Both user and AI score wrapper"""

    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 10)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)

        self.userScore = ScoreWidget(True)
        self.layout.addWidget(self.userScore)

        self.aiScore = ScoreWidget(False)
        self.layout.addWidget(self.aiScore)

    def updateScore(self, newValue: int, toUser: bool):
        if toUser:
            self.userScore.updateValue(newValue)
        else:
            self.aiScore.updateValue(newValue)


class NumeralCounter(QWidget):
    """Vertical widget that shows count of numerals in the game row"""

    def __init__(
        self,
        gameStateGetter: Callable[[], GameState],
    ):
        super().__init__()

        self._gameStateGetter = gameStateGetter

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)

        self.ones = QLabel("Vieninieku: 0")
        self.layout.addWidget(self.ones)

        self.twoes = QLabel("Divnieku: 0")
        self.layout.addWidget(self.twoes)

        self.threes = QLabel("Trijnieku: 0")
        self.layout.addWidget(self.threes)

        self.fours = QLabel("Četrinieku: 0")
        self.layout.addWidget(self.fours)

    def countUpdater(self):
        self.ones.setText( f"Vieninieku: {self._gameStateGetter().getStats()['1']}")
        self.twoes.setText(  f"Divnieku: {self._gameStateGetter().getStats()['2']}")
        self.threes.setText(f"Trijnieku: {self._gameStateGetter().getStats()['3']}")
        self.fours.setText(f"Četrinieku: {self._gameStateGetter().getStats()['4']}")


class WinsCounter(QWidget):
    """Vertical widget that shows count of total wins per player"""

    def __init__(
        self,
        gameStateGetter: Callable[[], GameState],
    ):
        super().__init__()

        self._gameStateGetter = gameStateGetter

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)

        self.humanWins = QLabel("Jūsu uzvaru: 0")
        self.layout.addWidget(self.humanWins)

        self.aiWins = QLabel("MI uzvaru: 0")
        self.layout.addWidget(self.aiWins)

    def countUpdater(self):
        self.humanWins.setText(f"Jūsu uzvaru: {self._gameStateGetter().getStats()['Uw']}")
        self.aiWins.setText(f"MI uzvaru: {self._gameStateGetter().getStats()['Aw']}")


class StatisticsWidget(QWidget):
    """Horizontal widget to display both players scores, game sessions statistics and total win counts."""

    def __init__(
        self,
        gameStateGetter: Callable[[], GameState],
        gameStateChangeSubscriber:  Callable[[Callable[..., Any], Literal["SendValue", "Execute"]], None]
    ):
        super().__init__()

        self._gameStateGetter = gameStateGetter
        self._gameStateChangeSubscriber = gameStateChangeSubscriber

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.score = ScoreWrapperWidget()
        self.layout.addWidget(self.score)

        self.winsCounter = WinsCounter(self._gameStateGetter)
        self.layout.addWidget(self.winsCounter)

        self.numeralCounter = NumeralCounter(self._gameStateGetter)
        self.layout.addWidget(self.numeralCounter)

        self._gameStateChangeSubscriber(self.winsCounter.countUpdater, 'Execute')
        self._gameStateChangeSubscriber(self.numeralCounter.countUpdater, 'Execute')

    def updateScore(self, newValue: int, toUser: bool):
        self.score.updateScore(newValue, toUser)


class UniversalFieldWidget(QWidget):
    """Universal field to show game number row status"""

    def __init__(
            self,
            getNumberRow:           Callable[[], str],
            setNumberRowBaseLength: Callable[[int], None],
            getNumberRowBaseLength: Callable[[], int]
        ):
        super().__init__()

        self._getNumberRow = getNumberRow
        self._setNumberRowBaseLength = setNumberRowBaseLength
        self._getNumberRowBaseLength = getNumberRowBaseLength

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.minusButton = QPushButton()
        self.minusButton.setText("-")
        self.minusButton.clicked.connect(self._denominateNumberRowBaseLength)
        self.minusButton.setDisabled(True) # bcs by default base length is minimal
        self.layout.addWidget(self.minusButton)

        self.universalField = QLineEdit()
        self.value: str = "Universal field"
        self.universalField.setText(self.value)
        self.universalField.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.universalField.setDisabled(True)
        self.universalField.setToolTip(
            self.updateNumberRowLengthText.__doc__.replace("  ", "")
            + "\n" +
            self.updateNumberRow.__doc__.replace("  ", "")
        )
        self.universalField.setStyleSheet("width: 100%")
        self.layout.addWidget(self.universalField)

        self.plusButton = QPushButton()
        self.plusButton.setText("+")
        self.plusButton.clicked.connect(self._incrementNumberRowBaseLength)
        self.layout.addWidget(self.plusButton)

    def enableGameMode(self):
        """Disables side-button click actions"""

        self.plusButton.setDisabled(True)
        self.minusButton.setDisabled(True)

    def disableGameMode(self):
        """Enables side-button click actions"""

        self.plusButton.setDisabled(False)
        self.minusButton.setDisabled(False)

    def _tryUpdateNumberRowBaseLength(self, newLength: int) -> bool:
        if newLength in range(15, 20+1):
            self._setNumberRowBaseLength(newLength)
            return True
        return False

    def _incrementNumberRowBaseLength(self):
        sucessfulUpdate = self._tryUpdateNumberRowBaseLength(self._getNumberRowBaseLength() + 1)
        self.updateNumberRowLengthText(self._getNumberRowBaseLength())
        if self._getNumberRowBaseLength() == 20:
            self.plusButton.setDisabled(True)
        self.minusButton.setDisabled(False)

    def _denominateNumberRowBaseLength(self):
        self._tryUpdateNumberRowBaseLength(self._getNumberRowBaseLength() - 1)
        self.updateNumberRowLengthText(self._getNumberRowBaseLength())
        if self._getNumberRowBaseLength() == 15:
            self.minusButton.setDisabled(True)
        self.plusButton.setDisabled(False)

    def updateNumberRowLengthText(self, length: int):
        """Before game started, universal field being used as status about
        number row to be generated. While game is not started, it contains
        text about number row length."""

        self.universalField.setText(f"Virknes garums: {length} cipari")

    def updateNumberRow(self):
        """After game is started, universal field must contain sequnece of
        numbers from 1 to 4 that is gameplay subject."""
        self.universalField.setText(self._getNumberRow())


class GameDataWidget(QWidget):
    """Widget for game data / statistics visualisation"""

    def __init__(self,
            gameStateGetter:            Callable[[                                                   ], GameState],
            gameStateChanger:           Callable[[                                                   ], None],
            algorithmChangeSubscriber:  Callable[[Callable[..., Any], Literal["SendValue", "Execute"]], None],
            gameStateChangeSubscriber:  Callable[[Callable[..., Any], Literal["SendValue", "Execute"]], None],
            setNumberRowBaseLength:     Callable[[int                                                ], None],
            getNumberRowBaseLength:     Callable[[                                                   ], int]
        ):
        super().__init__()

        self._gameStateGetter = gameStateGetter
        self._gameStateChanger = gameStateChanger
        self._algorithmChangeSubscriber = algorithmChangeSubscriber
        self._gameStateChangeSubscriber = gameStateChangeSubscriber
        self._setNumberRowBaseLength = setNumberRowBaseLength
        self._getNumberRowBaseLength = getNumberRowBaseLength

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.statisticsWidget = StatisticsWidget(
            self._gameStateGetter,
            self._gameStateChangeSubscriber
        )
        self.layout.addWidget(self.statisticsWidget)

        self.universalField = UniversalFieldWidget(
            self._getNumberRow,
            self._setNumberRowBaseLength,
            self._getNumberRowBaseLength
        )
        self.layout.addWidget(self.universalField)

        self.statusLabel = QLabel("")
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.statusLabel)

        self.playButton = QPushButton()
        self.playButton.setText("Lūdzu, izvēlieties MI algoritmu")
        self.playButton.setDisabled(True)
        self.playButton.clicked.connect(self._gameStateChanger)
        self.layout.addWidget(self.playButton)

        self._algorithmChangeSubscriber(self._setPlayText, "Execute")
        self._algorithmChangeSubscriber(self._updateNumberRowLengthTextInUF, "Execute")
        self._gameStateChangeSubscriber(self._widgetEnabler, "SendValue")
        self._gameStateChangeSubscriber(self.refreshFromState, "Execute")
        self._updateNumberRowLengthTextInUF()
        self.refreshFromState()

    def _widgetEnabler(self, isActive: bool):
        """Enables or disables widget elements depending on game state"""

        if isActive:
            self.universalField.enableGameMode()
            self.playButton.setDisabled(True)
        else:
            self.universalField.disableGameMode()
            self.playButton.setDisabled(False)

    def _updateNumberRowLengthTextInUF(self):
        """Before game started, universal field being used as status about
        number row to be generated. While game is not started, it contains
        text about number row length."""

        self.universalField.updateNumberRowLengthText(self._getNumberRowBaseLength())

    def _getNumberRow(self) -> str:
        return self._gameStateGetter().getNumberRow()

    def _setPlayText(self) -> None:
        """Set text "Play!" to main button"""
        
        self.playButton.setText("Spēlēt!")
        self.playButton.setDisabled(False)

    def refreshFromState(self) -> None:
        state = self._gameStateGetter()
        self.statisticsWidget.updateScore(state.user_score, True)
        self.statisticsWidget.updateScore(state.ai_score, False)
        if state.sequence:
            self.universalField.updateNumberRow()
        else:
            self._updateNumberRowLengthTextInUF()

        if state.is_finished:
            self.statusLabel.setText(state.winner_text or "Spēle beidzās!")
            self.playButton.setText("Sākt jaunu spēli!")
            self.playButton.setDisabled(False)
        elif state.sequence:
            self.statusLabel.setText(f"Tagad ir {'jūsu' if state.getTurn() else 'MI'} gaita")
        else:
            self.statusLabel.setText("")
