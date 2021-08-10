from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame
from pygame.rect import Rect
from pygame.sprite import AbstractGroup
from pygame.surface import Surface

from src.animation import Animation
from src.utils import Position, load_scaled_surface, load_scaled_surfaces

from src.constants import IMG_SHARD, TILE_SIZE_PX, ANIM_SHARD_IDLE

if TYPE_CHECKING:
    from src.scene import GameScene


@dataclass
class Shard:
    position: Position


class ShardSprite(pygame.sprite.Sprite):

    scene: 'GameScene'
    shard: Shard

    image: Surface
    rect: Rect
    hitbox: Rect

    animation: Animation

    def __init__(self, scene: 'GameScene', shard: Shard, *groups: AbstractGroup, ):
        super().__init__(*groups)
        self.scene = scene
        self.shard = shard

        scale_factor = self.scene.settings.scale_factor

        # load images and create looping animation
        frames = load_scaled_surfaces(ANIM_SHARD_IDLE, scale_factor)
        self.image = frames[0]
        self.animation = Animation(frames, 75, loop=True)
        self.animation.start(pygame.time.get_ticks())

        center_of_first_tile = ((TILE_SIZE_PX // 2) * scale_factor,
                                (TILE_SIZE_PX // 2) * scale_factor)

        # set rect and hitbox
        self.rect = self.image.get_rect(center=center_of_first_tile)
        self.hitbox = self.rect.copy()
        self.hitbox.inflate_ip(-3 * scale_factor, -3 * scale_factor)

    def update(self, *args, **kwargs) -> None:
        self._update_rectangle_based_on_current_position()
        self.image = self.animation.get_image(pygame.time.get_ticks())

    def _update_rectangle_based_on_current_position(self):
        scale_factor = self.scene.settings.scale_factor
        position = self.shard.position

        x = (position.x * TILE_SIZE_PX) + (TILE_SIZE_PX // 2)
        x = x * scale_factor

        y = (position.y * TILE_SIZE_PX) + (TILE_SIZE_PX // 2)
        y = y * scale_factor

        self.rect.center = (x, y)
        self.hitbox.center = (x, y)
