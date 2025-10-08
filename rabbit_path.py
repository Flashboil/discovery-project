import random
import numpy
import heapq
import pygame

WORLD_HEIGHT = 9
WORLD_WIDTH = 9

world_grid = []
working_list = []

cell_states = [0, 0, 0, 0, 1, 2]

for row in range(int(WORLD_HEIGHT)):
    for column in range(int(WORLD_WIDTH)):
        working_list.append(random.choice(cell_states))
    world_grid.append(working_list.copy())
    working_list = []

class Rabbit:
    def __init__(self, start, goal, tilewidth, tileheight):
        self.location = start
        self.goal = goal
        self.path = []
        self.path_index = 0
        self.image = pygame.image.load("rabbit.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (tilewidth, tileheight))
    
    def draw(self, screen, tile_width, tile_height):
        pixel_x = self.location[0] * tile_width
        pixel_y = self.location[1] * tile_height

        screen.blit(self.image, (pixel_x, pixel_y))

    def octile_distance(self, a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])

        return (numpy.sqrt(2) * min(dx, dy)) + (max(dx, dy) - min(dx, dy))
    
    def find_path(self, start, goal):
        
        open_heap = []
        closed_set = set()
        came_from = {}

        heapq.heappush(open_heap, (self.octile_distance(start, goal), 0, start, None))

        current_g = 0

        while open_heap:
            current_f, current_g, current, parent = heapq.heappop(open_heap)

            if current == goal:
                if current == goal:
                    self.path = self.reconstruct_path(goal, came_from)
                    self.path_index = 0
                    return self.path
            else:
                closed_set.add((current))

                for (neighbor, step_cost) in self.get_neighbors(current, goal):
                    if neighbor in closed_set:
                        continue

                    new_g = current_g + step_cost
                    new_h = self.octile_distance(neighbor, goal)
                    new_f = new_g + new_h

                    came_from[neighbor] = current

                    heapq.heappush(open_heap, (new_f, new_g, neighbor, current))

    def reconstruct_path(self, goal, came_from):
        path = []
        current = goal

        while current is not None:
            path.append(current)
            current = came_from.get(current)
        
        path.reverse()
        return path
    
    def follow_path(self):
        if self.path == [] or self.path_index >= len(self.path):
            return
        
        next_tile = self.path[self.path_index]

        self.location = next_tile

        self.path_index += 1

        if self.path_index >= len(self.path):
            self.path = []

    def get_neighbors(self, node, goal):
        neighbors = [(-1,-1), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1)]
        locals = []

        current_x, current_y = node

        for dx, dy in neighbors:
            neighbor_x = current_x + dx
            neighbor_y = current_y + dy
            if 0 <= neighbor_x < WORLD_WIDTH and 0 <= neighbor_y < WORLD_HEIGHT:
                if world_grid[neighbor_y][neighbor_x] not in (0, 2, 3): 
                    continue
                cost = 1.414 if dx != 0 and dy != 0 else 1
                locals.append(((neighbor_x, neighbor_y), cost))

        return locals
    
    def print_map_with_path(self, start, goal, path=None):
        # Make a copy so we don't modify the original grid
        display_grid = [row.copy() for row in world_grid]

        # Mark the path
        if path:
            for x, y in path:
                if (x, y) != start and (x, y) != goal:
                    display_grid[y][x] = "*"

        # Mark start and goal
        sx, sy = start
        gx, gy = goal
        display_grid[sy][sx] = "R"
        display_grid[gy][gx] = "G"

        # Print the grid row by row
        for row in display_grid:
            print(" ".join(str(cell) for cell in row))