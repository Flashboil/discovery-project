import pygame
import random

# ---------------------------
# Tile Constants
# ---------------------------
GRASS = 0
ROCK = 1
SHRUB = 2
CLOVER = 3
FLOWER = 5
TREE_BOTTOM = 6
TREE_TOP = 7
WARREN = 9

# ---------------------------
# Weighted tile distribution
# ---------------------------
TERRAIN_WEIGHTS = {
    GRASS: 0.70,
    SHRUB: 0.10,
    ROCK: 0.08,
    CLOVER: 0.07,
    TREE_BOTTOM: 0.05,
}


class World:
    """
    Handles:
    - grid generation
    - tile management
    - image loading
    - drawing background + foreground
    - placing flowers/warren
    """

    def __init__(self, width_px, height_px, tile_size):
        self.width_px = width_px
        self.height_px = height_px
        self.tile_size = tile_size

        self.grid_width = width_px // tile_size
        self.grid_height = height_px // tile_size

        # 2D grid
        self.grid = [[GRASS for _ in range(self.grid_width)]
                     for _ in range(self.grid_height)]

        # Load all tile images
        self.images = self.load_images()

        # Generate terrain
        self.generate_grid()

        # Fix trees (add tops)
        self.add_tree_tops()

    # --------------------------------------------------
    # Image loading
    # --------------------------------------------------
    def load_images(self):
        size = (self.tile_size, self.tile_size)

        def load(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)

        images = {
            ROCK: load("images/rock.png"),
            SHRUB: load("images/shrub.png"),
            CLOVER: load("images/clover.png"),
            FLOWER: load("images/flower_red.png"),
            TREE_BOTTOM: load("images/tree_bottom.png"),
            TREE_TOP: load("images/tree_top.png"),
            WARREN: load("images/warren.png"),
        }
        return images

    # --------------------------------------------------
    # Grid Generation
    # --------------------------------------------------
    def generate_grid(self):
        """Generate the base terrain using weighted tile probabilities."""
        choices = list(TERRAIN_WEIGHTS.keys())
        weights = list(TERRAIN_WEIGHTS.values())

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                self.grid[y][x] = random.choices(choices, weights)[0]

    # --------------------------------------------------
    # Tree top placement
    # --------------------------------------------------
    def add_tree_tops(self):
        """Convert TREE_BOTTOM tiles to TREE_TOP above them."""
        for y in range(1, self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] == TREE_BOTTOM:
                    # Replace tile above with TREE_TOP
                    self.grid[y - 1][x] = TREE_TOP

    # --------------------------------------------------
    # Tile info accessors
    # --------------------------------------------------
    def tile_at(self, x, y):
        return self.grid[y][x]

    def set_tile(self, x, y, tile):
        self.grid[y][x] = tile

    def is_walkable(self, x, y):
        """Return True if a creature can stand on this tile."""
        tile = self.tile_at(x, y)
        return tile in (GRASS, CLOVER, FLOWER)

    # --------------------------------------------------
    # Object placement
    # --------------------------------------------------
    def place_flowers(self, count):
        i = 0
        while i < count:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)

            if self.tile_at(x, y) in (GRASS, CLOVER, FLOWER):
                self.set_tile(x, y, FLOWER)
                i += 1

    def place_warren(self, x, y):
        """Place the rabbit’s home."""
        self.set_tile(x, y, WARREN)

    # --------------------------------------------------
    # Rendering functions
    # --------------------------------------------------
    def draw_background(self, screen):
        """Draw rocks, shrubs, clover, flowers, tree bottoms, warren."""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                tile = self.grid[y][x]

                if tile in self.images:  # Only background tiles
                    img = self.images[tile]
                    screen.blit(img, (x * self.tile_size, y * self.tile_size))

    def draw_foreground(self, screen, creatures):
        """
        Draws TREE_TOP tiles.
        If a creature is standing on a tree top, fade transparency.
        """
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                tile = self.grid[y][x]

                if tile == TREE_TOP:
                    pos = (x, y)

                    # Creature standing here?
                    creature_here = any(c.location == pos for c in creatures)

                    img = self.images[TREE_TOP]

                    if creature_here:
                        faded = img.copy()
                        faded.set_alpha(150)
                        screen.blit(faded, (x * self.tile_size, y * self.tile_size))
                    else:
                        screen.blit(img, (x * self.tile_size, y * self.tile_size))
