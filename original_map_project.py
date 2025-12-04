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

required_flowers = 8  # goal for the day


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
    2, 2,   # shrub
    1,  # rock
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
    """Draw tree tops as a second pass. Fade if a rabbit or the fox is under them."""
    for row in range(len(world_grid)):
        for col in range(len(world_grid[row])):
            tile = world_grid[row][col]

            if tile == 7 or tile == (6, 7):
                x = col * tilewidth
                y = row * tileheight

                # Check if ANY rabbit is here
                rabbit_under = any(r.location == (col, row) for r in rabbits)

                # Check if fox is here
                fox_under = (col, row) == fox.location

                if rabbit_under or fox_under:
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
place_flowers(6)


# ============================================================
# 7. CREATURE INITIALIZATION
# ============================================================

# Different random starts for each rabbit
start_rabbit1 = (
    random.randint(0, grid_width - 1),
    random.randint(0, grid_height - 1)
)
start_rabbit2 = (
    random.randint(0, grid_width - 1),
    random.randint(0, grid_height - 1)
)

start_rabbit3 = (
    random.randint(0, grid_width - 1),
    random.randint(0, grid_height - 1)
)

start_fox = (
    random.randint(0, grid_width - 1),
    random.randint(0, grid_height - 1)
)

goal1 = (
    random.randint(0, grid_width - 1),
    random.randint(0, grid_height - 1)
)
goal2 = (
    random.randint(0, grid_width - 1),
    random.randint(0, grid_height - 1)
)
goal3 = (
    random.randint(0, grid_width - 1),
    random.randint(0, grid_height - 1)
)

rabbit1 = Rabbit(start_rabbit1, goal1, tilewidth, tileheight,
                 world_grid, grid_width, grid_height)
rabbit1.find_path(rabbit1.location, rabbit1.goal)

rabbit2 = Rabbit(start_rabbit2, goal2, tilewidth, tileheight,
                 world_grid, grid_width, grid_height)
rabbit2.find_path(rabbit2.location, rabbit2.goal)

rabbit3 = Rabbit(start_rabbit3, goal3, tilewidth, tileheight,
                 world_grid, grid_width, grid_height)
rabbit3.find_path(rabbit3.location, rabbit3.goal)

# List of all rabbits
rabbits = [rabbit1, rabbit2, rabbit3]
rabbitspop = [rabbit1, rabbit2, rabbit3]

fox = Fox(start_fox, None, tilewidth, tileheight,
          world_grid, grid_width, grid_height)

# Place rabbit1's burrow (warren)
rabbit_home = rabbit1.location
world_grid[rabbit_home[1]][rabbit_home[0]] = 9


# ============================================================
# 8. INITIAL DRAW
# ============================================================

draw_world_grid(world_grid)

for r in rabbits:
    r.draw(screen, tilewidth, tileheight)

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
    draw_world_grid(world_grid)

    # compute fox delay once per frame (used below)
    fox_delay = fox.speed

    # -------------------------
    # Update each rabbit
    # -------------------------
    for r in rabbits:
        rabbit_delay = r.speed

        r.update_speed()
        # === Rabbit Behavior ===
        if frame_counter % rabbit_delay == 0:
            r.follow_path()

            # If fox is near, flee instead
            if r.detect_fox(fox.location):
                escape_goal = r.find_escape_goal(fox.location, grid_width, grid_height, world_grid)
                if escape_goal:
                    r.state = "flee"
                    r.find_path(r.location, escape_goal)
                    r.boost()
                elif r.state == "flee" and r.is_safe(fox.location):
                    r.state = "recover"
                    r.path = []
                    r.goal = None
                    r.recovery_timer = r.recovery_delay

            elif r.state == "wander" and not r.path:
                r.wander(fox.path)
                r.find_path(r.location, r.goal)

            elif r.detect_flower() and r.state == "wander":
                r.path = []
                r.state = "seek"
                r.find_path(r.location, r.detect_flower())

            if r.state == "recover":
                r.recovery_timer -= 1
                if r.recovery_timer <= 0:
                    r.state = "wander"
                    r.wander(fox.path)
                    if not r.path:
                        # fallback in case wander picked an invalid goal
                        r.goal = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
                        r.find_path(r.location, r.goal)

            # === Rabbit failsafe ===
            if not r.path and r.state in ("seek", "flee", "recover"):
                r.state = "wander"
                r.wander(fox.path)
                r.find_path(r.location, r.goal)

            # Check win/lose conditions (per-rabbit behavior for returning home)
            if rabbit_score >= required_flowers and r.state != "return_home":
                print("Enough flowers collected! Returning home.")
                r.state = "return_home"
                r.find_path(r.location, rabbit_home)

            elif day_timer <= 0 and r.state != "return_home":
                print("Day ended! Returning home.")
                r.state = "return_home"
                r.find_path(r.location, rabbit_home)

            # Track per-rabbit success without ending the game immediately
            if r.state == "return_home" and r.location == rabbit_home:
                r.state = "safe"   # mark rabbit as home and safe
                rabbits.remove(r)
                print("Rabbit made it home safely!")

                # -------------------------
                # END CONDITION (ALL RABBITS RESOLVED)
                # -------------------------
                # All rabbits must be either:
                #   - safely at home (state == "safe")
                #   - or removed because they were caught
                if all( (r.state == "safe") for r in rabbitspop ):
                    print("All surviving rabbits are safely home!")
                    print(f"Final Score: {rabbit_score}")
                    print(f"{len(rabbitspop)} rabbits survived.")
                    running = False


    # -------------------------
    # Fox Behavior (multi-rabbit aware)
    # -------------------------
    if frame_counter % fox_delay == 0:
        # 1. Wandering behavior
        if fox.state == "wander":
            # Occasionally pick a new random goal
            if not fox.path:
                fox.wander()
                if fox.goal:
                    fox.find_path(fox.location, fox.goal)


            # Check visible rabbits
            visible = [rr for rr in rabbits if fox.detect_rabbit(rr.location)]
            if visible:
                # pick the closest visible rabbit
                target = min(visible, key=lambda rr: fox.octile_distance(fox.location, rr.location))
                fox.state = "hunt"
                fox.goal = target.location
                fox.find_path(fox.location, fox.goal)

        # 2. Hunting behavior
        elif fox.state == "hunt":
            # Check if any rabbit is visible this tick
            visible = [rr for rr in rabbits if fox.detect_rabbit(rr.location)]
            if visible:
                target = min(visible, key=lambda rr: fox.octile_distance(fox.location, rr.location))
                fox.goal = target.location
                fox.find_path(fox.location, fox.goal)
                fox.memory_timer = fox.memory_duration  # refresh memory
            else:
                fox.memory_timer -= 1
                if fox.memory_timer <= 0:
                    fox.state = "wander"
                    fox.path = []
                    fox.goal = None
                    fox.wander()  # pick a new random wander goal
                else:
                    # Keep moving toward last known rabbit location    
                    fox.find_path(fox.location, fox.goal)

        fox.follow_path()

    # -------------------------
    # Flower collection (work per-rabbit)
    # -------------------------
    for r in rabbits:
        x, y = r.location
        if 0 <= y < len(world_grid) and 0 <= x < len(world_grid[0]):
            if world_grid[y][x] == 5:
                world_grid[y][x] = 0
                place_flowers(1)
                r.state = "wander"
                rabbit_score += 1
                print(rabbit_score)

    # -------------------------
    # Fox catches a rabbit? (check all rabbits)
    # -------------------------
    for r in list(rabbits):
        if fox.location == r.location:
            print("A rabbit was caught!")
            rabbits.remove(r)
            rabbitspop.remove(r)

            # --- FIX FREEZE: reset fox ----
            fox.state = "wander"
            fox.goal = None
            fox.path = []
            fox.memory_timer = fox.memory_duration
            fox.wander()
            # ------------------------------

            if len(rabbits) == 0:
                print("All rabbits are caught!")
                print(f"Final Score: {rabbit_score}")
                running = False



    # -------------------------
    # DRAWING
    # -------------------------
    for r in rabbits:
        r.draw(screen, tilewidth, tileheight)

    fox.draw(screen, tilewidth, tileheight)
    draw_world_foreground(world_grid)
    pygame.display.flip()

    # -------------------------
    # END OF FRAME housekeeping
    # -------------------------
    day_timer -= 1

    if frame_counter % 30 == 0:
        print("Time left:", day_timer // 30)

    frame_counter += 1
    clock.tick(30)
