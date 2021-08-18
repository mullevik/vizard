import typing
import logging
log = logging.getLogger(__name__)

import pygame

from src.action import ActionException
from src.event import notify, Observer, EventName, subscribe
from src.player import HorizontalMoveAction, VerticalMoveAction, \
    GrassEndJumpAction, GrassStartJumpAction
from src.particle import ParticleSprite
from src.utils import CardinalDirection, Position

if typing.TYPE_CHECKING:
    from src.scene import GameScene


class PlayerController(object):
    scene: 'GameScene'

    def __init__(self, scene: 'GameScene'):
        self.scene = scene

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
        ]
        for observer in observers:
            observer.subscribe()

    def handle_input(self, text_input: str):

        for char in text_input:
            if char in self.scene.settings.key_event_map:
                try:
                    notify(self.scene.settings.key_event_map[char], self.scene)
                except ActionException as e:
                    log.debug("invalid action")


def spawn_blink_particles(scene: 'GameScene', previous_position: Position):
    scene.player_sprite.animator.start_animation(
        "blink-in", pygame.time.get_ticks())
    scene.spawn_particle(
        ParticleSprite.create_blink_in(scene, scene.player.position))
    scene.spawn_particle(
        ParticleSprite.create_blink_out(scene, previous_position)
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
        scene.player.apply_action(
            GrassEndJumpAction(scene.environment,
                               CardinalDirection.EAST))
        spawn_blink_particles(scene, previous_position)


class BlinkToTheEndOfNextVegetationChunk(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-to-the-end-of-next-vegetation-chunk", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        scene.player.apply_action(
            GrassEndJumpAction(scene.environment,
                               CardinalDirection.EAST,
                               ignore_stones=True))
        spawn_blink_particles(scene, previous_position)


class BlinkToTheStartOfNextVegetation(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-to-the-start-of-next-vegetation", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        scene.player.apply_action(
            GrassStartJumpAction(scene.environment,
                                 CardinalDirection.EAST))
        spawn_blink_particles(scene, previous_position)


class BlinkToTheStartOfNextVegetationChunk(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-to-the-start-of-next-vegetation-chunk", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        scene.player.apply_action(
            GrassStartJumpAction(scene.environment,
                                 CardinalDirection.EAST,
                                 ignore_stones=True))
        spawn_blink_particles(scene, previous_position)


class BlinkToTheStartOfPreviousVegetation(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-to-the-start-of-previous-vegetation", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        scene.player.apply_action(
            GrassEndJumpAction(scene.environment,
                               CardinalDirection.WEST))
        spawn_blink_particles(scene, previous_position)


class BlinkToTheStartOfPreviousVegetationChunk(Observer):

    def subscribe(self) -> EventName:
        return subscribe("blink-to-the-start-of-previous-vegetation-chunk", self)

    def update(self, scene: 'GameScene') -> None:
        previous_position = scene.player.get_position()
        scene.player.apply_action(
            GrassEndJumpAction(scene.environment,
                               CardinalDirection.WEST,
                               ignore_stones=True))
        spawn_blink_particles(scene, previous_position)
