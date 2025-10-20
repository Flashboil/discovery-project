import random
import numpy
import heapq
import pygame

class Rabbit:
    def __init__(self, start, goal, tilewidth, tileheight, world_grid, world_width, world_height):
        self.world_grid = world_grid
        self.world_width = world_width
        self.world_height = world_height
        self.location = start
        self.goal = goal
        self.path = []
        self.path_index = 0
        self.image = pygame.image.load("images/rabbit_red.png").convert_alpha()
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
        came_from = {}
        g_score = {start: 0}
        # f = g + h; push (f, node)
        heapq.heappush(open_heap, (self.octile_distance(start, goal), start))

        closed_set = set()

        while open_heap:
            current_f, current = heapq.heappop(open_heap)

            if current == goal:
                self.path = self.reconstruct_path(goal, came_from)
                # set index to 1 so we DON'T try to "move" to the start tile again
                self.path_index = 1 if len(self.path) > 1 else 0
                return self.path

            if current in closed_set:
                continue
            closed_set.add(current)

            current_g = g_score[current]

            for (neighbor, step_cost) in self.get_neighbors(current, goal):
                tentative_g = current_g + step_cost

                # only consider this neighbor if it's a better path than previously known
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self.octile_distance(neighbor, goal)
                    heapq.heappush(open_heap, (f, neighbor))

        # no path found
        self.path = []
        self.path_index = 0
        return self.path


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
            if 0 <= neighbor_x < self.world_width and 0 <= neighbor_y < self.world_height:
                if self.world_grid[neighbor_y][neighbor_x] not in (0, 3, 5): 
                    continue
                cost = 1.414 if dx != 0 and dy != 0 else 1
                locals.append(((neighbor_x, neighbor_y), cost))

        return locals