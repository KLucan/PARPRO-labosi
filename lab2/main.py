from mpi4py import MPI
from random import randint

victory_state = 0

class Connect4Board:
    def __init__(self):
        self.board = [['[_]' for _ in range(7)] for _ in range(6)]

    def get(self, row, col, default=None):
        if 0 <= row < len(self.board) and 0 <= col < len(self.board[0]):
            return self.board[row][col]
        return default

    def set(self, row, col, value):
        self.board[row][col] = value

    def print_row(self, row):
        print(''.join(self.board[row]))

    def print_board(self):
        print(" 0  1  2  3  4  5  6")
        for row_index in range(len(self.board)):
            self.print_row(row_index)
        print()

class Connect4Game:
    def __init__(self, player_first=None):
        self.board = Connect4Board()
        self.player = player_first if player_first is not None else randint(0, 1)

    def play(self, col_index):
        global victory_state
        chosen_row = None
        for row_index in range(len(self.board.board) - 1, -1, -1):
            if self.board.board[row_index][col_index] == '[_]':
                chosen_row = row_index
                self.board.board[row_index][col_index] = f"[{self.player}]"
                victory_state = self.check_victory(row_index, col_index)
                self.player = 1 if self.player == 0 else 0
                return
        raise ValueError("Column is full")

    def input_move(self):
        if self.player == 1:
            col = int(input("Enter column: "))
            try:
                self.play(col)
            except ValueError as e:
                print(e)
                self.input_move()
        else:
            try:
                self.play(randint(0, 6))
            except ValueError as e:
                self.input_move()

    def check_victory(self, row, col):
        checkrow = [self.board.board[row][c] for c in range(len(self.board.board[row]))]
        print(f"[{self.player}]")
        print(checkrow)
        in_a_row = 0
        for cell in checkrow:
            if cell == f"[{self.player}]":
                in_a_row += 1
            else:
                in_a_row = 0
            if in_a_row == 4:
                return 1 if self.player == 0 else -1
        checkcol = [self.board.board[r][col] for r in range(len(self.board.board))]
        print(checkcol)
        for cell in checkcol:
            if cell == f"[{self.player}]":
                in_a_row += 1
            else:
                in_a_row = 0
            if in_a_row == 4:
                return 1 if self.player == 0 else -1
        up_diag = [self.board.get(row-3, col-3), self.board.get(row-2, col-2), self.board.get(row-1, col-1), self.board.get(row, col), self.board.get(row+1, col+1), self.board.get(row+2, col+2), self.board.get(row+3, col+3)]
        print(up_diag)
        for cell in up_diag:
            if cell == f"[{self.player}]":
                in_a_row += 1
            else:
                in_a_row = 0
            if in_a_row == 4:
                return 1 if self.player == 0 else -1
        down_diag = [self.board.get(row-3, col+3), self.board.get(row-2, col+2), self.board.get(row-1, col+1), self.board.get(row, col), self.board.get(row+1, col-1), self.board.get(row+2, col-2), self.board.get(row+3, col-3)]
        print(down_diag)
        for cell in down_diag:
            if cell == f"[{self.player}]":
                in_a_row += 1
            else:
                in_a_row = 0
            if in_a_row == 4:
                return 1 if self.player == 0 else -1
        return 0




game = Connect4Game()
while (victory_state == 0):
    print(f"victory_state: {victory_state}")
    game.board.print_board()
    game.input_move()
print(f"Winner: {'Player' if victory_state == -1 else 'CPU'}")
game.board.print_board()
