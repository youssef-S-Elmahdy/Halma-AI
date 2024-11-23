import tkinter as tk
from tkinter import messagebox
import time
import threading


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

    def move_to(self, new_row, new_col, duration=500, callback=None):
        start_x = self.col * self.cell_size + 10
        start_y = self.row * self.cell_size + 10
        end_x = new_col * self.cell_size + 10
        end_y = new_row * self.cell_size + 10
        dx = end_x - start_x
        dy = end_y - start_y
        steps = int(duration / 20)
        if steps == 0:
            steps = 1
        delta_x = dx / steps
        delta_y = dy / steps
        current_step = 0

        def animate():
            nonlocal current_step
            if current_step < steps:
                self.canvas.move(self.piece_id, delta_x, delta_y)
                current_step += 1
                self.canvas.after(20, animate)
            else:
                final_x1 = end_x
                final_y1 = end_y
                final_x2 = final_x1 + self.cell_size - 20
                final_y2 = final_y1 + self.cell_size - 20
                self.canvas.coords(self.piece_id, final_x1, final_y1, final_x2, final_y2)
                self.row, self.col = new_row, new_col
                if callback:
                    callback()

        animate()

    def set_outline(self, color="red", width=3):
        self.canvas.itemconfig(self.piece_id, outline=color, width=width)

    def clear_outline(self):
        self.canvas.itemconfig(self.piece_id, outline="", width=1)

    def delete(self):
        self.canvas.delete(self.piece_id)


class BoardState:
    def __init__(self, size=8, white_goal=None, black_goal=None):
        self.size = size
        self.board = [['' for _ in range(size)] for _ in range(size)]
        self.white_goal = white_goal if white_goal else []
        self.black_goal = black_goal if black_goal else []
        self.initialize_pieces()

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
            self.board[row][col] = 'white'
        for row, col in black_positions:
            self.board[row][col] = 'black'

    def copy(self):
        new_board = BoardState(self.size, self.white_goal, self.black_goal)
        new_board.board = [row[:] for row in self.board]
        return new_board

    def get_pieces(self, player_color):
        pieces = []
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == player_color:
                    pieces.append((row, col))
        return pieces

    def get_possible_moves(self, player_color):
        moves = []
        pieces = self.get_pieces(player_color)
        for piece in pieces:
            row, col = piece
            moves.extend(self.get_piece_moves(row, col))
        return moves

    def get_piece_moves(self, row, col):
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                if self.board[nr][nc] == '':
                    moves.append((row, col, nr, nc, []))
                elif self.board[nr][nc] != '':
                    jr, jc = nr + dr, nc + dc
                    if 0 <= jr < self.size and 0 <= jc < self.size and self.board[jr][jc] == '':
                        moves.append((row, col, jr, jc, []))
        return moves

    def make_move(self, move):
        from_row, from_col, to_row, to_col, _ = move
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = ''

    def undo_move(self, move):
        from_row, from_col, to_row, to_col, _ = move
        self.board[from_row][from_col] = self.board[to_row][to_col]
        self.board[to_row][to_col] = ''

    def evaluate(self, player_color):
        total_distance = 0
        opponent_color = 'black' if player_color == 'white' else 'white'
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == player_color:
                    total_distance -= self.distance_to_goal(row, col, player_color)
                elif self.board[row][col] == opponent_color:
                    total_distance += self.distance_to_goal(row, col, opponent_color)
        return total_distance

    def distance_to_goal(self, row, col, color):
        if color == 'white':
            return (self.size - 1 - row) + (self.size - 1 - col)
        else:
            return row + col

    def is_terminal(self):
        white_pieces_in_goal = sum(1 for pos in self.white_goal if self.board[pos[0]][pos[1]] == 'white')
        black_pieces_in_goal = sum(1 for pos in self.black_goal if self.board[pos[0]][pos[1]] == 'black')
        if white_pieces_in_goal >= 5:
            return True
        if black_pieces_in_goal >= 5:
            return True
        return False


class AIPlayer:
    def __init__(self, color, time_limit, max_depth=3):
        self.color = color
        self.time_limit = time_limit
        self.max_depth = max_depth
        self.start_time = None

    def make_move(self, board):
        self.start_time = time.time()
        best_move = None
        try:
            best_move = self.alpha_beta_search(board, self.max_depth)
        except TimeoutError:
            pass
        return best_move

    def alpha_beta_search(self, board, depth):
        def max_value(board, alpha, beta, depth):
            if time.time() - self.start_time >= self.time_limit:
                raise TimeoutError()
            if depth == 0 or board.is_terminal():
                return board.evaluate(self.color)
            v = float('-inf')
            moves = board.get_possible_moves(self.color)
            if not moves:
                return board.evaluate(self.color)
            for move in moves:
                board.make_move(move)
                v = max(v, min_value(board, alpha, beta, depth - 1))
                board.undo_move(move)
                if v >= beta:
                    return v
                alpha = max(alpha, v)
            return v

        def min_value(board, alpha, beta, depth):
            if time.time() - self.start_time >= self.time_limit:
                raise TimeoutError()
            if depth == 0 or board.is_terminal():
                return board.evaluate(self.color)
            v = float('inf')
            opponent_color = 'black' if self.color == 'white' else 'white'
            moves = board.get_possible_moves(opponent_color)
            if not moves:
                return board.evaluate(self.color)
            for move in moves:
                board.make_move(move)
                v = min(v, max_value(board, alpha, beta, depth - 1))
                board.undo_move(move)
                if v <= alpha:
                    return v
                beta = min(beta, v)
            return v

        best_score = float('-inf')
        beta = float('inf')
        best_move = None
        moves = board.get_possible_moves(self.color)
        for move in moves:
            if time.time() - self.start_time >= self.time_limit:
                raise TimeoutError()
            board.make_move(move)
            v = min_value(board, best_score, beta, depth - 1)
            board.undo_move(move)
            if v > best_score:
                best_score = v
                best_move = move
        return best_move


class HalmaBoard:
    def __init__(self, root, size=8, seconds_limit=10, white_player='human', black_player='human'):
        self.size = size
        self.cell_size = 50
        self.canvas = tk.Canvas(root, width=self.size * self.cell_size, height=self.size * self.cell_size)
        self.canvas.pack()

        self.seconds_limit = seconds_limit
        self.time_remaining = self.seconds_limit
        self.timer_id = None

        self.create_grid()

        self.pieces = {}
        self.selected_piece = None
        self.valid_moves = []
        self.current_turn = 'white'
        self.white_score = 0
        self.black_score = 0

        self.white_goal = [(7, 7), (7, 6), (7, 5), (6, 7), (6, 6)]
        self.black_goal = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)]

        self.initialize_pieces()
        self.status_bar = tk.Label(root, text="White's Turn | White Score: 0 | Black Score: 0 | Time Left: 10s",
                                   font=("Arial", 14))
        self.status_bar.pack()

        self.is_human = {
            'white': white_player == 'human',
            'black': black_player == 'human'
        }

        if not self.is_human['white']:
            self.white_player = AIPlayer('white', self.seconds_limit, max_depth=3)
        else:
            self.white_player = None

        if not self.is_human['black']:
            self.black_player = AIPlayer('black', self.seconds_limit, max_depth=3)
        else:
            self.black_player = None

        self.canvas.bind("<Button-1>", self.on_click)

        self.start_timer()

        if not self.is_human[self.current_turn]:
            self.canvas.after(100, self.computer_move)

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

    def highlight_moves(self, row, col):
        self.clear_highlights()

        possible_moves = self.get_possible_moves(row, col)
        valid_moves = []

        for move in possible_moves:
            r, c = move[2], move[3]
            x1 = c * self.cell_size
            y1 = r * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            move_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline='green', width=2)
            valid_moves.append((r, c, move_id, move))

        self.valid_moves = valid_moves

    def get_possible_moves(self, row, col):
        board_state = self.create_board_state()
        return board_state.get_piece_moves(row, col)

    def clear_highlights(self):
        for move in self.valid_moves:
            self.canvas.delete(move[2])
        self.valid_moves = []

    def on_click(self, event):
        if not self.is_human[self.current_turn]:
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
                    position = self.selected_piece
                    self.apply_move(move[3])
                    break

    def move_piece(self, position, to_pos, animate=False, callback=None):
        from_pos = (position.row, position.col)

        def after_animation():
            del self.pieces[from_pos]
            self.pieces[to_pos] = position
            position.clear_outline()
            self.clear_highlights()
            self.update_score()
            self.check_for_win()
            if callback:
                callback()

        if animate:
            position.move_to(to_pos[0], to_pos[1], duration=500, callback=after_animation)
        else:
            position.move_to(to_pos[0], to_pos[1])
            after_animation()

    def apply_move(self, move):
        from_row, from_col, to_row, to_col, path = move
        position = self.pieces[(from_row, from_col)]
        is_human_player = self.is_human[self.current_turn]

        def after_move():
            if not self.check_for_win():
                self.switch_turn()

        self.move_piece(position, (to_row, to_col), animate=True, callback=after_move)

    def switch_turn(self):
        if self.timer_id:
            self.canvas.after_cancel(self.timer_id)

        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        self.time_remaining = self.seconds_limit
        self.update_status()
        self.start_timer()

        if not self.is_human[self.current_turn]:
            self.canvas.after(100, self.computer_move)

    def start_timer(self):
        if self.time_remaining > 0:
            self.time_remaining -= 1
            self.update_status()
            self.timer_id = self.canvas.after(1000, self.start_timer)
        else:
            messagebox.showinfo("Time's up!", f"{self.current_turn.capitalize()} ran out of time!")
            if not self.check_for_win():
                self.switch_turn()

    def update_score(self):
        self.white_score = sum(1 for pos in self.white_goal if pos in self.pieces and self.pieces[pos].color == 'white')
        self.black_score = sum(1 for pos in self.black_goal if pos in self.pieces and self.pieces[pos].color == 'black')

    def update_status(self):
        self.status_bar.config(text=f"{self.current_turn.capitalize()}'s Turn | White Score: {self.white_score} | "
                                    f"Black Score: {self.black_score} | Time Left: {self.time_remaining}s")
        self.status_bar.update_idletasks()

    def check_for_win(self):
        self.update_score()
        if self.white_score >= 5:
            messagebox.showinfo("Game Over", f"White wins with a score of {self.white_score}!")
            self.canvas.unbind("<Button-1>")
            self.stop_timer()
            return True
        elif self.black_score >= 5:
            messagebox.showinfo("Game Over", f"Black wins with a score of {self.black_score}!")
            self.canvas.unbind("<Button-1>")
            self.stop_timer()
            return True
        return False

    def stop_timer(self):
        if self.timer_id:
            self.canvas.after_cancel(self.timer_id)
            self.timer_id = None

    def create_board_state(self):
        board_state = BoardState(self.size, white_goal=self.white_goal, black_goal=self.black_goal)
        board_state.board = [['' for _ in range(self.size)] for _ in range(self.size)]
        for (row, col), position in self.pieces.items():
            board_state.board[row][col] = position.color
        return board_state

    def computer_move(self):
        board_state = self.create_board_state()
        ai_player = self.white_player if self.current_turn == 'white' else self.black_player

        threading.Thread(target=self.run_ai_move, args=(ai_player, board_state)).start()

    def run_ai_move(self, ai_player, board_state):
        best_move = ai_player.make_move(board_state)
        self.canvas.after(0, self.apply_ai_move, best_move)

    def apply_ai_move(self, best_move):
        if best_move:
            self.apply_move(best_move)
        else:
            self.switch_turn()


root = tk.Tk()
root.title("Halma")
game_board = HalmaBoard(root, seconds_limit=15, white_player='human', black_player='ai')
root.mainloop()
