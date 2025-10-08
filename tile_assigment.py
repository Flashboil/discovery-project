
def identify_neighbors(worldgrid, x, y):
    empty_neighbor = 0
    tree_neighbor = 0
    rock_neighbor = 0
    water_neighbor = 0

    if x != 0 and y != 0:
        if worldgrid[y-1][x-1] == 0:
            empty_neighbor += 1

for row in range(len(world_grid)):
    for column in range(len(world_grid[row])):
        if world_grid[row][column] == 0:
            pygame.draw.rect(screen, (0, 0, 0), ((column * tilewidth), (row * tileheight), tilewidth, tileheight))
        elif world_grid[row][column] == 1:
            pygame.draw.rect(screen, (255, 255, 255), ((column * tileheight), (row * tilewidth), tilewidth, tileheight))
        elif world_grid[row][column] == 2:
            pygame.draw.rect(screen, (182, 184, 221), ((column * tileheight), (row * tilewidth), tilewidth, tileheight))
        elif world_grid[row][column] == 3:
            pygame.draw.rect(screen, (10, 20, 255), ((column * tileheight), (row * tilewidth), tilewidth, tileheight))