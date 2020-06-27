import random

from geometry import Direction, Point
from player import Player


class World:
    def __init__(self, map, N_GROUND_TILES=1):
        self.MAP = map
        self.WIDTH_TILES = len(self.MAP[0])
        self.HEIGHT_TILES = len(self.MAP)
        self.N_GROUND_TILES = N_GROUND_TILES

        self.GROUND_LAYER = [[{} for x in range(self.WIDTH_TILES)]
                             for y in range(self.HEIGHT_TILES)]

        for x in range(self.WIDTH_TILES):
            for y in range(self.HEIGHT_TILES):
                self.GROUND_LAYER[y][x]['tileidx'] = \
                    random.randint(0, self.N_GROUND_TILES-1)

        self.player = Player(Point(23, 22), Direction.DOWN)

    def random_point(self):
        x = random.randint(0, self.WIDTH_TILES - 1)
        y = random.randint(0, self.HEIGHT_TILES - 1)
        return Point(x, y)

    def in_world_bounds(self, pos):
        if pos.x < 0 or pos.x >= self.WIDTH_TILES or pos.y < 0 \
                or pos.y >= self.HEIGHT_TILES:
            return False
        return True

    def is_tree(self, pos):
        return self.in_world_bounds(pos) and self.MAP[pos.y][pos.x] == '#'

    def can_move_to(self, pos):
        if not self.in_world_bounds(pos):
            return False
        return True
