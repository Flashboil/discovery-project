import pygame
import random
from rabbit_class import Rabbit
from fox_class import Fox

pygame.init()

# ============================================================
# 1. GAME CONFIGURATION
# ============================================================

WORLD_HEIGHT = 550
WORLD_WIDTH = 650
TILE_SIZE = 25  # implicit from world generation grid spacing

day_length = 60 * 30  # 30 seconds @ 60 fps
day_timer = day_length

required_flowers = 5  # goal for the day


# ============================================================
# 2. SCREEN SETUP
# ============================================================

screen = pygame.display.set_mode((WORLD_WIDTH, WORLD_HEIGHT))
screen.fill((154, 202, 118))  # background color
pygame.display.set_caption("Ecosystem Simulator")


# ============================================================
# 3. WORLD GENERATION
# ============================================================

# Tile codes:
# 0 = empty grass
# 1 = rock
# 2 = shrub
# 3 = clover
# 5 = flower
# 6 = tree bottom
# 7 = tree top
# (6,7) = linked tree bottom+top stack
# 9 = rabbit warren (home)

world_grid = []
working_list = []

# Weighted tile distribution — most slots are 0 for empty ground
cell_states = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # lots of empty ground
    2,   # shrub
    1, 1,  # rock
    6   # tree bottom (tree top placed later)
]

rows = WORLD_HEIGHT // TILE_SIZE
cols = WORLD_WIDTH // TILE_SIZE

# --- Generate base terrain ---
for row in range(rows):
    for col in range(cols):
        working_list.append(random.choice(cell_states))
    world_grid.append(working_list.copy())
    working_list = []

# --- Add tree tops (7) above tree bottoms (6) ---
for row in range(1, rows):  # start at row 1 to avoid row-1 out of bounds
    for col in range(cols):
        if world_grid[row][col] == 6:  # tree bottom
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
    """Draw all ground-level tiles."""
    for row in range(len(world_grid)):
        for col in range(len(world_grid[row])):
            tile = world_grid[row][col]
            x = col * tilewidth
            y = row * tileheight

            if tile == 1:
                screen.blit(rock_image, (x, y))
            elif tile == 2:
                screen.blit(shrub_image, (x, y))
            elif tile == 3:
                screen.blit(clover_image, (x, y))
            elif tile == 5:
                screen.blit(flower_image, (x, y))
            elif tile == 6 or tile == (6, 7):
                screen.blit(tree_bottom_image, (x, y))
            elif tile == 9:
                screen.blit(warren_image, (x, y))


def draw_world_foreground(world_grid):
    """Draw tree tops as a second pass. Fade if rabbit/fox under them."""
    for row in range(len(world_grid)):
        for col in range(len(world_grid[row])):
            tile = world_grid[row][col]
            if tile == 7 or tile == (6, 7):
                x = col * tilewidth
                y = row * tileheight

                if (col, row) == rabbit.location or (col, row) == fox.location:
                    faded = tree_top_image.copy()
                    faded.set_alpha(160)
                    screen.blit(faded, (x, y))
                else:
                    screen.blit(tree_top_image, (x, y))


# ============================================================
# 6. RESOURCE / FOOD PLACEMENT
# ============================================================

def place_flowers(count):
    """Randomly place flowers on walkable tiles."""
    planted = 0
    while planted < count:
        gx = random.randint(0, grid_width - 1)
        gy = random.randint(0, grid_height - 1)
        tile = world_grid[gy][gx]

        if tile in (0, 3, 5):  # walkable ground
            world_grid[gy][gx] = 5
            planted += 1


screen.fill((154, 202, 118))
place_flowers(3)


# ============================================================
# 7. CREATURE INITIALIZATION
# ============================================================

start_rabbit = (
    random.randint(0, grid_width - 1),
    random.randint(0, grid_height - 1)
)
start_fox = (
    random.randint(0, grid_width - 1),
    random.randint(0, grid_height - 1)
)

goal = (
    random.randint(0, grid_width - 1),
    random.randint(0, grid_height - 1)
)

rabbit = Rabbit(start_rabbit, goal, tilewidth, tileheight, world_grid, grid_width, grid_height)
rabbit.find_path(rabbit.location, rabbit.goal)

fox = Fox(start_fox, goal, tilewidth, tileheight, world_grid, grid_width, grid_height)


# Place the rabbit’s home (warren)
rabbit_home = rabbit.location
world_grid[rabbit_home[1]][rabbit_home[0]] = 9


# ============================================================
# 8. INITIAL DRAW
# ============================================================

draw_world_grid(world_grid)
rabbit.draw(screen, tilewidth, tileheight)
fox.draw(screen, tilewidth, tileheight)
pygame.display.flip()


# ============================================================
# 9. GAME LOOP SETUP VARIABLES
# ============================================================

running = True
clock = pygame.time.Clock()

move_delay = 15  # frames per movement step
frame_counter = 0

rabbit_score = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill background once per frame
    screen.fill((154, 202, 118))
    # screen.fill((0, 0, 0))
    draw_world_grid(world_grid)


    rabbit_delay = rabbit.speed
    fox_delay = fox.speed

    rabbit.update_speed()
    # === Rabbit Behavior ===
    if frame_counter % rabbit_delay == 0:
        rabbit.follow_path()

        # If fox is near, flee instead
        if rabbit.detect_fox(fox.location):
            escape_goal = rabbit.find_escape_goal(fox.location, grid_width, grid_height, world_grid)
            if escape_goal:
                rabbit.state = "flee"
                rabbit.find_path(rabbit.location, escape_goal)
                rabbit.boost()
            elif rabbit.state == "flee" and rabbit.is_safe(fox.location):
                rabbit.state = "recover"
                rabbit.path = []
                rabbit.goal = None
                rabbit.recovery_timer = rabbit.recovery_delay

        elif rabbit.state == "wander" and not rabbit.path:
            rabbit.wander(fox.path)
            rabbit.find_path(rabbit.location, rabbit.goal)

        elif rabbit.detect_flower() and rabbit.state == "wander":
            rabbit.path = []
            rabbit.state = "seek"
            rabbit.find_path(rabbit.location, rabbit.detect_flower())

        if rabbit.state == "recover":
            rabbit.recovery_timer -= 1
            if rabbit.recovery_timer <= 0:
                rabbit.state = "wander"
                rabbit.wander(fox.path)
                if not rabbit.path:
                    # fallback in case wander picked an invalid goal
                    rabbit.goal = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
                    rabbit.find_path(rabbit.location, rabbit.goal)


        # === Rabbit failsafe ===
        if not rabbit.path and rabbit.state in ("seek", "flee", "recover"):
            rabbit.state = "wander"
            rabbit.wander(fox.path)
            rabbit.find_path(rabbit.location, rabbit.goal)

        # Check win/lose conditions
        if rabbit_score >= required_flowers and rabbit.state != "return_home":
            print("Enough flowers collected! Returning home.")
            rabbit.state = "return_home"
            rabbit.find_path(rabbit.location, rabbit_home)

        elif day_timer <= 0 and rabbit.state != "return_home":
            print("Day ended! Returning home.")
            rabbit.state = "return_home"
            rabbit.find_path(rabbit.location, rabbit_home)

        if rabbit.state == "return_home" and rabbit.location == rabbit_home:
            print("Rabbit made it home safely!")
            if rabbit_score >= required_flowers:
                print("You survived the day!")
            else:
                print("Not enough food collected. Game over.")
            running = False



    # === Fox Behavior ===
    if frame_counter % fox_delay == 0:

        # 1. Wandering behavior
        if fox.state == "wander":
            # Occasionally pick a new random goal
            if not fox.path:
                fox.wander()

            # Check if rabbit is visible
            if fox.detect_rabbit(rabbit.location):
                fox.state = "hunt"
                fox.goal = rabbit.location
                fox.find_path(fox.location, fox.goal)

        # 2. Hunting behavior
        elif fox.state == "hunt":
            if fox.detect_rabbit(rabbit.location):
                fox.goal = rabbit.location
                fox.find_path(fox.location, fox.goal)
                fox.memory_timer = fox.memory_duration  # refresh memory
            else:
                fox.memory_timer -= 1
                if fox.memory_timer <= 0:
                    fox.state = "wander"
                    fox.path = []
                    fox.goal = None
                    fox.wander()  # 🦊 immediately pick a new random wander goal
                else:
                    # Keep moving toward last known rabbit location
                    fox.find_path(fox.location, fox.goal)

            # Failsafe: If no valid path, switch back to wandering
            if not fox.path:
                fox.state = "wander"
                fox.path = []
                fox.goal = None
                fox.wander()


        fox.follow_path()

    if world_grid[rabbit.location[1]][rabbit.location[0]] == 5:
        world_grid[rabbit.location[1]][rabbit.location[0]] = 0
        place_flowers(1)
        rabbit.state = "wander"
        rabbit_score += 1
        print(rabbit_score)

    if fox.location == rabbit.location:
        print("Game End!")
        print(f"Score: {rabbit_score}")
        running = False

    rabbit.draw(screen, tilewidth, tileheight)
    fox.draw(screen, tilewidth, tileheight)
    draw_world_foreground(world_grid)
    pygame.display.flip()

    day_timer -= 1

    if frame_counter % 30 == 0:
        print("Time left:", day_timer // 30)

    frame_counter += 1
    clock.tick(30)


