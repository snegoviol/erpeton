// =================================================================================================
//
// Erpeton, a production-oriented Python chess engine module based on Stockfish 11
// Copyright (C) 2026 Ilya Snegov
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program. If not, see <http://www.gnu.org/licenses/>.
//
// =================================================================================================
// recipes/erpeton/src/erpeton/_core.cpp
// =================================================================================================

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>
#include <deque>
#include <string>
#include <vector>
#include <mutex>
#include <memory>
#include <cmath>
#include <cstdio>
#include <unistd.h>
#include <fcntl.h>

#include "stockfish11/bitboard.h"
#include "stockfish11/position.h"
#include "stockfish11/movegen.h"
#include "stockfish11/search.h"
#include "stockfish11/thread.h"
#include "stockfish11/tt.h"
#include "stockfish11/uci.h"
#include "stockfish11/endgame.h"
#include "stockfish11/syzygy/tbprobe.h"

namespace PSQT {
    void init(); 
}

namespace py = pybind11;

// =================================================================================================

const std::string STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

class ChessBoard;

struct AIResult {
    std::string best_move;
    int score_cp; 
    int depth;
    bool is_mate;
    int mate_in;
};

class FEN {
public:
    std::string value;
    
    FEN() : value(STARTING_FEN) {}
    explicit FEN(std::string v) : value(std::move(v)) {
        if (value.empty()) {
            value = STARTING_FEN;
        }
    }
    
    operator std::string() const { return value; }
};

enum class GameStatus {
    ONGOING = 0,
    CHECK = 1,
    CHECKMATE = 2,
    STALEMATE = 3,
    DRAW = 4
};

// =================================================================================================

class ChessEngine {
private:
    ChessEngine() = delete;
    ChessEngine(const ChessEngine&) = delete;
    ChessEngine& operator=(const ChessEngine&) = delete;

    static bool is_initialized;
    static std::mutex init_mutex;
    static std::mutex search_mutex;

public:
    static void ensure_initialized();
    static void clear_cache();
    
    static AIResult get_best_move(ChessBoard& board, int depth = 12, int movetime_ms = 500);
};

bool ChessEngine::is_initialized = false;
std::mutex ChessEngine::init_mutex;
std::mutex ChessEngine::search_mutex;

// =================================================================================================

class ChessBoard {
    Position pos;
    StateListPtr states_ptr;
    std::deque<Move> move_history;

public:
    explicit ChessBoard(const FEN& fen = FEN()) {
        ChessEngine::ensure_initialized();
        states_ptr.reset(new std::deque<StateInfo>(1));
        pos.set(fen.value, false, &states_ptr->back(), Threads.main());
    }

    void set_position(const FEN& fen = FEN()) {
        states_ptr.reset(new std::deque<StateInfo>(1));
        move_history.clear();
        pos.set(fen.value, false, &states_ptr->back(), Threads.main());
        TT.new_search();
    }

    std::string get_fen() const {
        return pos.fen();
    }

    std::vector<std::string> get_legal_moves() const {
        std::vector<std::string> moves;
        moves.reserve(30);
        bool is960 = pos.is_chess960();
        for (const auto& m : MoveList<LEGAL>(pos)) {
            moves.push_back(UCI::move(m, is960));
        }
        return moves;
    }

    std::vector<std::string> get_moves_from_square(const std::string& sq) const {
        std::vector<std::string> moves;
        if (sq.length() != 2) return moves;
        
        File f = File(sq[0] - 'a');
        Rank r = Rank(sq[1] - '1');
        Square from = make_square(f, r);
        bool is960 = pos.is_chess960();

        for (const auto& m : MoveList<LEGAL>(pos)) {
            if (from_sq(m) == from) {
                moves.push_back(UCI::move(m, is960));
            }
        }
        return moves;
    }

    bool make_move(const std::string& move_str) {
        std::string ms = move_str;
        Move m = UCI::to_move(pos, ms);
        
        if (m == MOVE_NONE) {
            return false; 
        }

        states_ptr->emplace_back();
        pos.do_move(m, states_ptr->back());
        move_history.push_back(m);
        return true;
    }

    void undo_move() {
        if (states_ptr && states_ptr->size() > 1 && !move_history.empty()) {
            Move m = move_history.back();
            pos.undo_move(m);
            states_ptr->pop_back();
            move_history.pop_back();
        }
    }

    GameStatus get_status() const {
        if (MoveList<LEGAL>(pos).size() == 0) {
            return pos.checkers() ? GameStatus::CHECKMATE : GameStatus::STALEMATE;
        }
        if (pos.is_draw(0)) { 
            return GameStatus::DRAW;
        }
        if (pos.checkers()) {
            return GameStatus::CHECK;
        }
        return GameStatus::ONGOING;
    }

    ::Color get_side_to_move() const {
        return pos.side_to_move() == WHITE ? ::Color::WHITE : ::Color::BLACK;
    }

    // Exposed for AI search
    Position& get_pos() { return pos; }
    const Position& get_pos() const { return pos; }
    StateListPtr& get_states_ptr() { return states_ptr; }
};

// =================================================================================================

void ChessEngine::ensure_initialized() {
    std::lock_guard<std::mutex> lock(init_mutex);
    if (is_initialized) return;

    UCI::init(Options);
    Options["Threads"] = 1; 
    Options["Hash"] = 16;   
    
    PSQT::init();
    Bitboards::init();
    Position::init();
    Bitbases::init();
    Endgames::init();
    
    Threads.set(Options["Threads"]);
    Search::clear(); 

    is_initialized = true;
}

void ChessEngine::clear_cache() {
    std::lock_guard<std::mutex> lock(search_mutex);
    Search::clear();
    TT.new_search(); 
}

AIResult ChessEngine::get_best_move(ChessBoard& board, int depth, int movetime_ms) {
    ensure_initialized();
    
    // Save original stdout
    int original_stdout = dup(1);
    
    // Redirect stdout to /dev/null
    int dev_null = open("/dev/null", O_WRONLY);
    dup2(dev_null, 1);
    close(dev_null);

    std::lock_guard<std::mutex> lock(search_mutex);
    
    Search::LimitsType limits;
    limits.depth = depth;
    limits.movetime = movetime_ms;

    Threads.start_thinking(board.get_pos(), board.get_states_ptr(), limits, false);
    Threads.main()->wait_for_search_finished();

    // Restore original stdout
    dup2(original_stdout, 1);
    close(original_stdout);

    AIResult res;
    const auto& root_moves = Threads.main()->rootMoves;
    
    if (root_moves.empty() || root_moves[0].pv.empty() || root_moves[0].pv[0] == MOVE_NONE) {
        res.best_move = "none";
        res.score_cp = 0;
        res.depth = 0;
        res.is_mate = false;
        res.mate_in = 0;
        return res;
    }

    const auto& best_rm = root_moves[0];
    res.best_move = UCI::move(best_rm.pv[0], board.get_pos().is_chess960());
    res.depth = Threads.main()->completedDepth;

    if (std::abs(best_rm.score) >= VALUE_MATE - MAX_PLY) {
        res.is_mate = true;
        int plies_to_mate = VALUE_MATE - std::abs(best_rm.score);
        res.mate_in = plies_to_mate;
        res.score_cp = best_rm.score > 0 ? 100000 : -100000;
    } else {
        res.is_mate = false;
        res.mate_in = 0;
        // Stockfish internal value to UCI centipawns: (value * 100) / PawnValueEg
        res.score_cp = static_cast<int>((best_rm.score * 100) / PawnValueEg);
    }

    return res;
}

// =================================================================================================

PYBIND11_MODULE(_core, m) {

    ChessEngine::ensure_initialized();
    m.attr("STARTING_FEN") = STARTING_FEN;

    py::class_<FEN>(m, "FEN")
        .def(py::init<>())
        .def(py::init<std::string>(), py::arg("value"))
        .def_readwrite("value", &FEN::value)
        .def("__str__", [](const FEN& f) { return f.value; })
        .def("__repr__", [](const FEN& f) { return "<FEN: " + f.value + ">"; });

    py::enum_<GameStatus>(m, "GameStatus")
        .value("ONGOING", GameStatus::ONGOING)
        .value("CHECK", GameStatus::CHECK)
        .value("CHECKMATE", GameStatus::CHECKMATE)
        .value("STALEMATE", GameStatus::STALEMATE)
        .value("DRAW", GameStatus::DRAW)
        .export_values();

    py::enum_<::Color>(m, "Color")
        .value("WHITE", ::Color::WHITE)
        .value("BLACK", ::Color::BLACK)
        .export_values();

    py::class_<AIResult>(m, "AIResult")
        .def_readonly("best_move", &AIResult::best_move)
        .def_readonly("score_cp", &AIResult::score_cp)
        .def_readonly("depth", &AIResult::depth)
        .def_readonly("is_mate", &AIResult::is_mate)
        .def_readonly("mate_in", &AIResult::mate_in)
        .def("__repr__", [](const AIResult& r) {
            return "<AIResult: move=" + r.best_move + 
                   " score=" + std::to_string(r.score_cp) + 
                   " depth=" + std::to_string(r.depth) + ">";
        });

    py::class_<ChessBoard>(m, "ChessBoard")
        .def(py::init<const FEN&>(), py::arg("fen") = FEN())
        .def("set_position", &ChessBoard::set_position, py::arg("fen") = FEN())
        .def("get_fen", &ChessBoard::get_fen)
        .def("get_legal_moves", &ChessBoard::get_legal_moves)
        .def("get_moves_from_square", &ChessBoard::get_moves_from_square)
        .def("make_move", &ChessBoard::make_move)
        .def("undo_move", &ChessBoard::undo_move)
        .def("get_status", &ChessBoard::get_status)
        .def("get_side_to_move", &ChessBoard::get_side_to_move);

    py::class_<ChessEngine>(m, "ChessEngine")
        .def_static("ensure_initialized", &ChessEngine::ensure_initialized)
        .def_static("clear_cache", &ChessEngine::clear_cache)
        .def_static("get_best_move", &ChessEngine::get_best_move, 
            py::arg("board"), 
            py::arg("depth") = 12, 
            py::arg("movetime_ms") = 500,
            py::call_guard<py::gil_scoped_release>()); 
}

// =================================================================================================
