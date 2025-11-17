import pygame
from creature import Creature
import random
import numpy

class Rabbit(Creature):
    def __init__(self, start, goal, tile_w, tile_h, world_grid, world_width, world_height):
        image_path = "images/rabbit_red.png"
        super().__init__(start, image_path, tile_w, tile_h,
                         world_grid, world_width, world_height)
        
        self.goal = goal if goal is not None else start
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
        self.home = start

    # --------------------------
    # Boost mechanics
    # --------------------------
    def boost(self):
        if self.can_boost:
            self.speed = self.boost_speed
            self.boost_timer = 24
            self.can_boost = False

    def update_speed(self):
        # Countdown boost duration
        if self.boost_timer > 0:
            self.boost_timer -= 1
            if self.boost_timer <= 0:
                self.speed = self.base_speed
                self.boost_timer = 0

        # Handle cooldown
        if not self.can_boost and self.boost_timer == 0:
            if not hasattr(self, "_cooldown_counter"):
                self._cooldown_counter = 0
            self._cooldown_counter += 1
            if self._cooldown_counter >= self.boost_cooldown:
                self.can_boost = True
                self._cooldown_counter = 0

    # --------------------------
    # Perception / interactions
    # --------------------------
    def detect_flower(self):
        x, y = self.location
        for dy in range(-self.vision_radius, self.vision_radius + 1):
            for dx in range(-self.vision_radius, self.vision_radius + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.world_width and 0 <= ny < self.world_height:
                    if self.world_grid[ny][nx] == 5:  # flower tile
                        return (nx, ny)
        return None

    def detect_fox(self, fox_location):
        if fox_location is None:
            return False
        x, y = self.location
        fx, fy = fox_location
        dx = abs(fx - x)
        dy = abs(fy - y)
        return dx <= self.vision_radius and dy <= self.vision_radius

    def is_safe(self, fox_location):
        if fox_location is None:
            return True
        x, y = self.location
        fx, fy = fox_location
        dx = abs(fx - x)
        dy = abs(fy - y)
        return dx > self.safe_radius or dy > self.safe_radius

    # --------------------------
    # Fleeing
    # --------------------------
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

    def find_escape_goal(self, fox_location):
        # Generate candidate tiles around the rabbit
        best_goal = None
        best_score = -float('inf')
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                gx = self.location[0] + dx
                gy = self.location[1] + dy
                if 0 <= gx < self.world_width and 0 <= gy < self.world_height:
                    if self.world_grid[gy][gx] == 0:  # empty
                        dist = ((gx - fox_location[0])**2 + (gy - fox_location[1])**2)**0.5
                        if dist > best_score:
                            best_score = dist
                            best_goal = (gx, gy)
        return best_goal
