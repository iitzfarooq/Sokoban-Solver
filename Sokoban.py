import core
import os
import pygame
from typing import List, Tuple, Set
from Grid import description

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
app_config = {
    "working_directory": WORKING_DIR,
    "size": (1280, 720),
    "title": "Sokoban",
    "fps": 60,
}

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

class SokobanView:
    def __init__(self, cell_len, resource_manager: core.ResourceManager):
        self._cell_len = cell_len
        self.resource_manager = resource_manager

        assets_dir = os.path.join(WORKING_DIR, "assets")
        assets_path = {
            "grass": os.path.join(assets_dir, "grass.png"),
            "player": os.path.join(assets_dir, "player.png"),
            "boulder": os.path.join(assets_dir, "boulder.png"),
            "target": os.path.join(assets_dir, "target.png"),
            "wall": os.path.join(assets_dir, "wall.png"),
        }
        
        self.original_images = {
            name: self.resource_manager.load_image(name, path, convert_alpha=True)
            for name, path in assets_path.items()
        }
        
        self.assets = {
            name: pygame.transform.smoothscale(img, (self.cell_len, self.cell_len))
            for name, img in self.original_images.items()
        }
        
    @property
    def cell_len(self):
        return self._cell_len
    
    @cell_len.setter
    def cell_len(self, value):
        assert value > 0, "Cell length must be positive."
        
        self._cell_len = value
        self.assets = {
            name: pygame.transform.smoothscale(img, (self.cell_len, self.cell_len))
            for name, img in self.original_images.items()
        }
    
        
    def render_view(self, state: SokobanState):
        # m = rows, n = cols
        board_width = state.n * self.cell_len
        board_height = state.m * self.cell_len
        
        board_surface = pygame.Surface((board_width, board_height), pygame.SRCALPHA, 32)
        board_surface.fill((0, 0, 0, 0))
        
        for i, j in generate_indices((state.m, state.n)):
            cell = state.logical_board[i][j]
            x, y = j * self.cell_len, i * self.cell_len
            
            board_surface.blit(self.assets["grass"], (x, y))
            if cell & MASKS["target"]:
                board_surface.blit(self.assets["target"], (x, y))
            if cell & MASKS["player"]:
                board_surface.blit(self.assets["player"], (x, y))
            if cell & MASKS["boulder"]:
                board_surface.blit(self.assets["boulder"], (x, y))
            if cell & MASKS["wall"]:
                board_surface.blit(self.assets["wall"], (x, y))
                
        return board_surface

def rescale_surface_to_fit(surface: pygame.Surface, shape):
    """
    Rescale the board surface to fit within the given shape (width, height),
    preserving aspect ratio.
    """
    if not shape:
        return surface

    target_width, target_height = shape
    surface_width, surface_height = surface.get_size()

    # Compute scale factors for width and height
    scale_x = target_width / surface_width
    scale_y = target_height / surface_height

    # Preserve aspect ratio — take the smaller scaling factor
    scale_factor = min(scale_x, scale_y)

    # Compute new size while preserving aspect ratio
    new_width = int(surface_width * scale_factor)
    new_height = int(surface_height * scale_factor)

    # Use smooth scaling for better quality
    return pygame.transform.smoothscale(surface, (new_width, new_height))

class Tape:
    pass


class SokobanSolver:
    pass

class SokobanLayer(core.Layer):
    def __init__(self):
        core.Layer.__init__(self, "SokobanLayer")
        self.state = None
        self.view = None
        
        self.resource_manager = core.ResourceManager()
        
        self.left_size = 680, 680
        self.left_center = 360, 360
        
        self.right_size = 520, 680
        self.right_center = 1000, 360
        
        # self.solver = None
        # self.tape = None
    
    def on_attach(self):
        self.state = make_state(description)
        self.view = SokobanView(25, self.resource_manager)
        # self.solver = SokobanSolver()
        # self.tape = Tape()
        
    def on_detach(self): 
        self.resource_manager.clear()
        
    def on_update(self, dt):
        pass
    
    def on_event(self, event):
        pass
    
    def on_render(self, renderer: core.Renderer):
        def get_top_left(center, size):
            return center[0] - size[0] // 2, center[1] - size[1] // 2

        def draw_section(center, size, surface_to_draw):
            pos = get_top_left(center, surface_to_draw.get_size())
            renderer.submit_surface(surface_to_draw, *pos)

        # Create and clear main screen surface
        screen_surface = renderer.create_surface(*app_config["size"])
        screen_surface.fill((255, 255, 255))  # White background
        renderer.submit_surface(screen_surface)

        # Render board
        board_surface = self.view.render_view(self.state)
        scaled_board = rescale_surface_to_fit(board_surface, self.left_size)

        # Draw board in left section
        draw_section(self.left_center, self.left_size, scaled_board)
        

class Sokoban(core.Application):
    def __init__(self):
        super().__init__(app_config)
        
    def on_start(self):
        sokoban_layer = SokobanLayer()
        self.layer_stack.push_layer(sokoban_layer)
        
app = Sokoban()
core.main(app)