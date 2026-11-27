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
# recipes/erpeton/src/erpeton/__init__.py
# ==================================================================================================
"""
A production-oriented Python chess engine module based on Stockfish 11, 
focused on providing low-latency move validation and classical search-based 
best move selection.

Architecture Note: Shared Engine State
--------------------------------------
All instances of `ChessBoard` share a single, global evaluation cache 
(Transposition Table and search history) managed internally by the 
`ChessEngine`. This is a deliberate design choice optimized for performance 
in sequential analysis scenarios.

Implications for Developers:
1. Performance Boost: When analyzing variations or consecutive moves within 
   the same game, the engine reuses previously calculated data, making 
   subsequent `ChessEngine.get_best_move` calls significantly faster.
2. Context Switching: When switching to a completely unrelated position 
   (e.g., loading a new chess puzzle, starting a fresh game, or running 
   deterministic benchmarks), the old cached data becomes irrelevant. 
   Always call `ChessEngine.clear_cache()` in these cases to ensure the 
   engine thinks with a "clean slate" and produces deterministic results.
3. The C++ search releases the Python Global Interpreter Lock (GIL). While the 
   underlying Stockfish thread pool is protected by a mutex (allowing only one 
   active search at a time per process), this design prevents Python-level 
   blocking, making it safe to use within asynchronous frameworks.

Quick Start
-----------
>>> from erpeton import ChessBoard, ChessEngine, FEN
>>> # Initialize the board
>>> board = ChessBoard()
>>> # Player makes a move
>>> board.make_move("e2e4")
>>> # Engine calculates a response (uses empty/fresh cache)
>>> result = ChessEngine.get_best_move(board, depth=12, movetime_ms=500)
>>> # Player responds, engine thinks again.
>>> # This search will be FASTER because it leverages the cache from previous search.
>>> board.make_move("e7e5")
>>> result2 = ChessEngine.get_best_move(board, depth=15, movetime_ms=500)
>>> # Switch to a new, unrelated context (e.g., a tactical puzzle)
>>> puzzle_fen = FEN("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4")
>>> board.set_position(puzzle_fen)
>>> # Clear the engine cache — previous game data is irrelevant here
>>> ChessEngine.clear_cache()
>>> # The search now starts with a clean slate
>>> puzzle_result = ChessEngine.get_best_move(board, depth=10)
"""

from ._core import STARTING_FEN, GameStatus, Color, FEN, AIResult, ChessBoard, ChessEngine

# ==================================================================================================
