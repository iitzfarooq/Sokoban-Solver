import core
import pygame
from typing import List, Tuple, Set

DIRECTION_VECTOR = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}

MASKS = {
    "player": 0x08,
    "target": 0x04,
    "boulder": 0x01,
    "wall": 0x02,
}


def generate_indices(shape):
    if not shape:
        yield ()
        return

    first, *rest = shape
    for i in range(first):
        for item in generate_indices(rest):
            yield (i,) + item


class SokobanState:

    def __init__(self, logical_board, player, targets):
        self.logical_board: List[List[int]] = logical_board
        self.player: Tuple[int, int] = player
        self.targets: Set[Tuple[int, int]] = targets

        self.m = len(logical_board)
        self.n = len(logical_board[0]) if logical_board else 0

    def has_player(self, cell):
        x, y = cell
        return self.logical_board[x][y] & MASKS["player"] != 0

    def has_boulder(self, cell):
        x, y = cell
        return self.logical_board[x][y] & MASKS["boulder"] != 0

    def has_wall(self, cell):
        x, y = cell
        return self.logical_board[x][y] & MASKS["wall"] != 0

    def has_target(self, cell):
        x, y = cell
        return self.logical_board[x][y] & MASKS["target"] != 0

    def __hash__(self):
        return hash(
            (tuple(map(tuple, self.logical_board)), self.player, tuple(self.targets))
        )

    def __eq__(self, value):
        if not isinstance(value, SokobanState):
            return False

        return (
            self.logical_board == value.logical_board
            and self.player == value.player
            and self.targets == value.targets
        )

    def __str__(self):
        return f"SokobanState(player={self.player}, targets={self.targets})"

    def clone(self):
        """
        Create a deep copy of the current state.
        """
        new_board = [row.copy() for row in self.logical_board]
        return SokobanState(new_board, self.player, self.targets.copy())


def analyze_move(state: SokobanState, direction: str):
    dx, dy = DIRECTION_VECTOR[direction]
    x, y = state.player
    m, n = len(state.logical_board), len(state.logical_board[0])

    new = (x + dx, y + dy)
    push = (new[0] + dx, new[1] + dy)

    def out(xy):
        return not (0 <= xy[0] < m and 0 <= xy[1] < n)

    if out(new) or state.has_wall(new):
        return "blocked", None

    if state.has_boulder(new):
        if out(push) or state.has_wall(push) or state.has_boulder(push):
            return "blocked", None
        return "push", (new, push)

    return "move", new


def try_move(state: SokobanState, direction: str):
    clone_state = state.clone()
    action, cells = analyze_move(clone_state, direction)

    if action == "blocked":
        return None
    elif action == "push":
        boulder, push = cells
        clone_state.logical_board[boulder[0]][boulder[1]] &= ~MASKS["boulder"]
        clone_state.logical_board[push[0]][push[1]] |= MASKS["boulder"]

    org_cell = state.player
    new_cell = cells if action == "move" else cells[0]

    clone_state.logical_board[org_cell[0]][org_cell[1]] &= ~MASKS["player"]
    clone_state.logical_board[new_cell[0]][new_cell[1]] |= MASKS["player"]
    clone_state.player = new_cell
    return clone_state


def is_victory(state: SokobanState):
    return all(
        state.has_boulder((x, y)) and state.has_target((x, y)) for x, y in state.targets
    )


def get_valid_moves(state: SokobanState):
    valid_moves = []

    for direction in DIRECTION_VECTOR.keys():
        action, cells = analyze_move(state, direction)

        if action != "blocked":
            valid_moves.append(direction)

    return valid_moves


def place_entities(board, entities, mask):
    """
    Place entities on the board.
    """
    for entity in entities:
        x, y = entity
        board[x][y] |= mask


def make_state(description):
    m = len(description)
    n = len(description[0])

    assert all(
        len(row) == n for row in description
    ), "All rows must have the same length."

    logical_board = [[0 for _ in range(n)] for _ in range(m)]

    entities = {
        "player": [],
        "target": [],
        "boulder": [],
        "wall": [],
    }

    cell_iter = (
        (i, j, obj) for i, j in generate_indices((m, n)) for obj in description[i][j]
    )

    for i, j, obj in cell_iter:
        entities[obj].append((i, j))

    for obj, mask in MASKS.items():
        place_entities(logical_board, entities[obj], mask)

    player = entities["player"][0] if entities["player"] else None
    targets = set(entities["target"])

    return SokobanState(logical_board, player, targets)


class Tape:
    pass


class SokobanSolver:
    pass


class Sokoban(core.Layer):
    pass
