import pygame
import random
from rabbit_class import Rabbit
from fox_class import Fox

pygame.init()

WORLD_HEIGHT = 550
WORLD_WIDTH = 650

screen = pygame.display.set_mode((WORLD_WIDTH, WORLD_HEIGHT))
screen.fill((154, 202, 118))
pygame.display.set_caption("Ecosystem Simulator")

world_grid = []
working_list = []

cell_states = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 6]

for row in range(int(WORLD_HEIGHT/25)):
    for column in range(int(WORLD_WIDTH/25)):
        working_list.append(random.choice(cell_states))
    world_grid.append(working_list.copy())
    working_list = []

for row in range(int(WORLD_HEIGHT/25)):
    for column in range(int(WORLD_WIDTH/25)):
        if world_grid[row][column] == 6:
            if world_grid[row-1][column] == 6:
                world_grid[row-1][column] = (6,7)
            else:
                world_grid[row-1][column] = 7
            


tilewidth  = WORLD_WIDTH  / len(world_grid[0])
tileheight = WORLD_HEIGHT / len(world_grid) 

grid_width = len(world_grid[0])
grid_height = len(world_grid)

# goal = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
# world_grid[goal[1]][goal[0]] = 6
# world_grid[goal[1]-1][goal[0]] = 7

shrub_image = pygame.image.load("images/shrub.png").convert_alpha()
shrub_image = pygame.transform.scale(shrub_image, (tileheight, tilewidth))
rock_image = pygame.image.load("images/rock.png").convert_alpha()
rock_image = pygame.transform.scale(rock_image, (tileheight, tilewidth))
clover_image = pygame.image.load("images/clover.png").convert_alpha()
clover_image = pygame.transform.scale(clover_image, (tileheight, tilewidth))
flower_image = pygame.image.load("images/flower_red.png").convert_alpha()
flower_image = pygame.transform.scale(flower_image, (tileheight, tilewidth))
tree_bottom_image = pygame.image.load("images/tree_bottom.png").convert_alpha()
tree_bottom_image = pygame.transform.scale(tree_bottom_image, (tileheight, tilewidth))
tree_top_image = pygame.image.load("images/tree_top.png").convert_alpha()
tree_top_image = pygame.transform.scale(tree_top_image, (tileheight, tilewidth))

def draw_world_grid(world_grid):
    for row in range(len(world_grid)):
        for column in range(len(world_grid[row])):
            if world_grid[row][column] == 1:
                screen.blit(rock_image, (column * tilewidth, row * tileheight))
            if world_grid[row][column] == 2:
                screen.blit(shrub_image, (column * tilewidth, row * tileheight))
            if world_grid[row][column] == 3:
                screen.blit(clover_image, (column * tilewidth, row * tileheight))
            if world_grid[row][column] == 5:
                screen.blit(flower_image, (column * tilewidth, row * tileheight))
            if world_grid[row][column] == 6 or world_grid[row][column] == (6,7):
                screen.blit(tree_bottom_image, (column * tilewidth, row * tileheight))

def draw_world_foreground(world_grid):
    for row in range(len(world_grid)):
        for column in range(len(world_grid[row])):
            if world_grid[row][column] == 7 or world_grid[row][column] == (6,7):
                if (column, row) == rabbit.location or (column, row) == fox.location:
                    # Create a faded copy for transparency
                    faded_top = tree_top_image.copy()
                    faded_top.set_alpha(160)  # slightly transparent
                    screen.blit(faded_top, (column * tilewidth, row * tileheight))
                else:
                    # Draw normal opaque top
                    screen.blit(tree_top_image, (column * tilewidth, row * tileheight))

def place_flowers(count):
    i = 0
    while i < count:
        gx = random.randint(0, grid_width - 1)
        gy = random.randint(0, grid_height - 1)
        tile = world_grid[gy][gx]

        # Only place on walkable ground — not on trees, rocks, shrubs, etc.
        if tile in (0, 3, 5):  # 0=grass, 3=clover, 5=flower (can replace another flower)
            world_grid[gy][gx] = 5
            i += 1

screen.fill((154, 202, 118))

place_flowers(3)

start_rabbit = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
start_fox = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))

goal = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))

rabbit = Rabbit(start_rabbit, goal, tilewidth, tileheight, world_grid, grid_width, grid_height)
rabbit.find_path(rabbit.location, rabbit.goal)
fox = Fox(start_fox, goal, tilewidth, tileheight, world_grid, grid_width, grid_height)
draw_world_grid(world_grid)
rabbit.draw(screen, tilewidth, tileheight)
fox.draw(screen, tilewidth, tileheight)
pygame.display.flip()

running = True
clock = pygame.time.Clock()

# To slow down visible motion — move every X frames
move_delay = 15
frame_counter = 0

rabbit_score = 0

cooldown = 4

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

    frame_counter += 1
    clock.tick(30)


