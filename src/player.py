from typing import Any

import pygame
from pygame.rect import Rect
from pygame.sprite import AbstractGroup
from pygame.surface import Surface

from src.action import AbstractAction, ActionException
from src.constants import TILE_SIZE_PX, IMG_VIZZARD_IDLE
from src.environment import Environment
from src.settings import GameSettings
from src.utils import load_scaled_surface, Position, CardinalDirection


class Player(object):
    position: Position
    direction: CardinalDirection

    def __init__(self):
        self.position = Position(0, 0)
        self.direction = CardinalDirection.EAST

    def get_position(self) -> Position:
        return self.position

    def set_position(self, position: Position):
        self.position = position

    def set_direction(self, direction: CardinalDirection):
        self.direction = direction

    def apply_action(self, action: AbstractAction):
        action.apply(self)


class PlayerSprite(pygame.sprite.Sprite):
    player: Player
    settings: GameSettings
    image: Surface
    original_image: Surface
    flipped_image: Surface
    rect: Rect

    def __init__(self, player: Player, settings: GameSettings,
                 *groups: AbstractGroup):
        super().__init__(*groups)

        self.player = player
        self.settings = settings

        self.original_image = load_scaled_surface(IMG_VIZZARD_IDLE,
                                                  settings.scale_factor)
        self.flipped_image = pygame.transform.flip(self.original_image, True,
                                                   False)
        self.image = self.original_image.copy()

        center_of_first_tile = ((TILE_SIZE_PX // 2) * settings.scale_factor,
                                (TILE_SIZE_PX + 1) * settings.scale_factor)
        self.rect = self.image.get_rect(midbottom=center_of_first_tile)

    def update(self, *args, **kwargs) -> None:
        self._update_rectangle_based_on_current_position()

    def _update_rectangle_based_on_current_position(self):
        x = (self.player.position.x * TILE_SIZE_PX) + (TILE_SIZE_PX // 2)
        x = x * self.settings.scale_factor

        y = (self.player.position.y * TILE_SIZE_PX) + (TILE_SIZE_PX + 1)
        y = y * self.settings.scale_factor

        self.rect = self.image.get_rect(midbottom=(x, y))

        if self.player.direction == CardinalDirection.WEST:
            self.image = self.flipped_image
        else:
            self.image = self.original_image


class HorizontalMoveAction(AbstractAction):
    steps: int
    environment: Environment

    def __init__(self, environment: Environment, steps: int):
        super().__init__()
        self.steps = steps
        self.environment = environment

    def apply(self, subject: Player):

        current_position = subject.get_position()
        current_x = current_position.x
        future_x = current_x + self.steps

        if 0 <= future_x < self.environment.get_tile_dimensions()[0]:

            future_position = Position(future_x, subject.get_position().y)

            if self.environment.tile_at(future_position).is_walkable():
                subject.set_position(future_position)

                future_direction = CardinalDirection.EAST \
                    if self.steps > 0 else CardinalDirection.WEST
                subject.set_direction(future_direction)
            else:
                raise ActionException(f"Horizontal move would end up on non-"
                                      f"walkable position {future_position}")

        else:
            raise ActionException(
                f"Horizontal move outside of bounds: {future_x}")


class VerticalMoveAction(AbstractAction):
    steps: int
    environment: Environment

    def __init__(self, environment: Environment, steps: int):
        super().__init__()
        self.steps = steps
        self.environment = environment

    def apply(self, subject: Any):

        current_position = subject.get_position()
        current_y = current_position.y
        future_y = current_y + self.steps

        if 0 <= future_y < self.environment.get_tile_dimensions()[1] - 1:

            future_position = Position(subject.get_position().x, future_y)

            if self.environment.tile_at(future_position).is_walkable():
                subject.set_position(future_position)
            else:
                raise ActionException(f"Vertical move would end up on non-"
                                      f"walkable position {future_position}")
        else:
            raise ActionException(
                f"Vertical move outside of bounds: {future_y}")
