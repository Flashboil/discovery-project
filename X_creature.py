import pygame
import heapq
import numpy
import random

class Creature:
    def __init__(self, start, image_path, tilewidth, tileheight,
                 world_grid, world_width, world_height):

        # World
        self.world_grid = world_grid
        self.world_width = world_width
        self.world_height = world_height

        # Positioning + Movement
        self.location = start
        self.goal = None
        self.path = []
        self.path_index = 0
        self.speed = 10
        self.state = "wander"

        # Load sprite
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (tilewidth, tileheight))

    # --------------------------
    # Drawing
    # --------------------------
    def draw(self, screen, tile_w, tile_h):
        px = self.location[0] * tile_w
        py = self.location[1] * tile_h
        screen.blit(self.image, (px, py))

    # --------------------------
    # Pathfinding
    # --------------------------
    def octile_distance(self, a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return (numpy.sqrt(2) * min(dx, dy)) + (max(dx, dy) - min(dx, dy))

    def is_walkable(self, pos):
        x, y = pos
        return self.world_grid[y][x] in (0, 3, 5, 7, 9)

    def get_neighbors(self, node, goal):
        neighbors = [(-1,-1), (0,-1), (1,-1),
                     (-1, 0),          (1, 0),
                     (-1, 1), (0, 1),  (1, 1)]

        result = []
        x, y = node

        for dx, dy in neighbors:
            nx, ny = x + dx, y + dy

            # Bound check
            if not (0 <= nx < self.world_width and 0 <= ny < self.world_height):
                continue

            if not self.is_walkable((nx, ny)):
                continue

            # Block illegal diagonals
            if dx != 0 and dy != 0:
                if not (self.is_walkable((x + dx, y)) and
                        self.is_walkable((x, y + dy))):
                    continue

            cost = 1.414 if (dx != 0 and dy != 0) else 1
            result.append(((nx, ny), cost))

        return result

    def reconstruct_path(self, goal, came_from):
        path = []
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = came_from.get(cur)
        path.reverse()
        return path

    def find_path(self, start, goal):
        self.goal = goal
        open_heap = []
        came_from = {}
        g = {start: 0}
        heapq.heappush(open_heap, (self.octile_distance(start, goal), start))

        closed = set()

        while open_heap:
            _, current = heapq.heappop(open_heap)

            if current in closed:
                continue
            closed.add(current)

            if current == goal:
                self.path = self.reconstruct_path(goal, came_from)
                self.path_index = 1 if len(self.path) > 1 else 0
                return self.path

            for (nb, cost) in self.get_neighbors(current, goal):
                new_g = g[current] + cost
                if nb not in g or new_g < g[nb]:
                    g[nb] = new_g
                    came_from[nb] = current
                    f = new_g + self.octile_distance(nb, goal)
                    heapq.heappush(open_heap, (f, nb))

        # No path found
        self.path = []
        self.path_index = 0
        return self.path

    # --------------------------
    # Following the path
    # --------------------------
    def follow_path(self):
        if not self.path or self.path_index >= len(self.path):
            return

        self.location = self.path[self.path_index]
        self.path_index += 1

        if self.path_index >= len(self.path):
            self.path = []
            self.path_index = 0

    # --------------------------
    # Generic wandering shared by Rabbit + Fox
    # --------------------------
    def wander(self, far_chance=0.25, min_range=4, max_range=8):
        attempts = 0
        max_attempts = 12
        self.goal = None

        while attempts < max_attempts and self.goal is None:

            if random.random() < far_chance:
                gx = random.randint(0, self.world_width - 1)
                gy = random.randint(0, self.world_height - 1)
            else:
                span = random.randint(min_range, max_range)
                gx = min(max(self.location[0] + random.randint(-span, span), 0),
                          self.world_width - 1)
                gy = min(max(self.location[1] + random.randint(-span, span), 0),
                          self.world_height - 1)

            if self.is_walkable((gx, gy)):
                self.goal = (gx, gy)
                self.find_path(self.location, self.goal)

                if self.path:
                    return
                else:
                    self.goal = None

            attempts += 1

        # Worst case: fail → do nothing
        self.goal = None
        self.path = []
