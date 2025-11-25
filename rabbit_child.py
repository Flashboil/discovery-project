# rabbit.py
import random
import pygame
from creature_parent import Creature  # adjust import path as needed


class Rabbit(Creature):
    def __init__(self, start, goal, tilewidth, tileheight, world_grid, world_width, world_height):
        # initialize shared Creature state
        super().__init__(start, goal, tilewidth, tileheight, world_grid, world_width, world_height)

        # === Rabbit-specific stats ===
        self.base_speed = 14
        self.boost_speed = 8
        self.speed = self.base_speed

        self.boost_timer = 0
        self.boost_cooldown = 120  # frames until next boost allowed
        self.can_boost = True
        # dynamic cooldown counter used by update_speed (created when needed)
        # self._cooldown_counter = 0

        self.recovery_timer = 0
        self.recovery_delay = 20  # frames of rest after fleeing

        self.safe_radius = 7

        # Rabbit-specific rendering override (subclass supplies its image)
        self.image = pygame.image.load("images/rabbit_red.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (tilewidth, tileheight))

        # home (Creature already sets self.home = start, but keep explicit if desired)
        self.home = start

    # -------------------------
    # Rabbit-specific behavior
    # -------------------------
    def boost(self):
        """Start a short boost if available."""
        if self.can_boost:
            self.speed = self.boost_speed
            self.boost_timer = 24  # how long boost lasts (frames)
            self.can_boost = False

    def update_speed(self):
        """Handle boost timers and cooldowns. Call this each tick for rabbits."""
        # Handle active boost countdown
        if self.boost_timer > 0:
            self.boost_timer -= 1
            if self.boost_timer <= 0:
                self.speed = self.base_speed
                self.boost_timer = 0

        # Handle cooldown reset so boost can be used again later
        if not self.can_boost and self.boost_timer == 0:
            if not hasattr(self, "_cooldown_counter"):
                self._cooldown_counter = 0
            self._cooldown_counter += 1
            if self._cooldown_counter >= self.boost_cooldown:
                self.can_boost = True
                self._cooldown_counter = 0

    def detect_flower(self):
        """Scan tiles in vision radius for a flower tile (tile value 5). Return first found coords or None."""
        x, y = self.location
        for dy in range(-self.vision_radius, self.vision_radius + 1):
            for dx in range(-self.vision_radius, self.vision_radius + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.world_width and 0 <= ny < self.world_height:
                    if self.world_grid[ny][nx] == 5:  # flower tile value used in your world
                        return (nx, ny)
        return None

    def wander(self, fox_path):
        """
        Rabbit's wander: similar to Creature.wander but avoids tiles that are in fox_path.
        This overrides the base wander which didn't know about fox_path.
        """
        attempts = 0
        while attempts < 5:
            if random.random() < 0.25:
                gx = random.randint(0, self.world_width - 1)
                gy = random.randint(0, self.world_height - 1)
            else:
                wander_range = random.randint(4, 8)
                gx = min(max(self.location[0] + random.randint(-wander_range, wander_range), 0), self.world_width - 1)
                gy = min(max(self.location[1] + random.randint(-wander_range, wander_range), 0), self.world_height - 1)

            # ensure tile walkable and not in the fox's planned path
            if self.world_grid[gy][gx] in (0, 3, 5, 7, 9) and (gx, gy) not in fox_path:
                self.goal = (gx, gy)
                self.find_path(self.location, self.goal)
                if self.path:
                    return
            attempts += 1

        # fallback: pick a random open tile (like your old code)
        open_tiles = [(x, y) for y in range(self.world_height) for x in range(self.world_width)
                      if self.world_grid[y][x] in (0, 3, 5, 7)]
        if open_tiles:
            self.goal = random.choice(open_tiles)
            self.find_path(self.location, self.goal)

    def detect_fox(self, fox_location):
        """Keep API-compatible: calls the generic detect_entity from Creature."""
        return self.detect_entity(fox_location)

    def flee_from_fox(self, fox_location):
        """Choose a simple escape target away from the fox and plan a path to it."""
        if fox_location is None:
            return

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

        # Move several tiles away (scale 5 like original)
        escape_x = min(max(x + dx * 5, 0), self.world_width - 1)
        escape_y = min(max(y + dy * 5, 0), self.world_height - 1)

        # Ensure it's a walkable goal (match your original allowed tiles)
        if self.world_grid[escape_y][escape_x] in (0, 3, 5):
            self.goal = (escape_x, escape_y)
            self.state = "flee"
            self.find_path(self.location, self.goal)

    def find_escape_goal(self, fox_location, grid_width, grid_height, world_grid):
        """
        Like the old helper: check a 11x11 area around rabbit and pick the furthest empty tile.
        Returns coords or None.
        """
        best_goal = None
        best_score = -float('inf')

        for dx in range(-5, 6):
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
        """Return True if fox is outside rabbit's safe radius (or no fox)."""
        if fox_location is None:
            return True
        x, y = self.location
        fx, fy = fox_location
        dx = abs(fx - x)
        dy = abs(fy - y)
        return dx > self.safe_radius or dy > self.safe_radius
