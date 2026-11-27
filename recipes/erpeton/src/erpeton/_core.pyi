# ==================================================================================================
#
# Erpeton, a production-oriented Python chess engine module based on Stockfish 11
# Copyright (C) 2026 Ilya Snegov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================
# recipes/erpeton/src/erpeton/_core.pyi
# ==================================================================================================

from enum import Enum

# ==================================================================================================

STARTING_FEN: str
"""
The standard starting position Forsyth-Edwards Notation (FEN) string.
"""

# ==================================================================================================

class GameStatus(Enum):
    """
    Possible states of a chess game.

    Class Attributes
    ----------------
    ONGOING : GameStatus
        The game is in progress and no special condition applies.
        Value of the attribute: `0` (int).
    CHECK : GameStatus
        The side to move is in check but the game continues.
        Value of the attribute: `1` (int).
    CHECKMATE : GameStatus
        The side to move is in check and has no legal moves.
        Value of the attribute: `2` (int).
    STALEMATE : GameStatus
        The side to move has no legal moves but is not in check.
        Value of the attribute: `3` (int).
    DRAW : GameStatus
        The game is drawn (50-move rule, threefold repetition, or
        insufficient material).
        Value of the attribute: `4` (int).
    """
    ONGOING: GameStatus
    CHECK: GameStatus
    CHECKMATE: GameStatus
    STALEMATE: GameStatus
    DRAW: GameStatus

# ==================================================================================================

class Color(Enum):
    """
    Side to move in a chess position.

    Class Attributes
    ----------------
    WHITE : Color
        White side. Value of the attribute: `0` (int).
    BLACK : Color
        Black side. Value of the attribute: `1` (int).
    """
    WHITE: Color
    BLACK: Color

# ==================================================================================================

class FEN:
    """
    Semantic wrapper for a Forsyth-Edwards Notation (FEN) string.

    Ensures valid state initialization and provides a typed interface
    for board setup, preventing accidental misuse of raw strings.

    Instance Attributes
    -------------------
    value : str
        The underlying FEN string value.
    """
    value: str

    def __init__(self, value: str = ...) -> None:
        """
        Initialize the FEN wrapper.

        Parameters
        ----------
        value : str, optional
            The FEN string representation. Defaults to `STARTING_FEN`.
        """
        ...

    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

# ==================================================================================================

class AIResult:
    """
    Result container for the AI best move calculation.

    Instance Attributes
    -------------------
    best_move : str
        The recommended move in UCI coordinate notation (e.g., `"e2e4"`).
    score_cp : int
        The evaluation score in centipawns. Positive values favor White.
    depth : int
        The search depth reached in plies (half-moves).
    is_mate : bool
        Indicates if the score represents a forced checkmate.
    mate_in : int
        Number of plies until checkmate (only valid if `is_mate` is True).
    """
    best_move: str
    score_cp: int
    depth: int
    is_mate: bool
    mate_in: int

    def __repr__(self) -> str: ...

# ==================================================================================================

class ChessBoard:
    """
    Core chess board representation and move validation engine.

    Manages the internal Stockfish `Position` object, state history,
    and provides low-latency move generation and validation.

    Note: All `ChessBoard` instances share a single underlying evaluation 
    cache (Transposition Table) managed by the global `ChessEngine`.
    """

    def __init__(self, fen: FEN = ...) -> None:
        """
        Initialize the chess board.

        Parameters
        ----------
        fen : FEN, optional
            The initial board state. Defaults to the standard starting position.
        """
        ...

    def set_position(self, fen: FEN = ...) -> None:
        """
        Set the board to a new state.

        Clears the move history and reinitializes the internal position.
        Preserves the global transposition table cache for continuous analysis.

        Parameters
        ----------
        fen : FEN, optional
            The new FEN string to set. Defaults to the starting position.
        """
        ...

    def get_fen(self) -> str:
        """
        Get the current board state in FEN format.

        Returns
        -------
        str
            The Forsyth-Edwards Notation string of the current position.
        """
        ...

    def get_legal_moves(self) -> list[str]:
        """
        Generate all legal moves for the current position.

        Returns
        -------
        list[str]
            A list of legal moves in UCI coordinate notation.
        """
        ...

    def get_moves_from_square(self, sq: str) -> list[str]:
        """
        Generate all legal moves originating from a specific square.

        Parameters
        ----------
        sq : str
            The source square in algebraic notation (e.g., `"e2"`).

        Returns
        -------
        list[str]
            A list of legal moves starting from the given square.
        """
        ...

    def make_move(self, move_str: str) -> bool:
        """
        Attempt to make a move on the board.

        Parameters
        ----------
        move_str : str
            The move in UCI coordinate notation (e.g., `"e2e4"`).

        Returns
        -------
        bool
            True if the move was legal and successfully made, False otherwise.
        """
        ...

    def undo_move(self) -> None:
        """
        Undo the last made move.

        Reverts the board to the previous state if a move history exists.
        Does nothing if the board is at the initial state.
        """
        ...

    def get_status(self) -> GameStatus:
        """
        Get the current game status.

        Returns
        -------
        GameStatus
            The current state of the game (e.g., `ONGOING`, `CHECKMATE`).
        """
        ...

    def get_side_to_move(self) -> Color:
        """
        Get the color of the side whose turn it is to move.

        Returns
        -------
        Color
            The color of the side whose turn it is to move (e.g., `WHITE` or `BLACK`).
        """
        ...

# ==================================================================================================

class ChessEngine:
    """
    Global manager for the Stockfish evaluation engine.

    This class cannot be instantiated. It provides static methods to control
    the shared search state, transposition table, and move calculation for
    all `ChessBoard` instances.
    """

    @staticmethod
    def clear_cache() -> None:
        """
        Clear the global transposition table and search history.

        This forces the engine to forget all previously calculated positions.
        Useful when starting a completely new, unrelated game or puzzle,
        or when running deterministic performance benchmarks.
        """
        ...

    @staticmethod
    def get_best_move(board: ChessBoard, depth: int = 12, movetime_ms: int = 500) -> AIResult:
        """
        Calculate the best move for the given board position.

        This function releases the Python Global Interpreter Lock (GIL) during
        the C++ search, allowing for true concurrent execution in multi-threaded
        Python applications.

        Parameters
        ----------
        board : ChessBoard
            The board instance to analyze.
        depth : int, optional
            The maximum search depth in plies. Defaults to 12.
        movetime_ms : int, optional
            The maximum time to spend searching in milliseconds. Defaults to 500.

        Returns
        -------
        AIResult
            An object containing the best move, evaluation score, and search depth.
        """
        ...

# ==================================================================================================
