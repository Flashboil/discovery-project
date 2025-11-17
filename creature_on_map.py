import pygame
import random
from rabbit import Rabbit
from fox import Fox

pygame.init()

# ============================================================
# 1. GAME CONFIGURATION
# ============================================================

WORLD_HEIGHT = 550
WORLD_WIDTH = 650
TILE_SIZE = 25  # grid spacing

day_length = 60 * 30  # 30 seconds at 60 FPS
day_timer = day_length

required_flowers = 5  # goal for the day

# ============================================================
# 2. SCREEN SETUP
# ============================================================

screen = pygame.display.set_mode((WORLD_WIDTH, WORLD_HEIGHT))
screen.fill((154, 202, 118))
pygame.display.set_caption("Ecosystem Simulator")

# ============================================================
# 3. WORLD GENERATION
# ============================================================

world_grid = []
working_list = []

cell_states = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # mostly empty grass
    2,  # shrub
    1, 1,  # rock
    6  # tree bottom
]

rows = WORLD_HEIGHT // TILE_SIZE
cols = WORLD_WIDTH // TILE_SIZE

# Base terrain
for row in range(rows):
    for col in range(cols):
        working_list.append(random.choice(cell_states))
    world_grid.append(working_list.copy())
    working_list = []

# Add tree tops (7) above tree bottoms (6)
for row in range(1, rows):
    for col in range(cols):
        if world_grid[row][col] == 6:
            above = world_grid[row - 1][col]
            if above == 6:
                world_grid[row - 1][col] = (6, 7)
            else:
                world_grid[row - 1][col] = 7

# Grid geometry
grid_width = cols
grid_height = rows
tilewidth = WORLD_WIDTH / grid_width
tileheight = WORLD_HEIGHT / grid_height

# ============================================================
# 4. ASSET LOADING
# ============================================================

def load_and_scale(path):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (tileheight, tilewidth))

shrub_image       = load_and_scale("images/shrub.png")
rock_image        = load_and_scale("images/rock.png")
clover_image      = load_and_scale("images/clover.png")
flower_image      = load_and_scale("images/flower_red.png")
tree_bottom_image = load_and_scale("images/tree_bottom.png")
tree_top_image    = load_and_scale("images/tree_top.png")
warren_image      = load_and_scale("images/warren.png")

# ============================================================
# 5. WORLD DRAW FUNCTIONS
# ============================================================

def draw_world_grid(world_grid):
    for row in range(len(world_grid)):
        for col in range(len(world_grid[row])):
            tile = world_grid[row][col]
            x
