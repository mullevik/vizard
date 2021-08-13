from typing import TYPE_CHECKING, Dict
import logging

log = logging.getLogger(__name__)

import pygame
from pygame.rect import Rect
from pygame.sprite import AbstractGroup
from pygame.surface import Surface

from src.animation import Animation, LinearAlphaFadeAnimation
from src.constants import TILE_SIZE_PX, ANIM_VIZARD_DASH
from src.utils import Point, load_scaled_surfaces, Position, CardinalDirection

if TYPE_CHECKING:
    from src.scene import GameScene


class ParticleSprite(pygame.sprite.Sprite):
    scene: 'GameScene'
    image: Surface
    rect: Rect

    position: Position
    px_offset: Position
    animation: Animation

    def __init__(self, scene: 'GameScene', animation: Animation,
                 position: Position, px_offset: Position = Position(0, 0),
                 *groups: AbstractGroup):
        super().__init__(*groups)

        self.scene = scene
        self.animation = animation
        self.position = position
        self.px_offset = px_offset

        # automatically start the animation on creation
        self.animation.start(pygame.time.get_ticks())

        self.image = self.animation.get_image(pygame.time.get_ticks())
        self.rect = self.image.get_rect()
        self._update_rectangle_based_on_vertical_shift()

    def update(self, *args, **kwargs) -> None:
        self.image = self.animation.get_image(pygame.time.get_ticks())
        self._update_rectangle_based_on_vertical_shift()
        self._destroy()

    def _update_rectangle_based_on_vertical_shift(self):
        scale_factor = self.scene.settings.scale_factor
        x = (self.position.x * TILE_SIZE_PX) + (
                TILE_SIZE_PX // 2) + self.px_offset.x
        x = x * scale_factor

        y = ((self.position.y - self.scene.vertical_shift) * TILE_SIZE_PX) + (
                TILE_SIZE_PX // 2) + self.px_offset.y
        y = y * scale_factor

        self.rect.center = (x, y)

    def _destroy(self):
        if self.animation.is_over():
            self.kill()

    @staticmethod
    def create_dash_left(scene: 'GameScene',
                         position: Position) -> 'ParticleSprite':
        return ParticleSprite(
            scene,
            scene.animation_manager.get_animation("particle-dash-left"),
            position,
            px_offset=Position(-TILE_SIZE_PX // 2, 1)
        )

    @staticmethod
    def create_dash_right(scene: 'GameScene',
                          position: Position) -> 'ParticleSprite':
        return ParticleSprite(
            scene,
            scene.animation_manager.get_animation("particle-dash-right"),
            position,
            px_offset=Position(TILE_SIZE_PX // 2, 1)
        )

    @staticmethod
    def create_ascent(scene: 'GameScene', position: Position,
                      direction: CardinalDirection):
        animation_name = "particle-ascent-left" \
            if direction == CardinalDirection.WEST else "particle-ascent-right"

        return ParticleSprite(
            scene,
            scene.animation_manager.get_animation(animation_name),
            position,
            px_offset=Position(0, TILE_SIZE_PX // 2)
        )

    @staticmethod
    def create_descent(scene: 'GameScene', position: Position,
                       direction: CardinalDirection):
        animation_name = "particle-descent-left" \
            if direction == CardinalDirection.WEST else "particle-descent-right"

        return ParticleSprite(
            scene,
            scene.animation_manager.get_animation(animation_name),
            position,
            px_offset=Position(0, -TILE_SIZE_PX // 2)
        )

    @staticmethod
    def create_blink_in(scene: 'GameScene',
                        position: Position) -> 'ParticleSprite':
        return ParticleSprite(
            scene,
            scene.animation_manager.get_animation("particle-blink-in"),
            position,
            px_offset=Position(0, -TILE_SIZE_PX // 4)
        )


    @staticmethod
    def create_blink_out(scene: 'GameScene',
                         position: Position) -> 'ParticleSprite':
        return ParticleSprite(
            scene,
            scene.animation_manager.get_animation("particle-blink-out"),
            position,
            px_offset=Position(0, 0)
        )


    @staticmethod
    def create_shard_collected(scene: 'GameScene',
                               position: Position) -> 'ParticleSprite':
        return ParticleSprite(
            scene,
            scene.animation_manager.get_animation("particle-shard-collected"),
            position,
            px_offset=Position(0, -TILE_SIZE_PX)
        )
