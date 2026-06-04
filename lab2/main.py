from argparse import ArgumentParser
from collections import deque
from copy import deepcopy

import time

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

    def is_valid_move(self, col_index):
        for row_index in range(len(self.board.board) - 1, -1, -1):
            if self.board.get(row_index, col_index) == '[_]':
                return True
        return False

    def play(self, col_index):
        global victory_state
        chosen_row = None
        for row_index in range(len(self.board.board) - 1, -1, -1):
            if self.board.get(row_index, col_index) == '[_]':
                chosen_row = row_index
                self.board.set(row_index, col_index, f"[{self.player}]")
                victory_state = self.check_victory(row_index, col_index)
                self.player = 1 if self.player == 0 else 0
                return
        raise ValueError("Invalid move")

    def check_victory(self, row, col):
        checkrow = [self.board.get(row, c) for c in range(len(self.board.board[row]))]
        in_a_row = 0
        for cell in checkrow:
            if cell == f"[{self.player}]":
                in_a_row += 1
            else:
                in_a_row = 0
            if in_a_row == 4:
                return 1 if self.player == 0 else -1
        in_a_row = 0
        checkcol = [self.board.get(r, col) for r in range(len(self.board.board))]
        for cell in checkcol:
            if cell == f"[{self.player}]":
                in_a_row += 1
            else:
                in_a_row = 0
            if in_a_row == 4:
                return 1 if self.player == 0 else -1
        in_a_row = 0
        up_diag = [self.board.get(row-3, col-3), self.board.get(row-2, col-2), self.board.get(row-1, col-1), self.board.get(row, col), self.board.get(row+1, col+1), self.board.get(row+2, col+2), self.board.get(row+3, col+3)]
        for cell in up_diag:
            if cell == f"[{self.player}]":
                in_a_row += 1
            else:
                in_a_row = 0
            if in_a_row == 4:
                return 1 if self.player == 0 else -1
        in_a_row = 0
        down_diag = [self.board.get(row-3, col+3), self.board.get(row-2, col+2), self.board.get(row-1, col+1), self.board.get(row, col), self.board.get(row+1, col-1), self.board.get(row+2, col-2), self.board.get(row+3, col-3)]
        for cell in down_diag:
            if cell == f"[{self.player}]":
                in_a_row += 1
            else:
                in_a_row = 0
            if in_a_row == 4:
                return 1 if self.player == 0 else -1
        return 0

def bfs_average_eval(state, max_depth):
    """
    listovi:
       1 = CPU win
      -1 = Player win
       0 = nema dobitnika

    ne-listovi: vrijednost = (zbroj vrijednosti djece) / (broj djece)
    """
    global victory_state

    if victory_state != 0: # sanity check
        return float(victory_state)

    # nema validnih poteza ili smo na listu
    if max_depth <= 0 or not any(state.is_valid_move(c) for c in range(7)):
        return 0.0

    # nodes - stanje
    # levels – razine od korijena do listova
    # term_val  – ako smo na listu, vrijednost, inače None
    # children  – indeksi djece u nodes
    nodes = [state]
    levels = [0]
    term_val = [None]
    children = [[]]

    idx = 0
    while idx < len(nodes):
        lvl = levels[idx]

        if term_val[idx] is not None:
            idx += 1
            continue

        if lvl >= max_depth:
            term_val[idx] = 0.0
            idx += 1
            continue

        node = nodes[idx]

        for col in range(7):
            if not node.is_valid_move(col):
                continue

            child = deepcopy(node)
            saved = victory_state
            child.play(col)

            child_idx = len(nodes)
            nodes.append(child)
            levels.append(lvl + 1)
            children.append([])

            if victory_state != 0:
                term_val.append(float(victory_state))
            else:
                term_val.append(None)

            victory_state = saved
            children[idx].append(child_idx)

        idx += 1

    # zbroj vrijednosti
    values = [0.0] * len(nodes)

    for i in range(len(nodes) - 1, -1, -1):
        if term_val[i] is not None:
            values[i] = term_val[i]
        elif children[i]:
            total = 0.0
            for c in children[i]:
                total += values[c]
            values[i] = total / len(children[i])
        else:
            values[i] = 0.0

    return values[0]


def bfs_best_move(game, depth):
    """
    Traži najbolji sljedeći potez
    """
    global victory_state

    valid_moves = [c for c in range(7) if game.is_valid_move(c)]
    if not valid_moves:
        return -1

    best_col = -1
    best_val = -float('inf')

    for col in valid_moves:
        new_game = deepcopy(game)
        saved = victory_state
        new_game.play(col)

        if victory_state == 1: # prvi potez instantna CPU pobjeda
            victory_state = saved
            return col

        if victory_state == -1: # prvi potez instantna Player pobjeda
            val = -1.0
        elif depth <= 1:
            val = 0.0
        else:
            val = bfs_average_eval(new_game, depth - 1) # nema instantne pobjede, traži najbolji potez

        victory_state = saved

        if val > best_val:
            best_val = val
            best_col = col

    return best_col


def bfs_best_move_mpi(game, depth, comm, world_size, world_rank, max_task_depth):
    """
    Kao bfs_best_move, ali delegacija zadataka na druge radnike
    """
    global victory_state

    valid_moves = [c for c in range(7) if game.is_valid_move(c)]
    if not valid_moves:
        return -1

    # instant pobjeda
    for col in valid_moves:
        new_game = deepcopy(game)
        saved = victory_state
        new_game.play(col)
        if victory_state == 1:
            victory_state = saved
            return col
        victory_state = saved

    # nemamo paralelizaciju
    if world_size <= 1 or depth <= 1:
        return bfs_best_move(game, depth)

    # distribucija zadataka
    tasks_sent = 0
    send_reqs = []
    for col in valid_moves:
        dest = (tasks_sent % (world_size - 1)) + 1
        req = comm.isend((deepcopy(game), col, depth, 0), dest=dest)
        send_reqs.append(req)
        tasks_sent += 1
    MPI.Request.Waitall(send_reqs)

    # skupljanje rezultata
    scores = {}
    early_win = None
    remaining = tasks_sent
    while remaining > 0:
        col, score = comm.recv(source=MPI.ANY_SOURCE)
        scores[col] = score
        remaining -= 1
        if score == 1.0 and early_win is None:
            early_win = col

    # pobjeda odmah je uvijek najbolja
    if early_win is not None:
        return early_win
    return max(scores, key=scores.get)


def process_task(comm, game_state, col, depth, level, world_rank, world_size, max_task_depth):
    """
    Odigraj potez, zatim delegiraj dalje ili izračunaj sam ako si list.
    Vraća (col, result) odnosno stupac i vrijednost.
    """
    global victory_state
    saved = victory_state

    game_state.play(col)

    if victory_state != 0:
        result = float(victory_state)
        victory_state = saved
        return (col, result)

    if depth <= 1 or level >= max_task_depth:
        result = bfs_average_eval(game_state, depth - 1)
        victory_state = saved
        return (col, result)

    sub_valid = [c for c in range(7) if game_state.is_valid_move(c)]
    if not sub_valid:
        victory_state = saved
        return (col, 0.0)

    # svi procesi osim sebe i glavnog procesa
    workers = [w for w in range(1, world_size) if w != world_rank]

    if not workers:
        # P = 2 -> sve moramo sami
        total = 0.0
        for c in sub_valid:
            new_game = deepcopy(game_state)
            saved2 = victory_state
            new_game.play(c)
            if victory_state != 0:
                total += float(victory_state)
            else:
                total += bfs_average_eval(new_game, depth - 2)
            victory_state = saved2
        victory_state = saved
        return (col, total / len(sub_valid))

    # delegacija
    total = 0.0
    count = 0
    sub_reqs = []

    for i, c in enumerate(sub_valid):
        dest = workers[i % len(workers)]
        req = comm.isend(
            (deepcopy(game_state), c, depth - 1, level + 1),
            dest=dest,
        )
        sub_reqs.append(req)

    MPI.Request.Waitall(sub_reqs)

    expected = len(sub_reqs)
    while expected > 0:
        status2 = MPI.Status()
        msg2 = comm.recv(source=MPI.ANY_SOURCE, status=status2)
        if len(msg2) == 2:
            _c, score = msg2
            total += score
            count += 1
            expected -= 1
        else:
            # dobili smo zadatak od drugog worker-a, delegiraj dalje
            task_state, task_col, task_depth, task_level = msg2
            task_sender = status2.Get_source()
            sub_result = process_task(comm, task_state, task_col,
                                      task_depth, task_level,
                                      world_rank, world_size, max_task_depth)
            comm.send(sub_result, dest=task_sender)

    result = total / count if count > 0 else 0.0
    victory_state = saved
    return (col, result)


argparser = ArgumentParser()
argparser.add_argument("max_tasks", type=int)
argparser.add_argument("depth", type=int)
args = argparser.parse_args()

MAX_TASK_DEPTH = args.max_tasks

comm = MPI.COMM_WORLD
# ukupan broj procesa
world_size = comm.Get_size()
# moj redni broj
world_rank = comm.Get_rank()

if world_rank == 0:
    game = Connect4Game(player_first=0)
    first_cpu_move = True
    while victory_state == 0:

        if game.player == 1:
            game.board.print_board()
            print("Enter column: ")
            col = int(input())
            try:
                game.play(col)
            except ValueError as e:
                print(e)
                continue
        else:
            if first_cpu_move:
                start_time = time.perf_counter()

            if world_size > 1 and args.depth > 1:
                col = bfs_best_move_mpi(game, args.depth, comm, world_size, world_rank, MAX_TASK_DEPTH)
            else:
                col = bfs_best_move(game, args.depth)

            if col == -1:
                valid = [c for c in range(7) if game.is_valid_move(c)]
                if not valid:
                    continue
                col = valid[randint(0, len(valid) - 1)]
            try:
                game.play(col)
            except ValueError as e:
                continue

            if first_cpu_move:
                elapsed = time.perf_counter() - start_time
                print(f"First CPU move took {elapsed:.6f} s")
                first_cpu_move = False
    # kraj
    if victory_state == 1:
        print("CPU WIN")
    elif victory_state == -1:
        print("Player WIN")
    else:
        print("Nema pobjednika!")
    game.board.print_board()

    # gasi workere
    for i in range(1, world_size):
        comm.send((None, None, -1, -1), dest=i)

else:
    # worker
    while True:
        status = MPI.Status()
        msg = comm.recv(source=MPI.ANY_SOURCE, status=status)
        sender = status.Get_source()

        if len(msg) == 2:
            continue

        game_state, col, depth, level = msg

        if game_state is None:
            break

        result_tuple = process_task(comm, game_state, col, depth, level,
                                     world_rank, world_size, MAX_TASK_DEPTH)
        comm.send(result_tuple, dest=sender)
