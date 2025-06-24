# Python Chess Game with Pygame GUI and AI

A fully functional chess game implemented in Python using Pygame for the graphical user interface. It supports Player vs Player (PvP), Player vs AI (PvE), and AI vs AI (EvE) modes with a basic chess engine featuring move validation, check/checkmate detection, and a minimax/negamax AI with alpha-beta pruning.

---

## Features

- **Graphical Chessboard UI:** Clean and interactive chessboard rendered using Pygame.
- **Multiple Game Modes:** Play human vs human, human vs AI, or AI vs AI.
- **Legal Move Validation:** Ensures all moves follow chess rules.
- **Check and Checkmate Detection:** Detects end game scenarios accurately.
- **Pawn Promotion Handling:** User selects promotion piece via GUI.
- **Undo and Reset:** Undo moves or reset the game anytime via keyboard.
- **AI Opponent:** Implements minimax/negamax search with alpha-beta pruning and positional evaluation.
- **Smooth Move Animations:** Pieces animate moving across the board for better UX.

---

## Getting Started

### Prerequisites

- Python 3.7+
- Pygame library

Install Pygame via pip if not already installed:

```bash
pip install pygame
