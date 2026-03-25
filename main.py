from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Literal, Optional

from PyQt6.QtCore import QSize, QTimer
from PyQt6.QtWidgets import QApplication, QGridLayout, QMessageBox, QWidget

from User_Input_Widget import UserInputWidget
from Game_Data_Widget import GameDataWidget
from AI_Config_Widget import AIcfgWidget
from Game_State import GameState


@dataclass(frozen=True)
class Action:
    """Producable action for the game"""
    action_type: Literal["take", "split2", "split4"]
    index: int


@dataclass(frozen=True)
class SolverState:
    sequence: tuple[int, ...]
    scores: tuple[int, int]   # (user, ai)
    current_player: int       # 0 user, 1 ai

    def is_terminal(self) -> bool:
        return len(self.sequence) == 0


class NumberSequenceGame:
    def __init__(self, max_depth: int = 6):
        self.max_depth = max_depth

    def initial_state(self, baseLength: int, starting_player: int) -> SolverState:
        sequence = tuple(random.randint(1, 4) for _ in range(baseLength))
        return SolverState(
            sequence=sequence,
            scores=(0, 0),
            current_player=starting_player
        )

    def get_legal_actions(self, state: SolverState) -> List[Action]:
        actions: List[Action] = []

        for i, value in enumerate(state.sequence):
            actions.append(Action("take", i))

            if value == 2:
                actions.append(Action("split2", i))
            elif value == 4:
                actions.append(Action("split4", i))

        return actions

    def apply_action(self, state: SolverState, action: Action) -> SolverState:
        seq = list(state.sequence)
        scores = list(state.scores)
        player = state.current_player

        if action.index < 0 or action.index >= len(seq):
            raise ValueError("Nederīgs indekss.")

        value = seq[action.index]

        if action.action_type == "take":
            scores[player] += value
            del seq[action.index]

        elif action.action_type == "split2":
            if value != 2:
                raise ValueError("\"split2\" drīkst izmantot tikai skaitlim 2.")
            seq[action.index:action.index + 1] = [1, 1]

        elif action.action_type == "split4":
            if value != 4:
                raise ValueError("\"split4\" drīkst izmantot tikai skaitlim 4.")
            scores[player] += 1
            seq[action.index:action.index + 1] = [2, 2]

        else:
            raise ValueError("Nezināms darbības tips.")

        return SolverState(
            sequence=tuple(seq),
            scores=(scores[0], scores[1]),
            current_player=1 - player
        )

    def evaluate_terminal(self, state: SolverState, maximizing_player: int) -> int:
        return state.scores[maximizing_player] - state.scores[1 - maximizing_player]

    def heuristic(self, state: SolverState, maximizing_player: int) -> float:
        my_score = state.scores[maximizing_player]
        opp_score = state.scores[1 - maximizing_player]
        score_diff = my_score - opp_score

        seq = state.sequence
        count1 = seq.count(1)
        count2 = seq.count(2)
        count3 = seq.count(3)
        count4 = seq.count(4)

        material = count1 * 1.0 + count2 * 2.0 + count3 * 3.0 + count4 * 4.0
        split_potential = count4 * 0.6 + count2 * 0.2
        turn_bonus = 0.3 if state.current_player == maximizing_player else -0.3

        return score_diff * 10 + material * 0.15 + split_potential + turn_bonus

    def order_actions(self, state: SolverState, actions: List[Action]) -> List[Action]:
        def priority(action: Action) -> int:
            value = state.sequence[action.index]

            if action.action_type == "take":
                return 100 + value
            if action.action_type == "split4":
                return 80
            if action.action_type == "split2":
                return 50
            return 0

        return sorted(actions, key=priority, reverse=True)

    def minimax(
        self,
        state: SolverState,
        depth: int,
        maximizing_player: int
    ) -> tuple[float, Optional[Action]]:
        if state.is_terminal():
            return self.evaluate_terminal(state, maximizing_player), None

        if depth == 0:
            return self.heuristic(state, maximizing_player), None

        actions = self.order_actions(state, self.get_legal_actions(state))
        is_max_turn = state.current_player == maximizing_player

        best_action: Optional[Action] = None

        if is_max_turn:
            best_value = -math.inf
            for action in actions:
                next_state = self.apply_action(state, action)
                value, _ = self.minimax(next_state, depth - 1, maximizing_player)

                if value > best_value:
                    best_value = value
                    best_action = action

            return best_value, best_action

        best_value = math.inf
        for action in actions:
            next_state = self.apply_action(state, action)
            value, _ = self.minimax(next_state, depth - 1, maximizing_player)

            if value < best_value:
                best_value = value
                best_action = action

        return best_value, best_action

    def alphabeta(
        self,
        state: SolverState,
        depth: int,
        alpha: float,
        beta: float,
        maximizing_player: int
    ) -> tuple[float, Optional[Action]]:
        if state.is_terminal():
            return self.evaluate_terminal(state, maximizing_player), None

        if depth == 0:
            return self.heuristic(state, maximizing_player), None

        actions = self.order_actions(state, self.get_legal_actions(state))
        is_max_turn = state.current_player == maximizing_player
        best_action: Optional[Action] = None

        if is_max_turn:
            value = -math.inf
            for action in actions:
                next_state = self.apply_action(state, action)
                child_value, _ = self.alphabeta(
                    next_state, depth - 1, alpha, beta, maximizing_player
                )

                if child_value > value:
                    value = child_value
                    best_action = action

                alpha = max(alpha, value)
                if beta <= alpha:
                    break

            return value, best_action

        value = math.inf
        for action in actions:
            next_state = self.apply_action(state, action)
            child_value, _ = self.alphabeta(
                next_state, depth - 1, alpha, beta, maximizing_player
            )

            if child_value < value:
                value = child_value
                best_action = action

            beta = min(beta, value)
            if beta <= alpha:
                break

        return value, best_action

    def best_move(self, state: SolverState, algorithm: str = "alphabeta") -> Optional[Action]:
        maximizing_player = state.current_player
        algorithm = algorithm.lower()

        if algorithm == "minmax":
            _, action = self.minimax(state, depth=4, maximizing_player=maximizing_player)
        elif algorithm == "alphabeta":
            _, action = self.alphabeta(
                state, self.max_depth, -math.inf, math.inf, maximizing_player
            )
        else:
            raise ValueError("Algoritmam jābūt 'minmax' vai 'alphabeta'.")

        return action


class GameDispatcher:
    """Connector between frontend and backend"""

    def __init__(self):
        self.baseLength: int = 15

        self.isActive: bool = False
        self.activeStatusDependedFunctions: Dict[
            Callable[..., Any],
            Literal["SendValue", "Execute"]
        ] = {}

        self.algorithm: Literal['minmax', 'alphabeta'] | None
        self.algorithmDependedFunctions: Dict[
            Callable[..., Any],
            Literal["SendValue", "Execute"]
        ] = {}

        self.engine = NumberSequenceGame(max_depth=6)
        self.state = GameState()
        self.window: Optional[QWidget] = None
        self.startingPlayer: Literal[0, 1] = 0         # 0 -> Human; 1 -> AI
        self.humanWins: int = 0
        self.aiWins: int = 0

    def setStartingPlayer(self, int: Literal[0, 1]) -> None:
        self.startingPlayer = int

    def set_window(self, window: QWidget) -> None:
        self.window = window

    def algorithmChangeSubscriber(
        self,
        function: Callable[..., Any],
        activationRule: Literal["SendValue", "Execute"]
    ) -> None:
        """Saves function in dictionary to call it after AI algorithm change.
        
        :param Callable[..., Any] function:
        Function to be called after algorithm change

        :param Literal["SendValue", "Execute"] activationRule:
        Is responsible to send new game state value or not."""

        self.algorithmDependedFunctions[function] = activationRule

    def gameStateChangeSubscriber(
        self,
        function: Callable[..., Any],
        activationRule: Literal["SendValue", "Execute"]
    ) -> None:
        """Saves function in dictionary to call it after game state change.
        
        :param Callable[..., Any] function:
        Function to be called after game state change

        :param Literal["SendValue", "Execute"] activationRule:
        Is responsible to send new game state value or not."""

        self.activeStatusDependedFunctions[function] = activationRule

    def _notifyAlgorithmChange(self) -> None:
        for function, rule in self.algorithmDependedFunctions.items():
            function(self.algorithm) if rule == "SendValue" else function()

    def _notifyGameStateChange(self) -> None:
        for function, rule in self.activeStatusDependedFunctions.items():
            function(self.isActive) if rule == "SendValue" else function()

    def setNumberRowBaseLength(self, newLength: int) -> None:
        if not self.isActive:
            self.baseLength = newLength

    def getNumberRowBaseLength(self) -> int:
        return self.baseLength

    def _solverToView(self, solver_state: SolverState) -> GameState:
        return GameState(
            sequence=solver_state.sequence,
            user_score=solver_state.scores[0],
            ai_score=solver_state.scores[1],
            user_turn=(solver_state.current_player == 0),
            algorithm=self.algorithm,
            is_finished=(len(solver_state.sequence) == 0),
        )

    def _viewToSolver(self) -> SolverState:
        return SolverState(
            sequence=self.state.sequence,
            scores=(self.state.user_score, self.state.ai_score),
            current_player=0 if self.state.user_turn else 1,
        )

    def _finishGame(self) -> None:
        self.state.is_finished = True

        if self.state.user_score > self.state.ai_score:
            self.state.incrementHumanWins()
            self.state.winner_text = (
                f"Spēle beigusies. Jūs uzvarējāt, rezultāts ir {self.state.user_score}:{self.state.ai_score}."
            )
        elif self.state.ai_score > self.state.user_score:
            self.state.incrementAiWins()
            self.state.winner_text = (
                f"Spēle beigusies. Uzvarēja MI, rezultāts ir {self.state.user_score}:{self.state.ai_score}."
            )
        else:
            self.state.winner_text = (
                f"Spēle beigusies neizšķirti. Rezultāts ir {self.state.user_score}:{self.state.ai_score}."
            )

        self.isActive = False
        self._notifyGameStateChange()

        if self.window is not None:
            QMessageBox.information(self.window, "Spēle beidzās", self.state.winner_text)

    def _applySolverAction(self, action: Action) -> None:
        next_state = self.engine.apply_action(self._viewToSolver(), action)
        self.state = self._solverToView(next_state)

        if self.state.is_finished:
            self._finishGame()
        else:
            self._notifyGameStateChange()

    def _findFirstValueIndex(self, value: int) -> int:
        try:
            return self.state.sequence.index(value)
        except ValueError as exc:
            raise ValueError(f"Skaitlis {value} virknē nav pieejams.") from exc

    def doUserTurn(self, action: Literal["TAKE1", "TAKE2", "TAKE3", "TAKE4", "SPLIT2", "SPLIT4"]) -> None:
        """:param Literal[\
            "TAKE1",\
            "TAKE2",\
            "TAKE3",\
            "TAKE4",\
            "SPLIT2",\
            "SPLIT4"\
        ] action:
        Argument for one of 6 defined game action names,
        which player can use when it is his turn"""
        if not self.isActive or not self.state.user_turn or self.state.is_finished:
            return

        try:
            if action == "TAKE1":
                selected_action = Action("take", self._findFirstValueIndex(1))
            elif action == "TAKE2":
                selected_action = Action("take", self._findFirstValueIndex(2))
            elif action == "TAKE3":
                selected_action = Action("take", self._findFirstValueIndex(3))
            elif action == "TAKE4":
                selected_action = Action("take", self._findFirstValueIndex(4))
            elif action == "SPLIT2":
                selected_action = Action("split2", self._findFirstValueIndex(2))
            elif action == "SPLIT4":
                selected_action = Action("split4", self._findFirstValueIndex(4))
            else:
                return

            self._applySolverAction(selected_action)

        except ValueError:
            return

        if self.isActive and not self.state.user_turn and not self.state.is_finished:
            QTimer.singleShot(200, self._doAiTurn)

    def _doAiTurn(self) -> None:
        if not self.isActive or self.state.user_turn or self.state.is_finished:
            return

        solver_state = self._viewToSolver()
        ai_action = self.engine.best_move(solver_state, self.algorithm or "alphabeta")

        if ai_action is None:
            self._finishGame()
            return

        self._applySolverAction(ai_action)

    def doConfigurateAi(self, action: Literal["minmax", "alphabeta"]) -> None:
        """This function updates selected AI algorithm value and call functions,
        which was declared in `self.algorithmDependedFunctions` dict"""

        self.algorithm = action
        self._notifyAlgorithmChange()

    def getGameState(self) -> GameState:
        return self.state

    def changeActiveState(self) -> None:
        """This function reverts game active state and call functions,
        which was declared in `self.activeStatusDependedFunctions` dict"""
        if self.algorithm is None:
            return

        self.state = self._solverToView(
            self.engine.initial_state(self.baseLength, starting_player=self.startingPlayer)
        )
        self.state.algorithm = self.algorithm
        self.state.winner_text = ""
        self.state.is_finished = False
        self.isActive = True
        self._notifyGameStateChange()

    def getActiveState(self):
        return self.isActive


GAME_DISPATCHER = GameDispatcher()


class MainWindow(QWidget):
    """Application window"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("MIP-1")
        self.setMinimumSize(QSize(500, 400))

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        GAME_DISPATCHER.set_window(self)

        self.gameDataWidget = GameDataWidget(
            GAME_DISPATCHER.getGameState,
            GAME_DISPATCHER.changeActiveState,
            GAME_DISPATCHER.algorithmChangeSubscriber,
            GAME_DISPATCHER.gameStateChangeSubscriber,
            GAME_DISPATCHER.setNumberRowBaseLength,
            GAME_DISPATCHER.getNumberRowBaseLength
        )

        self.userInputWidget = UserInputWidget(
            GAME_DISPATCHER.doUserTurn,
            GAME_DISPATCHER.getGameState().getTurn,
            GAME_DISPATCHER.gameStateChangeSubscriber,
            GAME_DISPATCHER.getGameState
        )

        self.aiIoWidget = AIcfgWidget(
            GAME_DISPATCHER.doConfigurateAi,
            GAME_DISPATCHER.gameStateChangeSubscriber,
            GAME_DISPATCHER.setStartingPlayer
        )

        self.layout.addWidget(self.gameDataWidget, 0, 0, 1, 2)
        self.layout.addWidget(self.userInputWidget, 1, 0, 1, 1)
        self.layout.addWidget(self.aiIoWidget, 1, 1, 1, 1)


def main():
    app = QApplication(sys.argv)
    gameWindow = MainWindow()
    gameWindow.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
else:
    del GAME_DISPATCHER