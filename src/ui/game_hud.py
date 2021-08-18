import typing

import pygame
from pygame.rect import Rect
from pygame.sprite import Sprite, AbstractGroup, Group
from pygame.surface import Surface

from src.animation import PIXEL_FONT_SMALL, \
    WIDTH_IN_TILES, TILE_SIZE_PX, HEIGHT_IN_TILES, ANIM_SHARD_IDLE
from src.utils import load_scaled_surfaces

if typing.TYPE_CHECKING:
    from src.scene import GameScene, Scene


class GameHudFactory(object):

    @staticmethod
    def build_group(scene: 'Scene') -> Group:
        shard_icon = ShardIconUI(scene)
        shard_count = ShardCountUI(scene)
        clock = ClockUI(scene)

        return Group([shard_icon, shard_count, clock])


class ShardIconUI(Sprite):
    scene: 'GameScene'

    image: Surface
    rect: Rect

    def __init__(self, scene: 'GameScene', *groups: AbstractGroup):
        super().__init__(*groups)

        self.scene = scene
        scale_factor = self.scene.settings.scale_factor
        scale_multiplier = 0.6

        self.image = load_scaled_surfaces(ANIM_SHARD_IDLE,
                                          scale_factor * scale_multiplier)[0]
        self.rect = self.image.get_rect(bottomright=(
            (WIDTH_IN_TILES - 3) * TILE_SIZE_PX * scale_factor,
            (HEIGHT_IN_TILES) * TILE_SIZE_PX * scale_factor))

    def update(self, *args, **kwargs) -> None:
        pass


class ShardCountUI(Sprite):
    scene: 'GameScene'
    color = (93, 255, 238)
    image: Surface
    rect: Rect

    def __init__(self, scene: 'GameScene', *groups: AbstractGroup):
        super().__init__(*groups)

        self.scene = scene
        scale_factor = self.scene.settings.scale_factor

        self.image = PIXEL_FONT_SMALL.render("nan", False, self.color)
        self.rect = self.image.get_rect(
            bottomleft=((WIDTH_IN_TILES - 3) * TILE_SIZE_PX * scale_factor,
                        HEIGHT_IN_TILES * TILE_SIZE_PX * scale_factor))

    def update(self, *args, **kwargs) -> None:
        self.image = PIXEL_FONT_SMALL.render(
            f"{self.scene.data.collected_shards}", False, self.color)


class ClockUI(Sprite):
    scene: 'GameScene'

    image: Surface
    rect: Rect

    def __init__(self, scene: 'GameScene', *groups: AbstractGroup):
        super().__init__(*groups)

        self.scene = scene

        self.image = PIXEL_FONT_SMALL.render("nan", False, (255, 255, 255))
        self._update_position_of_timer_text()

    def _update_position_of_timer_text(self):
        scale_factor = self.scene.settings.scale_factor
        self.rect = self.image.get_rect(
            bottomright=(WIDTH_IN_TILES * TILE_SIZE_PX * scale_factor,
                         HEIGHT_IN_TILES * TILE_SIZE_PX * scale_factor))

    def update(self, *args, **kwargs) -> None:
        ms_since_start = self.scene.recording.get_recording_time(
            pygame.time.get_ticks())
        seconds = ms_since_start // 1000
        minutes = seconds // 60

        minute_string = f"{minutes}:" if minutes > 0 else ""
        second_string = f"{seconds % 60:02d}." if minutes > 0 else f"{seconds % 60}."
        ms_string = f"{(ms_since_start % 1000) // 100}"

        self.image = PIXEL_FONT_SMALL.render(
            f"{minute_string + second_string + ms_string}", False,
            (255, 255, 255))

        self._update_position_of_timer_text()
