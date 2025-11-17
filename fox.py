from creature import Creature

class Fox(Creature):
    def __init__(self, start, image_path, tile_w, tile_h,
                 world_grid, world_width, world_height):
        
        image_path = "images/fox_red.png"

        super().__init__(start, image_path, tile_w, tile_h,
                         world_grid, world_width, world_height)

        # Fox-specific
        self.vision_range = 12
        self.hunting = False

    # --------------------------
    # Fox detects rabbit
    # --------------------------
    def sees_rabbit(self, rabbit_location):
        dx = abs(self.location[0] - rabbit_location[0])
        dy = abs(self.location[1] - rabbit_location[1])
        return max(dx, dy) <= self.vision_range

    # --------------------------
    # Fox hunts rabbit
    # --------------------------
    def hunt(self, rabbit_location):
        self.hunting = True
        self.find_path(self.location, rabbit_location)

    # --------------------------
    # Fox logic update
    # --------------------------
    def update(self, rabbit_location):
        if self.sees_rabbit(rabbit_location):
            self.hunt(rabbit_location)
        else:
            self.hunting = False
            if not self.goal:
                self.wander()

        self.follow_path()
