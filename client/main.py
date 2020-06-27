import enum
import io
import os
import random
import sys
import time

import pygame as pg

from abc import abstractmethod
from geometry import Direction, pdist, Point, Rotation

from map import get_map
from world import World


# Logical screen dimensions. This will be scaled to fit the display window.
SCREEN_WIDTH = 672
SCREEN_HEIGHT = 512
SCREENRECT = pg.rect.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
TILE_WIDTH = 32
TILE_HEIGHT = 32
SCREEN_WIDTH_TILES = int(SCREENRECT.width / TILE_WIDTH)
SCREEN_HEIGHT_TILES = int(SCREENRECT.height / TILE_HEIGHT)
WHITE_COLOR = (255, 255, 255)

ASSETS = [
    {'name': "water",  'tiles': True},
    {'name': "fox",  'tiles': True},
    {'name': "tree",  'tiles': True},
    {'name': "summerground", 'tiles': True, 'mirror': True},
]


def resource_dir():
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.curdir)
    return os.path.join(base_path, 'assets')


class GameState(enum.Enum):
    STARTED = 1


class GameTime:
    current_time = 0

    @classmethod
    def current_time_ms(cls):
        return cls.current_time

    @classmethod
    def update(cls, time_delta_ms):
        cls.current_time += time_delta_ms


class Controller:
    @abstractmethod
    def handle(self, event, game):
        pass

    @abstractmethod
    def tick(self, game, clock):
        pass


class GameController(Controller):
    MOVE_KEYPRESS_INTERVAL = 100

    def __init__(self):
        self.last_move_timestamp = 0

    def handle(self, event, game):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_q:
                game.rotate(Rotation.CounterClockwise)
            if event.key == pg.K_e:
                game.rotate(Rotation.Clockwise)
            if event.key in [pg.K_UP, pg.K_w]:
                game.face(Direction.UP)
            if event.key in [pg.K_DOWN, pg.K_s]:
                game.face(Direction.DOWN)
            if event.key in [pg.K_LEFT, pg.K_a]:
                game.face(Direction.LEFT)
            if event.key in [pg.K_RIGHT, pg.K_d]:
                game.face(Direction.RIGHT)
            if event.key == pg.K_ESCAPE:
                return True


    def tick(self, game, clock):
        GameTime.update(clock.get_time())
        current_timestamp = GameTime.current_time_ms()

        if current_timestamp > self.last_move_timestamp + \
                GameController.MOVE_KEYPRESS_INTERVAL:
            keystate = pg.key.get_pressed()
            direction = None
            if keystate[pg.K_UP] or keystate[pg.K_w]:
                game.move(Direction.UP)
                self.last_move_timestamp = current_timestamp
            if keystate[pg.K_DOWN] or keystate[pg.K_s]:
                game.move(Direction.DOWN)
                self.last_move_timestamp = current_timestamp
            if keystate[pg.K_LEFT] or keystate[pg.K_a]:
                game.move(Direction.LEFT)
                self.last_move_timestamp = current_timestamp
            if keystate[pg.K_RIGHT] or keystate[pg.K_d]:
                game.move(Direction.RIGHT)
                self.last_move_timestamp = current_timestamp

        for scheduled_event in game.scheduled_events:
            if current_timestamp > scheduled_event.last_timestamp + \
                                    scheduled_event.period:
                scheduled_event.action(scheduled_event, current_timestamp)
                scheduled_event.last_timestamp = current_timestamp

        game.tick()


class Game:
    N_GROUND_TILES = 30

    def __init__(self, screen):
        font_path = os.path.join(resource_dir(), "freesansbold.ttf")
        self.title_font = pg.font.Font(font_path, 48)
        self.stats_font = pg.font.Font(font_path, 28)
        self.score_font = pg.font.Font(font_path, 24)

        self.screen = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.display_screen = screen
        self.assets = {}

        self.controllers = {
            GameState.STARTED: GameController(),
        }

        self.reset()

    def reset(self):
        self.scheduled_events = []

        self.world = World(get_map(), self.N_GROUND_TILES)
        self.new_pos = Point(self.world.player.pos.x,
                             self.world.player.pos.y)

        self.state = GameState.STARTED

    def _schedule_event(self, action, period):
        event = ScheduledEvent(action, period)
        self.scheduled_events.append(event)

    def load_assets(self):
        assets_path = resource_dir()
        for asset in ASSETS:
            asset_filename = asset if isinstance(asset, str) else asset['name']
            f = os.path.join(assets_path, f"{asset_filename}.png")
            try:
                surface = pg.image.load(f)
            except pg.error:
                raise SystemExit((f"Failed to load asset {asset_filename}: "
                                  f"{pg.get_error()}"))
            surface = surface.convert_alpha()
            if surface.get_width() > TILE_WIDTH and isinstance(asset, dict) \
                    and asset.get('tiles'):
                self.assets[asset_filename] = []
                for i in range(int(surface.get_width() / TILE_WIDTH)):
                    r = pg.rect.Rect(i*TILE_WIDTH, 0, TILE_WIDTH, TILE_HEIGHT)
                    subsurface = surface.subsurface(r)
                    self.assets[asset_filename].append(subsurface)
                    if isinstance(asset, dict) and asset.get('mirror'):
                        self.assets[asset_filename].append(pg.transform.flip(
                            subsurface, True, False))
            else:
                self.assets[asset_filename] = surface.convert_alpha()

    def _draw_image_at(self, image, x, y, frame=None):
        if isinstance(image, str):
            image = self.assets[image]
        px = x * TILE_WIDTH
        py = y * TILE_HEIGHT

        if frame is not None:
            image = image[frame]

        self.screen.blit(image, (px, py))

    def render_map(self):
        for x in range(SCREEN_WIDTH_TILES):
            for y in range(SCREEN_HEIGHT_TILES):
                (mapx, mapy) = (self.world.player.pos.x + x -
                                int(SCREEN_WIDTH_TILES / 2),
                                self.world.player.pos.y + y -
                                int(SCREEN_HEIGHT_TILES / 2 - 1))
                if mapx < 0 or mapx >= self.world.WIDTH_TILES or mapy < 0 \
                        or mapy >= self.world.HEIGHT_TILES:
                    self._draw_image_at('water', x, y)
                elif self.world.MAP[mapy][mapx] == '.':
                    frame = self.world.GROUND_LAYER[mapy][mapx]['tileidx']
                    ground = 'summerground'
                    self._draw_image_at(ground, x, y, frame=frame)
                elif self.world.MAP[mapy][mapx] == '#':
                    tree = 'tree'
                    self._draw_image_at(tree, x, y)

    def render(self):
        self.render_map()

        # Draw player
        self._draw_image_at(
            'fox',
            int(SCREEN_WIDTH_TILES / 2),
            int(SCREEN_HEIGHT_TILES / 2 - 1),
            frame=self.world.player.facing.value-1)

        # Scale logical screen to fit window display.
        display_width = self.display_screen.get_width()
        display_height = self.display_screen.get_height()
        scale_x = display_width / SCREEN_WIDTH
        scale_y = display_height / SCREEN_HEIGHT
        scale = min(scale_x, scale_y)

        if scale != 1:
            scaled_width = int(SCREEN_WIDTH * scale)
            scaled_height = int(SCREEN_HEIGHT * scale)
            screen_x = int((display_width - scaled_width) / 2)
            screen_y = int((display_height - scaled_height) / 2)

            scaled_screen = pg.transform.scale(
                self.screen, (scaled_width, scaled_height))
        else:
            screen_x, screen_y = 0, 0
            scaled_screen = self.screen

        self.display_screen.fill((0, 0, 0))
        self.display_screen.blit(scaled_screen, (screen_x, screen_y))

        pg.display.update()

    def _move_in_direction(self, pos, direction):
        x, y = pos.x, pos.y
        if direction == Direction.UP:
            y -= 1
        elif direction == Direction.DOWN:
            y += 1
        elif direction == Direction.LEFT:
            x -= 1
        elif direction == Direction.RIGHT:
            x += 1
        x = max(0, min(self.world.WIDTH_TILES - 1, x))
        y = max(0, min(self.world.HEIGHT_TILES - 1, y))
        return Point(x, y)

    def move(self, key):
        self.new_pos = self._move_in_direction(self.new_pos, key)

    def face(self, key):
        self.world.player.facing = key

    def rotate(self, direction):
        # TODO: fix spritesheet and enum order to allow
        # this to be done with modular arithmetic.
        if direction == Rotation.Clockwise:
            rmap = {
                Direction.DOWN: Direction.LEFT,
                Direction.LEFT: Direction.UP,
                Direction.UP: Direction.RIGHT,
                Direction.RIGHT: Direction.DOWN,
            }
        elif direction == Rotation.CounterClockwise:
            rmap = {
                Direction.DOWN: Direction.RIGHT,
                Direction.RIGHT: Direction.UP,
                Direction.UP: Direction.LEFT,
                Direction.LEFT: Direction.DOWN,
            }
        self.world.player.facing = rmap[self.world.player.facing]

    def _facing(self):
        facingx, facingy = self.world.player.pos.x, self.world.player.pos.y
        if self.world.player.facing == Direction.UP:
            return facingx, facingy-1
        elif self.world.player.facing == Direction.DOWN:
            return facingx, facingy+1
        elif self.world.player.facing == Direction.LEFT:
            return facingx-1, facingy
        elif self.world.player.facing == Direction.RIGHT:
            return facingx+1, facingy

    def action(self, action):
        facingx, facingy = self._facing()
        facing = Point(facingx, facingy)

    def tick(self):
        # If we're moving in a cardinal direction, face that way
        if self.new_pos.x != self.world.player.pos.x \
                and self.new_pos.y == self.world.player.pos.y:
            self.world.player.facing = Direction.LEFT \
                if self.new_pos.x < self.world.player.pos.x \
                else Direction.RIGHT
        elif self.new_pos.y != self.world.player.pos.y \
                and self.new_pos.x == self.world.player.pos.x:
            self.world.player.facing = Direction.UP \
                if self.new_pos.y < self.world.player.pos.y \
                else Direction.DOWN

        if self.world.player.can_move_to(self.world, self.new_pos):
            self.world.player.pos = self.new_pos
        else:
            self.new_pos = self.world.player.pos


class ScheduledEvent:
    def __init__(self, action, period):
        self.action = action
        self.period = period
        self.last_timestamp = GameTime.current_time_ms()


def main():
    pg.init()
    pg.font.init()

    screen = pg.display.set_mode(SCREENRECT.size, pg.RESIZABLE)
    clock = pg.time.Clock()

    pg.display.set_caption('multiplayer test')

    game = Game(screen)
    game.load_assets()

    last_move_timestamp = 0

    doquit = False
    while not doquit:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                doquit = True
            if game.controllers[game.state].handle(event, game):
                doquit = True
                break

        game.controllers[game.state].tick(game, clock)

        game.render()

        clock.tick(30)

    pg.quit()


if __name__ == '__main__':
    main()
