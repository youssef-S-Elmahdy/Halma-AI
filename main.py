import tkinter as tk
from tkinter import messagebox
import math


class Position:
    def __init__(self, row, col, color, canvas, cell_size):
        self.row = row
        self.col = col
        self.color = color
        self.canvas = canvas
        self.cell_size = cell_size
        self.piece_id = self.create_piece()

    def create_piece(self):
        x1 = self.col * self.cell_size + 10
        y1 = self.row * self.cell_size + 10
        x2 = x1 + self.cell_size - 20
        y2 = y1 + self.cell_size - 20
        return self.canvas.create_oval(x1, y1, x2, y2, fill=self.color, outline="")

    def move_to(self, row, col):
        self.row, self.col = row, col
        x1 = col * self.cell_size + 10
        y1 = row * self.cell_size + 10
        x2 = x1 + self.cell_size - 20
        y2 = y1 + self.cell_size - 20
        self.canvas.coords(self.piece_id, x1, y1, x2, y2)

    def set_outline(self, color="red", width=3):
        self.canvas.itemconfig(self.piece_id, outline=color, width=width)

    def clear_outline(self):
        self.canvas.itemconfig(self.piece_id, outline="", width=1)

    def delete(self):
        self.canvas.delete(self.piece_id)


class HalmaBoard:
    def __init__(self, root, size=8, seconds_limit=10, ai_enabled=False):
        self.size = size
        self.cell_size = 50
        self.canvas = tk.Canvas(root, width=self.size * self.cell_size, height=self.size * self.cell_size)
        self.canvas.pack()

        self.seconds_limit = seconds_limit
        self.time_remaining = self.seconds_limit
        self.timer_id = None

        self.pieces = {}
        self.selected_piece = None
        self.valid_moves = []
        self.current_turn = 'white'
        self.white_score = 0
        self.black_score = 0
        self.turn_completed = False

        self.ai_enabled = ai_enabled

        # Create grid, pieces, and UI elements
        self.create_grid()
        self.initialize_pieces()

        # Status bar to display game state
        self.status_bar = tk.Label(root, text="White's Turn | White Score: 0 | Black Score: 0 | Time Left: 10s",
                                   font=("Arial", 14))
        self.status_bar.pack()

        self.canvas.bind("<Button-1>", self.on_click)
        self.update_status()
        self.start_timer()

    def create_grid(self):
        for row in range(self.size):
            for col in range(self.size):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                color = 'beige' if (row + col) % 2 == 0 else 'lightgray'
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

    def place_piece(self, row, col, color):
        position = Position(row, col, color, self.canvas, self.cell_size)
        self.pieces[(row, col)] = position

    def initialize_pieces(self):
        white_positions = [
            (0, 0), (0, 1), (0, 2), (0, 3),
            (1, 0), (1, 1), (1, 2),
            (2, 0), (2, 1),
            (3, 0)
        ]
        black_positions = [
            (7, 7), (7, 6), (7, 5), (7, 4),
            (6, 7), (6, 6), (6, 5),
            (5, 7), (5, 6),
            (4, 7)
        ]
        for row, col in white_positions:
            self.place_piece(row, col, 'white')
        for row, col in black_positions:
            self.place_piece(row, col, 'black')

    def update_status(self):
        """
        Updates the status bar with the current turn, scores, and remaining time.
        """
        self.status_bar.config(text=f"{self.current_turn.capitalize()}'s Turn | White Score: {self.white_score} | "
                                    f"Black Score: {self.black_score} | Time Left: {self.time_remaining}s")

    def update_score(self):
        """
        Updates the scores for each player based on their pieces in the goal area.
        """
        white_goal = [(7, 7), (7, 6), (7, 5), (6, 7), (6, 6)]
        black_goal = [(0, 0), (0, 1), (1, 0), (1, 1)]

        self.white_score = sum(1 for pos in white_goal if pos in self.pieces and self.pieces[pos].color == 'white')
        self.black_score = sum(1 for pos in black_goal if pos in self.pieces and self.pieces[pos].color == 'black')

    def apply_move(self, move):
        """
        Apply a move to the board.
        """
        from_pos, to_pos = move
        piece = self.pieces.pop(from_pos)  # Remove the piece from its original position
        piece.move_to(*to_pos)
        self.pieces[to_pos] = piece  # Place the piece in the new position

    def undo_move(self, move):
        """
        Undo a move on the board.
        """
        to_pos, from_pos = move
        piece = self.pieces.pop(to_pos)  # Remove the piece from its current position
        piece.move_to(*from_pos)
        self.pieces[from_pos] = piece  # Place the piece back in its original position

    def check_for_win(self):
        """
        Checks if either player has won by getting 5 pieces into the opponent's goal area.
        """
        white_goal = [(7, 7), (7, 6), (7, 5), (6, 7), (6, 6)]
        black_goal = [(0, 0), (0, 1), (1, 0), (1, 1)]

        if self.white_score >= 5:
            messagebox.showinfo("Game Over", "White wins!")
            self.end_game()
        elif self.black_score >= 5:
            messagebox.showinfo("Game Over", "Black wins!")
            self.end_game()

    def end_game(self):
        """
        Ends the game by disabling all interactions.
        """
        self.canvas.unbind("<Button-1>")
        if self.timer_id:
            self.canvas.after_cancel(self.timer_id)

    def highlight_moves(self, row, col):
        self.clear_highlights()

        possible_moves = self.get_possible_moves(row, col)
        valid_moves = []

        for r, c in possible_moves:
            if 0 <= r < self.size and 0 <= c < self.size and (r, c) not in self.pieces:
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                move_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline='green', width=2)
                valid_moves.append((r, c, move_id))

        self.valid_moves = valid_moves

    def get_possible_moves(self, row, col):
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.size and 0 <= nc < self.size and (nr, nc) not in self.pieces:
                moves.append((nr, nc))
            elif 0 <= nr < self.size and 0 <= nc < self.size and (nr, nc) in self.pieces:
                jr, jc = nr + dr * 2, nc + dc * 2
                if 0 <= jr < self.size and 0 <= jc < self.size and (jr, jc) not in self.pieces:
                    moves.append((jr, jc))
        return moves

    def clear_highlights(self):
        for move in self.valid_moves:
            self.canvas.delete(move[2])
        self.valid_moves = []

    def on_click(self, event):
        if self.ai_enabled and self.current_turn == 'black':
            return
        if self.turn_completed:
            return

        row, col = event.y // self.cell_size, event.x // self.cell_size

        if (row, col) in self.pieces and self.pieces[(row, col)].color == self.current_turn:
            if self.selected_piece:
                self.selected_piece.clear_outline()
            self.selected_piece = self.pieces[(row, col)]
            self.selected_piece.set_outline("red", 3)
            self.highlight_moves(row, col)
        elif self.selected_piece:
            for move in self.valid_moves:
                if (row, col) == (move[0], move[1]):
                    self.move_piece(self.selected_piece, (move[0], move[1]))
                    self.turn_completed = True
                    self.switch_turn()
                    return

    def move_piece(self, position, to_pos):
        from_pos = (position.row, position.col)
        position.move_to(*to_pos)
        del self.pieces[from_pos]
        self.pieces[to_pos] = position
        position.clear_outline()
        self.clear_highlights()
        self.update_score()
        self.check_for_win()

    def switch_turn(self):
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        self.turn_completed = False
        self.reset_timer()
        self.update_status()
        if self.ai_enabled and self.current_turn == 'black':
            self.make_best_move_if_AI()

    def start_timer(self):
        if self.time_remaining > 0:
            self.time_remaining -= 1
            self.update_status()
            self.timer_id = self.canvas.after(1000, self.start_timer)
        else:
            messagebox.showinfo("Time's up!", f"{self.current_turn.capitalize()} ran out of time!")
            self.switch_turn()

    def reset_timer(self):
        if self.timer_id:
            self.canvas.after_cancel(self.timer_id)
        self.time_remaining = self.seconds_limit
        self.start_timer()

    def minimax(self, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.white_score >= 5 or self.black_score >= 5:
            return self.utility_function(), None

        best_move = None
        if maximizing_player:
            max_eval = -math.inf
            for move in self.generate_legal_moves('white'):
                self.apply_move(move)
                eval, _ = self.minimax(depth - 1, alpha, beta, False)
                self.undo_move(move)

                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = math.inf
            for move in self.generate_legal_moves('black'):
                self.apply_move(move)
                eval, _ = self.minimax(depth - 1, alpha, beta, True)
                self.undo_move(move)

                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def generate_legal_moves(self, color):
        moves = []
        for position in self.pieces.values():
            if position.color == color:
                possible_moves = self.get_possible_moves(position.row, position.col)
                for move in possible_moves:
                    moves.append(((position.row, position.col), move))
        return moves

    def make_best_move_if_AI(self):
        _, best_move = self.minimax(depth=3, alpha=-math.inf, beta=math.inf, maximizing_player=False)
        if best_move:
            self.apply_move(best_move)
            self.turn_completed = True
            self.update_score()
            self.check_for_win()
            self.switch_turn()

    def utility_function(self):
        white_goal = [(7, 7), (7, 6), (7, 5), (6, 7), (6, 6)]
        black_goal = [(0, 0), (0, 1), (1, 0), (1, 1)]
        white_score = sum(1 for pos in white_goal if pos in self.pieces and self.pieces[pos].color == 'white')
        black_score = sum(1 for pos in black_goal if pos in self.pieces and self.pieces[pos].color == 'black')
        return white_score - black_score if self.current_turn == 'white' else black_score - white_score


root = tk.Tk()
root.title("Halma")
game_board = HalmaBoard(root, seconds_limit=15, ai_enabled=True)
root.mainloop()
