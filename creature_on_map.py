import pygame
import random
from rabbit_class import Rabbit
from fox_class import Fox

pygame.init()

WORLD_HEIGHT = 500
WORLD_WIDTH = 500

screen = pygame.display.set_mode((WORLD_WIDTH, WORLD_HEIGHT))
screen.fill((154, 202, 118))
pygame.display.set_caption("Ecosystem Simulator")

world_grid = []
working_list = []

cell_states = [0, 0, 0, 0, 0, 0, 0, 0, 1, 2]

for row in range(int(WORLD_HEIGHT/25)):
    for column in range(int(WORLD_WIDTH/25)):
        working_list.append(random.choice(cell_states))
    world_grid.append(working_list.copy())
    working_list = []

tilewidth  = WORLD_WIDTH  / len(world_grid[0])
tileheight = WORLD_HEIGHT / len(world_grid) 

grid_width = len(world_grid[0])
grid_height = len(world_grid)

shrub_image = pygame.image.load("images/shrub.png").convert_alpha()
shrub_image = pygame.transform.scale(shrub_image, (tileheight, tilewidth))
rock_image = pygame.image.load("images/rock.png").convert_alpha()
rock_image = pygame.transform.scale(rock_image, (tileheight, tilewidth))
clover_image = pygame.image.load("images/clover.png").convert_alpha()
clover_image = pygame.transform.scale(clover_image, (tileheight, tilewidth))
flower_image = pygame.image.load("images/flower_red.png").convert_alpha()
flower_image = pygame.transform.scale(flower_image, (tileheight, tilewidth))

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

screen.fill((154, 202, 118))

goal = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
world_grid[goal[1]][goal[0]] = 5
start_rabbit = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
start_fox = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))

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

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill background once per frame
    screen.fill((154, 202, 118))
    # screen.fill((0, 0, 0))
    draw_world_grid(world_grid)


    rabbit_delay = 13
    fox_delay = 12  # smaller number = faster

    if frame_counter % rabbit_delay == 0:
        rabbit.follow_path()

    if frame_counter % fox_delay == 0:
        if frame_counter % (rabbit_delay * 2) == 0:
            rabbit_future = rabbit.path[rabbit.path_index + 1] if rabbit.path_index + 1 < len(rabbit.path) else rabbit.location
            # rabbit_future = rabbit.location
            fox.find_path(fox.location, rabbit_future)
        fox.follow_path()

    if fox.location == rabbit.location:
        running = False

    rabbit.draw(screen, tilewidth, tileheight)
    fox.draw(screen, tilewidth, tileheight)
    pygame.display.flip()

    frame_counter += 1
    clock.tick(30)  # 30 FPS for smooth drawing


