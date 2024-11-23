# Halma AI Project

## Overview

It’s time to have some fun while gaining hands-on experience with applied AI techniques! Building clever software based on theoretical concepts is at the heart of AI. For this project, we’ve implemented **Halma**, a simple yet strategically rich board game. The highlight of this project is a tournament where Halma-playing agents face off with strict per-turn time limits to determine which program is the smartest. Let the games begin!

---

## The Problem

To focus on adversarial search and smart game playing, Halma was chosen for its simplicity in rules and movement while retaining strategic depth. 

### Key Features of Halma:
- **Objective:** Move all pieces from your starting corner to the opponent’s goal camp.
- **Rules Highlights:**
  - Turn-based play with a time limit for moves.
  - Players can move pieces in any direction into free spaces or by jumping over other pieces.
  - Once a piece enters the goal camp, it cannot leave; similarly, pieces cannot re-enter their own home area.
  - The game ends when all pieces are in the opponent's camp.
- **Board Variations:** Standard size is 16x16, but 8x8 and 10x10 boards are also supported.

For more about the game rules, visit the [Wikipedia page](https://en.wikipedia.org/wiki/Halma).

---

## The Assignment

The goal is to create a **graphical Halma-playing program** with the following features:

### Basic Features:
1. **Graphical Board**:
   - Displays the board, pieces, and camps.
   - Shows move highlights and turn indicators.

2. **Two-Player Interface**:
   - Supports human-vs-human and human-vs-computer play.
   - Allows user interaction via clicks or text-based move input.

3. **Rules Enforcement**:
   - Validates legal moves.
   - Ensures win/loss detection based on Halma rules.

4. **Turn Management**:
   - Enforces time limits for moves.
   - Alternates turns and highlights the most recent move for clarity.

### Advanced Features:
1. **AI Agent**:
   - Implements **Minimax search with alpha-beta pruning** to determine the best moves.
   - Efficiently explores the game tree within the time limit.
   - Returns optimized moves while adapting to the opponent’s strategy.

2. **Utility Function**:
   - Scores the board state based on piece distances to the goal and positional advantage.
   - Helps evaluate the best moves during the Minimax search.

3. **Tournament-Ready**:
   - The AI agent can compete against others in a timed tournament setting.

4. **Customizability**:
   - Supports board size selection (8x8, 10x10, 16x16).
   - Allows loading specific board configurations for testing.

---

## How to Use

1. **Running the Program**:
python halma.py --board_size [8|10|16] --seconds_limit [time_per_move] --human_player [white|black]

2. **Gameplay**:
- The game window displays the board with human and AI player camps.
- Moves are made either by clicking or entering them as text (e.g., `a3->b4`).
- A status bar shows the current turn, scores, and remaining time.

3. **Endgame**:
- When a player wins, the game announces the result, including:
  - Final scores.
  - Number of move cycles.
  - Statistics like jumps made during the game.

---

## Milestones

### Part 1: Manual Game Framework
- **Graphical Board:** Displays the board and highlights moves.
- **Win/Loss Detector:** Identifies when a player has won.
- **Move Generator:** Generates all legal moves for a player, including jumps.
- **Turn Management:** Alternates turns, enforces rules, and displays a status bar.
- **Milestone:** A functioning two-player manual game.

### Part 2: AI Agent Development
- **Minimax Search:** Searches the game tree to select the best moves.
- **Alpha-Beta Pruning:** Optimizes the search by pruning irrelevant branches.
- **Utility Function:** Evaluates board states to guide decision-making.
- **Performance Tuning:** Ensures the AI operates efficiently within time limits.
- **Milestone:** A competitive AI agent ready for tournaments.

---

## Key Highlights

- **Real-Time AI Decision-Making:** The AI calculates moves within a strict time limit, ensuring competitive gameplay.
- **Dynamic Move Highlights:** Tracks and displays moves for clarity.
- **Scoring System:** Includes endgame scoring based on pieces in the goal and proximity to the goal.
- **Customizability:** Adaptable to different board sizes and configurations.

---

## Example Gameplay

1. **Start the Game**: Run the program with the desired settings.
2. **Human vs AI**:
- The AI makes calculated moves using Minimax with alpha-beta pruning.
- Human players can interact via clicks or text commands.
3. **Win Announcement**: The game announces the winner with detailed stats.

---
