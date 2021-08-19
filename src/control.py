import typing
import logging

from src.constants import HEIGHT_IN_TILES

log = logging.getLogger(__name__)

import pygame

from src.action import ActionException
from src.event import notify, Observer, EventName, subscribe
from src.player import HorizontalMoveAction, VerticalMoveAction, \
    GrassEndJumpAction, GrassStartJumpAction, ContourJumpAction, \
    VerticalJumpAction
from src.particle import ParticleSprite
from src.utils import CardinalDirection, Position

if typing.TYPE_CHECKING:
    from src.scene import GameScene


class PlayerController(object):
    scene: 'GameScene'
    buffer: str

    def __init__(self, scene: 'GameScene'):
        self.scene = scene
        self.buffer = ""

        observers = [
            DashLeft(),
            DashDown(),
            DashUp(),
            DashRight(),
            BlinkToTheEndOfNextVegetation(),
            BlinkToTheEndOfNextVegetationChunk(),
            BlinkToTheStartOfNextVegetation(),
            BlinkToTheStartOfNextVegetationChunk(),
            BlinkToTheStartOfPreviousVegetation(),
            BlinkToTheStartOfPreviousVegetationChunk(),
            BlinkToTheEndOfContour(),
            BlinkToTheStartOfContour(),
            BlinkToTheStartOfFirstVegetationChunk(),
            BlinkToTheTop(),
            BlinkUp(),
            BlinkUpHalf(),
            BlinkDown(),
            BlinkDownHalf(),
            BlinkToTheBottom(),
        ]
        for observer in observers:
            observer.subscribe()

    def handle_input(self, text_input: str):

        for char in text_input:
            log.debug(f"detected char: {char} ({bytes(char, 'ascii')})")
            text = char

            # check for buffer
            if len(self.buffer) > 0:
                # something is in the buffer - take it out and clear buffer
                text = self.buffer + char
                self.buffer = ""
            else:
                if char in self.scene.settings.buffer_keys:
                    # add buffer key to an empty buffer
                    self.buffer = self.buffer + char
                    log.debug(f"buffer: {bytes(self.buffer, 'ascii')}")
                    return

            if text in self.scene.settings.key_event_map:
                try:
                    notify(self.scene.settings.key_event_map[text], self.scene)
                except ActionException as e:
                    log.debug(f"invalid action - {e}")
            else:
                log.warning(f"Unknown input text {bytes(text, 'ascii')}")


def spawn_blink_particles(scene: 'GameScene', previous_position: Position,
                          previous_direction: CardinalDirection):
    scene.player_sprite.animator.start_animation(
        "blink-in", pygame.time.get_ticks())
    scene.spawn_particle(
        ParticleSprite.create_blink_in(scene, scene.player.position))
    scene.spawn_particle(
        ParticleSprite.create_blink_out(scene, previous_position,
                                        previous_direction)
    )


class DashLeft(Observer):

    def subscribe(self) -> EventName:
        return subscribe("dash-left", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        scene.player.apply_action(
            HorizontalMoveAction(scene.environment, -1))
        scene.player_sprite.animator.start_animation(
            "dash", pygame.time.get_ticks())
        scene.spawn_particle(
            ParticleSprite.create_dash_left(scene, previous_position))


class DashDown(Observer):

    def subscribe(self) -> EventName:
        return subscribe("dash-down", self)

    def update(self, scene: 'GameScene') -> None:
        scene.player.apply_action(
            VerticalMoveAction(scene.environment, 1))
        scene.player_sprite.animator.start_animation(
            "descent", pygame.time.get_ticks())
        scene.spawn_particle(
            ParticleSprite.create_descent(scene,
                                          scene.player.position,
                                          scene.player.direction))


class DashUp(Observer):

    def subscribe(self) -> EventName:
        return subscribe("dash-up", self)

    def update(self, scene: 'GameScene') -> None:
        scene.player.apply_action(
            VerticalMoveAction(scene.environment, -1))
        scene.player_sprite.animator.start_animation(
            "ascent", pygame.time.get_ticks())
        scene.spawn_particle(
            ParticleSprite.create_ascent(scene,
                                         scene.player.position,
                                         scene.player.direction))


class DashRight(Observer):

    def subscribe(self) -> EventName:
        return subscribe("dash-right", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        scene.player.apply_action(
            HorizontalMoveAction(scene.environment, 1))
        scene.player_sprite.animator.start_animation(
            "dash", pygame.time.get_ticks())
        scene.spawn_particle(
            ParticleSprite.create_dash_right(scene, previous_position))


class BlinkToTheEndOfNextVegetation(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-to-the-end-of-next-vegetation", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        previous_direction = scene.player.direction
        scene.player.apply_action(
            GrassEndJumpAction(scene.environment,
                               CardinalDirection.EAST))
        spawn_blink_particles(scene, previous_position, previous_direction)


class BlinkToTheEndOfNextVegetationChunk(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-to-the-end-of-next-vegetation-chunk", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        previous_direction = scene.player.direction
        scene.player.apply_action(
            GrassEndJumpAction(scene.environment,
                               CardinalDirection.EAST,
                               ignore_stones=True))
        spawn_blink_particles(scene, previous_position, previous_direction)


class BlinkToTheStartOfNextVegetation(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-to-the-start-of-next-vegetation", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        previous_direction = scene.player.direction
        scene.player.apply_action(
            GrassStartJumpAction(scene.environment,
                                 CardinalDirection.EAST))
        spawn_blink_particles(scene, previous_position, previous_direction)


class BlinkToTheStartOfNextVegetationChunk(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-to-the-start-of-next-vegetation-chunk", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        previous_direction = scene.player.direction
        scene.player.apply_action(
            GrassStartJumpAction(scene.environment,
                                 CardinalDirection.EAST,
                                 ignore_stones=True))
        spawn_blink_particles(scene, previous_position, previous_direction)


class BlinkToTheStartOfPreviousVegetation(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-to-the-start-of-previous-vegetation", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        previous_direction = scene.player.direction
        scene.player.apply_action(
            GrassEndJumpAction(scene.environment,
                               CardinalDirection.WEST))
        spawn_blink_particles(scene, previous_position, previous_direction)


class BlinkToTheStartOfPreviousVegetationChunk(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-to-the-start-of-previous-vegetation-chunk", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        previous_direction = scene.player.direction
        scene.player.apply_action(
            GrassEndJumpAction(scene.environment,
                               CardinalDirection.WEST,
                               ignore_stones=True))
        spawn_blink_particles(scene, previous_position, previous_direction)


class BlinkToTheEndOfContour(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-to-the-end-of-contour", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        previous_direction = scene.player.direction
        scene.player.apply_action(
            ContourJumpAction(scene.environment,
                              CardinalDirection.EAST)
        )
        spawn_blink_particles(scene, previous_position, previous_direction)


class BlinkToTheStartOfContour(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-to-the-start-of-contour", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        previous_direction = scene.player.direction
        scene.player.apply_action(
            ContourJumpAction(scene.environment,
                              CardinalDirection.WEST)
        )
        spawn_blink_particles(scene, previous_position, previous_direction)


class BlinkToTheStartOfFirstVegetationChunk(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-to-the-start-of-first-vegetation-chunk", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        previous_direction = scene.player.direction
        scene.player.apply_action(
            ContourJumpAction(scene.environment,
                              CardinalDirection.WEST,
                              to_vegetation=True)
        )
        spawn_blink_particles(scene, previous_position, previous_direction)


class BlinkToTheTop(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-to-the-top", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        previous_direction = scene.player.direction
        scene.player.apply_action(
           VerticalJumpAction(scene.environment, -1,
                              CardinalDirection.NORTH)
        )
        spawn_blink_particles(scene, previous_position, previous_direction)


class BlinkUp(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-up", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        previous_direction = scene.player.direction
        scene.player.apply_action(
           VerticalJumpAction(scene.environment, HEIGHT_IN_TILES,
                              CardinalDirection.NORTH)
        )
        spawn_blink_particles(scene, previous_position, previous_direction)


class BlinkUpHalf(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-up-half", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        previous_direction = scene.player.direction
        scene.player.apply_action(
           VerticalJumpAction(scene.environment, HEIGHT_IN_TILES // 2,
                              CardinalDirection.NORTH)
        )
        spawn_blink_particles(scene, previous_position, previous_direction)


class BlinkDown(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-down", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        previous_direction = scene.player.direction
        scene.player.apply_action(
           VerticalJumpAction(scene.environment, HEIGHT_IN_TILES,
                              CardinalDirection.SOUTH)
        )
        spawn_blink_particles(scene, previous_position, previous_direction)


class BlinkDownHalf(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-down-half", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        previous_direction = scene.player.direction
        scene.player.apply_action(
           VerticalJumpAction(scene.environment, HEIGHT_IN_TILES // 2,
                              CardinalDirection.SOUTH)
        )
        spawn_blink_particles(scene, previous_position, previous_direction)


class BlinkToTheBottom(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-to-the-bottom", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        previous_direction = scene.player.direction
        scene.player.apply_action(
           VerticalJumpAction(scene.environment, -1,
                              CardinalDirection.SOUTH)
        )
        spawn_blink_particles(scene, previous_position, previous_direction)
