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
        self.base_speed = 14
        self.boost_speed = 8
        self.speed = self.base_speed
        self.boost_timer = 0
        self.boost_cooldown = 120  # frames until next boost allowed
        self.can_boost = True
        self.recovery_timer = 0
        self.recovery_delay = 20  # frames of rest after fleeing

        self.safe_radius = 7

        self.vision_radius = 5
        self.state = "wander"

        self.image = pygame.image.load("images/rabbit_red.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (tilewidth, tileheight))
    
        self.home = start

    def boost(self):
        # Only trigger if not already boosted or cooling down
        if self.can_boost:
            self.speed = self.boost_speed
            self.boost_timer = 24  # how long boost lasts (in frames)
            self.can_boost = False


    def update_speed(self):
        # Handle boost timer countdown
        if self.boost_timer > 0:
            self.boost_timer -= 1
            if self.boost_timer <= 0:
                self.speed = self.base_speed
                self.boost_timer = 0

        # Handle cooldown reset (so it can boost again later)
        if not self.can_boost and self.boost_timer == 0:
            if not hasattr(self, "_cooldown_counter"):
                self._cooldown_counter = 0
            self._cooldown_counter += 1
            if self._cooldown_counter >= self.boost_cooldown:
                self.can_boost = True
                self._cooldown_counter = 0


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
                if self.world_grid[neighbor_y][neighbor_x] not in (0, 3, 5, 7): 
                    continue
                cost = 1.414 if dx != 0 and dy != 0 else 1
                locals.append(((neighbor_x, neighbor_y), cost))

        return locals
    
    def detect_flower(self):
        x, y = self.location
        for dy in range(-self.vision_radius, self.vision_radius + 1):
            for dx in range(-self.vision_radius, self.vision_radius + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.world_width and 0 <= ny < self.world_height:
                    if self.world_grid[ny][nx] == 5:  # flower tile
                        return (nx, ny)
        return None
    
    def wander(self, fox_path):
        attempts = 0
        while attempts < 5:
            if random.random() < 0.25:
                gx = random.randint(0, self.world_width - 1)
                gy = random.randint(0, self.world_height - 1)
            else:
                wander_range = random.randint(4, 8)
                gx = min(max(self.location[0] + random.randint(-wander_range, wander_range), 0), self.world_width - 1)
                gy = min(max(self.location[1] + random.randint(-wander_range, wander_range), 0), self.world_height - 1)

            if self.world_grid[gy][gx] in (0, 3, 5, 7) and (gx, gy) not in fox_path:
                self.goal = (gx, gy)
                self.find_path(self.location, self.goal)
                if self.path:
                    return
            attempts += 1

        # If all attempts fail, pick random open tile
        open_tiles = [(x, y) for y in range(self.world_height) for x in range(self.world_width)
                    if self.world_grid[y][x] in (0, 3, 5, 7)]
        if open_tiles:
            self.goal = random.choice(open_tiles)
            self.find_path(self.location, self.goal)



    def detect_fox(self, fox_location):
        if fox_location is None:
            return False
        x, y = self.location
        fx, fy = fox_location
        dx = abs(fx - x)
        dy = abs(fy - y)
        return dx <= self.vision_radius and dy <= self.vision_radius


    def flee_from_fox(self, fox_location):
        x, y = self.location
        fx, fy = fox_location

        # Direction vector away from fox
        dx = x - fx
        dy = y - fy

        # Normalize direction roughly
        if dx != 0:
            dx = int(dx / abs(dx))
        if dy != 0:
            dy = int(dy / abs(dy))

        # Move several tiles away
        escape_x = min(max(x + dx * 5, 0), self.world_width - 1)
        escape_y = min(max(y + dy * 5, 0), self.world_height - 1)

        # Ensure it’s a walkable goal
        if self.world_grid[escape_y][escape_x] in (0, 3, 5):
            self.goal = (escape_x, escape_y)
            self.state = "flee"
            self.find_path(self.location, self.goal)

    def find_escape_goal(self, fox_location, grid_width, grid_height, world_grid):
        # Generate candidate tiles around the rabbit
        directions = [(-1, -1), (0, -1), (1, -1),
                    (-1,  0),          (1,  0),
                    (-1,  1), (0,  1), (1,  1)]
        
        best_goal = None
        best_score = -float('inf')

        for dx in range(-5, 6):   # look in a 10x10 area
            for dy in range(-5, 6):
                gx = self.location[0] + dx
                gy = self.location[1] + dy
                if 0 <= gx < grid_width and 0 <= gy < grid_height:
                    if world_grid[gy][gx] == 0:  # empty
                        dist = ((gx - fox_location[0])**2 + (gy - fox_location[1])**2)**0.5
                        if dist > best_score:
                            best_score = dist
                            best_goal = (gx, gy)

        return best_goal
    
    def is_safe(self, fox_location):
        if fox_location is None:
            return True
        x, y = self.location
        fx, fy = fox_location
        dx = abs(fx - x)
        dy = abs(fy - y)
        return dx > self.safe_radius or dy > self.safe_radius


