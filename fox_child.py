import pygame
import random
from creature_parent import Creature

class Fox(Creature):
    def __init__(self, start, goal, tilewidth, tileheight,
                 world_grid, world_width, world_height):

        super().__init__(start, goal, tilewidth, tileheight,
                         world_grid, world_width, world_height)

        # Override Creature image with fox sprite
        self.image = pygame.image.load("images/fox_red.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (tilewidth, tileheight))

        # Fox-specific behavior
        self.memory_timer = 0
        self.memory_duration = 60    # frames fox remembers last rabbit sighting


    # --- Fox-specific detection (special case of detect_entity) ---
    def detect_rabbit(self, rabbit_list):
        closest_rabbit = None
        closest_dist = float('inf')

        for rabbit in rabbit_list:
            if self.detect_entity(rabbit.location):
                d = self.octile_distance(self.location, rabbit.location)
                if d < closest_dist:
                    closest_dist = d
                    closest_rabbit = rabbit

        return closest_rabbit  # may be None



    # --- Fox-specific diagonal movement rules ---
    def get_neighbors(self, node, goal):
        neighbors = [(-1,-1), (0,-1), (1,-1),
                     (-1,0),          (1,0),
                     (-1,1), (0,1),  (1,1)]

        locals = []
        x, y = node

        for dx, dy in neighbors:
            nx, ny = x + dx, y + dy

            if 0 <= nx < self.world_width and 0 <= ny < self.world_height:
                if self.world_grid[ny][nx] not in (0, 3, 5, 7, 9):
                    continue

                # Fox-specific diagonal blocking
                if dx != 0 and dy != 0:
                    if (self.world_grid[y][x + dx] not in (0, 3, 5, 7, 9) or
                        self.world_grid[y + dy][x] not in (0, 3, 5, 7, 9)):
                        continue

                cost = 1.414 if dx != 0 and dy != 0 else 1
                locals.append(((nx, ny), cost))

        return locals


    # --- Optional: Fox may stick with Creature.wander, unless you need special rules ---
    # def wander(self):
    #     super().wander()
