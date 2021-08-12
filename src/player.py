from abc import abstractmethod
from typing import Any, TYPE_CHECKING
import logging
log = logging.getLogger(__name__)

import pygame
from pygame.rect import Rect
from pygame.sprite import AbstractGroup
from pygame.surface import Surface

from src.action import AbstractAction, ActionException
from src.animation import FallbackAnimator, Animation
from src.constants import *
from src.environment import Environment
from src.utils import Position, CardinalDirection, load_scaled_surfaces

if TYPE_CHECKING:
    from src.scene import GameScene


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
    scene: 'GameScene'
    player: Player
    animator: FallbackAnimator
    image: Surface
    rect: Rect

    def __init__(self, scene: 'GameScene', player: Player,
                 *groups: AbstractGroup):
        super().__init__(*groups)

        self.scene = scene
        self.scene.player = player

        scale_factor = scene.settings.scale_factor

        idle_frames = load_scaled_surfaces(ANIM_VIZARD_IDLE, scale_factor)
        dash_frames = load_scaled_surfaces(ANIM_VIZARD_DASH, scale_factor)
        self.image = idle_frames[0]
        self.animator = FallbackAnimator({
            "idle": Animation(idle_frames, 600, loop=True),
            "dash": Animation(dash_frames, 100)
        })
        self.animator.start(pygame.time.get_ticks())

        center_of_first_tile = ((TILE_SIZE_PX // 2) * scale_factor,
                                (TILE_SIZE_PX + 1) * scale_factor)
        self.rect = self.image.get_rect(midbottom=center_of_first_tile)

    def update(self, *args, **kwargs) -> None:
        self._check_for_vertical_shift()
        self._update_rectangle_based_on_current_position()

    def _update_rectangle_based_on_current_position(self):
        x = (self.scene.player.position.x * TILE_SIZE_PX) + (TILE_SIZE_PX // 2)
        x = x * self.scene.settings.scale_factor

        y = ((
                         self.scene.player.position.y - self.scene.vertical_shift) * TILE_SIZE_PX) \
            + (TILE_SIZE_PX + 1)
        y = y * self.scene.settings.scale_factor

        self.rect = self.image.get_rect(midbottom=(x, y))

        image = self.animator.get_image(pygame.time.get_ticks())
        if self.scene.player.direction == CardinalDirection.WEST:
            self.image = pygame.transform.flip(image, True, False)
        else:
            self.image = image

    def _check_for_vertical_shift(self):
        current_screen_position = self.scene.player.position.y - self.scene.vertical_shift
        if current_screen_position < 1:
            self.scene.shift_view(0 + (current_screen_position - 1))
        elif current_screen_position > HEIGHT_IN_TILES - 2:
            self.scene.shift_view(
                (current_screen_position + 1) - (HEIGHT_IN_TILES - 1))


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
        player: Player = subject

        current_position = player.get_position()
        current_y = current_position.y
        future_y = current_y + self.steps

        if 0 <= future_y < self.environment.get_tile_dimensions()[1] - 1:

            future_position = Position(player.get_position().x, future_y)

            if self.environment.tile_at(future_position).is_walkable():
                player.set_position(future_position)
            else:
                raise ActionException(f"Vertical move would end up on non-"
                                      f"walkable position {future_position}")
        else:
            raise ActionException(
                f"Vertical move outside of bounds: {future_y}")


class GrassJumpAction(AbstractAction):
    environment: Environment
    direction: CardinalDirection
    ignore_stones: bool

    def __init__(self, environment: Environment,
                 direction: CardinalDirection, ignore_stones: bool):
        super().__init__()
        self.environment = environment
        self.direction = direction
        self.ignore_stones = ignore_stones

    def apply(self, subject: Any):
        player: Player = subject
        current_position = player.get_position()

        future_position = self._find_goal_position(current_position)

        if (self.environment.contains(future_position)
                and self.environment.tile_at(
                    future_position).is_walkable()):
            player.set_position(future_position)
            player.set_direction(self.direction)
        else:
            raise ActionException(
                f"Target position is not walkable: {future_position}")

    def _increment_position_with_direction(self,
                                           position: Position) -> Position:
        x, y = position
        width = self.environment.get_tile_dimensions()[0]

        x = x + 1 if self.direction == CardinalDirection.EAST else x - 1
        # if x is out of bounds, jump to the next/previous row
        if x < 0:
            x = width - 1
            y -= 1
        if x > width - 1:
            x = 0
            y += 1
        return Position(x, y)

    @abstractmethod
    def _find_goal_position(self, current_position: Position) -> Position:
        raise NotImplementedError


class GrassStartJumpAction(GrassJumpAction):

    def __init__(self, environment: Environment, direction: CardinalDirection,
                 ignore_stones: bool = False):
        super().__init__(environment, direction, ignore_stones)

    def _find_goal_position(self, current_position: Position) -> Position:

        current_tile = self.environment.tile_at(current_position)
        source_tile = current_tile

        position = self._increment_position_with_direction(current_position)

        height = self.environment.get_tile_dimensions()[1] - 1

        while 0 <= position.y < height:

            tile = self.environment.tile_at(position)

            if not source_tile.is_stone() and not source_tile.is_grass():
                # starting on blank tile
                if tile.is_grass() or tile.is_stone():
                    return position

            if source_tile.is_grass():
                # starting on grass tile
                if not self.ignore_stones and tile.is_stone():
                    return position

                if not tile.is_grass() and not tile.is_stone():
                    source_tile = tile

            if source_tile.is_stone():
                # starting on stone tile
                if not self.ignore_stones and tile.is_grass():
                    return position
                if not tile.is_grass() and not tile.is_stone():
                    source_tile = tile

            position = self._increment_position_with_direction(position)

        return position


class GrassEndJumpAction(GrassJumpAction):

    def __init__(self, environment: Environment, direction: CardinalDirection,
                 ignore_stones: bool = False):
        super().__init__(environment, direction, ignore_stones)

    def _find_goal_position(self, current_position: Position) -> Position:
        current_tile = self.environment.tile_at(current_position)

        height = self.environment.get_tile_dimensions()[1] - 1

        previous_position = self._increment_position_with_direction(
            current_position)
        next_position = self._increment_position_with_direction(
            previous_position)

        while 0 <= previous_position.y < height:

            previous_tile = self.environment.tile_at(previous_position)
            next_tile = self.environment.tile_at(next_position)

            if ((previous_tile.is_stone() or previous_tile.is_grass())
                    and ((
                                 not next_tile.is_stone() and not next_tile.is_grass())
                         or (
                         not self.environment.contains(next_position)))):
                # previous position was grass/stone and next position is blank
                # or it is not in the bounds of the map
                # so return previous position (end of word)
                return previous_position

            if not self.ignore_stones:
                if previous_tile.is_grass() and next_tile.is_stone():
                    return previous_position
                if previous_tile.is_stone() and next_tile.is_grass():
                    return previous_position

            previous_position = next_position
            next_position = self._increment_position_with_direction(
                next_position)

        return previous_position


class PlayerController(object):
    scene: 'GameScene'

    def __init__(self, scene: 'GameScene'):
        self.scene = scene

    def handle_input(self, text_input: str):

        for char in text_input:
            try:
                if char == "h":
                    self.scene.player.apply_action(
                        HorizontalMoveAction(self.scene.environment, -1))
                    self.scene.player_sprite.animator.start_animation(
                        "dash", pygame.time.get_ticks())
                if char == "j":
                    self.scene.player.apply_action(
                        VerticalMoveAction(self.scene.environment, 1))
                if char == "k":
                    self.scene.player.apply_action(
                        VerticalMoveAction(self.scene.environment, -1))
                if char == "l":
                    self.scene.player.apply_action(
                        HorizontalMoveAction(self.scene.environment, 1))
                    self.scene.player_sprite.animator.start_animation(
                        "dash", pygame.time.get_ticks())
                if char == "w":
                    self.scene.player.apply_action(
                        GrassStartJumpAction(self.scene.environment,
                                             CardinalDirection.EAST))
                if char == "e":
                    self.scene.player.apply_action(
                        GrassEndJumpAction(self.scene.environment,
                                           CardinalDirection.EAST))

                if char == "E":
                    self.scene.player.apply_action(
                        GrassEndJumpAction(self.scene.environment,
                                           CardinalDirection.EAST,
                                           ignore_stones=True))

                if char == "b":
                    self.scene.player.apply_action(
                        GrassEndJumpAction(self.scene.environment,
                                           CardinalDirection.WEST))

                if char == "B":
                    self.scene.player.apply_action(
                        GrassEndJumpAction(self.scene.environment,
                                           CardinalDirection.WEST,
                                           ignore_stones=True))

            except ActionException as e:
                log.debug("invalid action")
