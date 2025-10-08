import pygame
import random

pygame.init()

class Rabbit:
    def __init__(self):
        pass

WORLD_HEIGHT = 600
WORLD_WIDTH = 600



screen = pygame.display.set_mode((WORLD_WIDTH, WORLD_HEIGHT))
screen.fill((154, 202, 118))
pygame.display.set_caption("Ecosystem Simulator")

world_grid = []
working_list = []

cell_states = [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 3]

for row in range(int(WORLD_HEIGHT/25)):
    for column in range(int(WORLD_WIDTH/25)):
        working_list.append(random.choice(cell_states))
    world_grid.append(working_list.copy())
    working_list = []

running = True

tilewidth  = WORLD_WIDTH  / len(world_grid[0])
tileheight = WORLD_HEIGHT / len(world_grid) 

shrub_image = pygame.image.load("shrub.png").convert_alpha()
shrub_image = pygame.transform.scale(shrub_image, (tileheight, tilewidth))
rock_image = pygame.image.load("rock.png").convert_alpha()
rock_image = pygame.transform.scale(rock_image, (tileheight, tilewidth))
clover_image = pygame.image.load("clover.png").convert_alpha()
clover_image = pygame.transform.scale(clover_image, (tileheight, tilewidth))

for row in range(len(world_grid)):
    for column in range(len(world_grid[row])):
        if world_grid[row][column] == 1:
            screen.blit(rock_image, (column * tilewidth, row * tileheight))
        if world_grid[row][column] == 2:
            screen.blit(shrub_image, (column * tilewidth, row * tileheight))
        if world_grid[row][column] == 3:
            screen.blit(clover_image, (column * tilewidth, row * tileheight))

pygame.display.flip()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
