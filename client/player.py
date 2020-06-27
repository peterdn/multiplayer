import enum
import random

from npc import NPC


class Player(NPC):
    __next_id = 1

    def __init__(self, pos, facing):
        super().__init__(pos, facing)

    @classmethod
    def _can_move_to(cls, world, pos):
        return not world.is_tree(pos)
