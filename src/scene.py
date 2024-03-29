import logging
import random
from dataclasses import dataclass

from pygame._sprite import Group

from src.animation import AnimationManager
from src.control import PlayerController
from src.ui.game_hud import GameHudFactory

log = logging.getLogger(__name__)
from abc import ABC, abstractmethod
from typing import Any, List, cast, Optional

import pygame
import yaml
from pygame.event import Event
from pygame.surface import Surface
from pygame.time import Clock

from src.constants import TICK_SPEED, HEIGHT_IN_TILES
from src.environment import Environment, EnvironmentRenderer
from src.event import EventHandler, AppEventHandler, TextEventHandler
from src.player import Player, PlayerSprite
from src.replay import Recording
from src.settings import GameSettings
from src.shard import ShardSprite, Shard
from src.utils import Position, Milliseconds, CardinalDirection
from src.particle import ParticleSprite


class SceneException(Exception):
    pass


class Scene(ABC):
    screen: Surface
    settings: GameSettings
    clock: Clock
    event_handlers: List[EventHandler]

    def __init__(self, screen: Surface, clock: Clock):
        self.settings = GameSettings(
            **yaml.load(open("../config.yaml"), Loader=yaml.FullLoader))
        self.screen = screen
        self.clock = clock
        self.event_handlers = [AppEventHandler(self)]
        self.data = GameData()

    def get_name(self) -> str:
        return self.__class__.__name__

    def get_game_object_by_name(self, name: str) -> Any:
        """
        Get a reference to any game object in the scene.
        :raises: SceneException when there is no object of this name in the scene
        :return: the game object which can have any type
        """
        if hasattr(self, name):
            return getattr(self, name)
        raise SceneException(f"Scene does not have game object {name}")

    def handle_events(self) -> List[Event]:
        """
        Delegates event handling to the scene event handlers.
        :return: list of the extracted events
        """
        events = pygame.event.get()

        for handler in self.event_handlers:
            handler.handle_events(events)

        return events

    def add_event_handler(self, event_handler: EventHandler) -> EventHandler:
        """Add event handler to the pipeline of scene event handlers.
        :return: the added handler reference"""
        self.event_handlers.append(event_handler)
        return event_handler

    @abstractmethod
    def run(self) -> str:
        """
        Starts the infinite real-time game loop.
        :returns The name of the followup scene or None if there is no
        preference for the followup scene."""
        raise NotImplementedError


class EmptyScene(Scene):

    def __init__(self, screen: Surface, clock: Clock):
        super().__init__(screen, clock)

    def run(self) -> bool:
        while True:

            # handle events
            for event in self.handle_events():

                if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    log.info("Starting game")
                    return GameScene.__name__

            self.screen.fill("gray")

            pygame.display.update()
            self.clock.tick(TICK_SPEED)


@dataclass
class GameData:

    start_time: Optional[Milliseconds] = None
    end_time: Optional[Milliseconds] = None
    collected_shards: int = 0


class GameScene(Scene):

    def __init__(self, screen: Surface, clock: Clock):
        super().__init__(screen, clock)
        self.environment = Environment(self.settings,
                                       open("../assets/maps/default.txt",
                                            "r").read())

        self.animation_manager = AnimationManager(self)

        self.vertical_shift = 0
        self.environment_renderer = EnvironmentRenderer(self.environment,
                                                        self.settings)

        self.text_event_handler = TextEventHandler(self)
        self.add_event_handler(self.text_event_handler)
        self.player_controller = PlayerController(self)

        self.recording = Recording()

        self.player = Player()
        self.player.set_position(self.environment.get_starting_position())
        self.player_sprite = PlayerSprite(self, self.player)
        self.player_group = pygame.sprite.GroupSingle(self.player_sprite)

        self.shard_group = pygame.sprite.Group([])

        self.particle_group = pygame.sprite.Group([])

        self.hud_ui_group = GameHudFactory.build_group(self)

        self.player_group.update()
        self.spawn_pack_of_shards()

    def shift_view(self, amount: int) -> int:
        """Shift the view of the world by +amount
        :param amount: by how many rows down should the world shift
        :return the new vertical_shift
        """
        self.vertical_shift += amount
        return self.vertical_shift

    def spawn_particle(self, particle_sprite: ParticleSprite) -> None:
        """Spawns a given particle. Particles should destroy automatically
        once their animation is over."""
        self.particle_group.add(particle_sprite)

    def spawn_shard(self, position: Position) -> None:
        """Spawns a shard at a given position.
        :param position: where to spawn a shard
        """
        shard = Shard(position)
        self.shard_group.add(ShardSprite(self, shard))
        self.recording.record_shard_spawn(pygame.time.get_ticks(), position)

        if shard.position.y > self.vertical_shift + HEIGHT_IN_TILES:
            # shard is below the screen
            particle = ParticleSprite.create_shard_pointer(
                self,
                Position(shard.position.x, self.vertical_shift + HEIGHT_IN_TILES - 2),
                CardinalDirection.SOUTH
            )
            self.particle_group.add(particle)
        elif shard.position.y < self.vertical_shift:
            # shard is above the screen
            particle = ParticleSprite.create_shard_pointer(
                self,
                Position(shard.position.x, self.vertical_shift + 1),
                CardinalDirection.NORTH
            )
            self.particle_group.add(particle)

    def spawn_random_shard(self) -> None:
        """Spawns a shard at a random walkable position.
        At least 4 units far from the player.
        And where there is no other shard."""

        def get_random_position(environment: 'Environment') -> Position:
            w, h = environment.get_tile_dimensions()
            x = random.randint(0, w - 1)
            y = random.randint(0, h - 2)
            return Position(x, y)

        def is_close_to_the_player(position: Position, player: Player) -> bool:
            if abs(player.get_position().x - position.x) < 4:
                return True
            if abs(player.get_position().y - position.y) < 4:
                return True
            return False

        def contains_shard(position: Position, shard_group: Group) -> bool:
            for shard_sprite in shard_group.sprites():
                shard_position = cast(ShardSprite, shard_sprite).shard.position
                if position == shard_position:
                    return True
            return False

        random_position = get_random_position(self.environment)
        n_rolls = 1
        while (not self.environment.tile_at(random_position).is_walkable()
               or is_close_to_the_player(random_position, self.player)
               or contains_shard(random_position, self.shard_group)):
            random_position = get_random_position(self.environment)
            n_rolls += 1

            if n_rolls > 500:
                log.error(f"Spawning random shard took too many ({n_rolls}) "
                          f"tries, no shard was spawned")
                return

        log.debug(f"Shard spawn took {n_rolls} tries")
        self.spawn_shard(random_position)

    def spawn_pack_of_shards(self):
        """Spawns two random shards."""
        self.spawn_random_shard()
        self.spawn_random_shard()

    def handle_collisions(self):
        colliding_sprites = pygame.sprite.spritecollide(
            self.player_sprite, self.shard_group, dokill=False,
            collided=self.is_player_colliding_with_shard)

        if colliding_sprites:
            log.debug("collision with shard")

            # spawn shard collected particles
            for sprite in colliding_sprites:
                position = cast(ShardSprite, sprite).shard.position
                self.spawn_particle(ParticleSprite.create_shard_collected(self, position))

            # remove collected shards
            number_of_shards = len(colliding_sprites)
            self.shard_group.remove(colliding_sprites)

            # add shards to score
            self.data.collected_shards += number_of_shards

            # spawn new random shards if there are no shards
            if len(self.shard_group.sprites()) == 0:
                self.spawn_pack_of_shards()

    @staticmethod
    def is_player_colliding_with_shard(player: PlayerSprite,
                                       shard: ShardSprite):
        return player.rect.colliderect(shard.hitbox)

    def run(self) -> bool:

        self.recording.start(pygame.time.get_ticks())
        log.info("Started recording")
        while True:

            events = self.handle_events()

            text_input = self.text_event_handler.get_text_from_this_tick()

            self.recording.record_text_input(pygame.time.get_ticks(), text_input)
            self.player_controller.handle_input(text_input)

            # additional event handling that will need to be refactored later
            # TODO: move this somewhere else
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    print("=======RECORDING=STARTS==")
                    print(self.recording.serialize())
                    print("=======RECORDING=ENDS====")
                    log.info("Return from game scene")
                    return None

            self.screen.fill("dimgray")

            self.player_group.update()
            self.shard_group.update()
            self.particle_group.update()
            self.hud_ui_group.update()

            self.environment_renderer.render(self.screen, self.vertical_shift)
            self.player_group.draw(self.screen)
            self.shard_group.draw(self.screen)
            self.particle_group.draw(self.screen)

            self.hud_ui_group.draw(self.screen)

            self.handle_collisions()

            pygame.display.update()
            self.clock.tick(TICK_SPEED)
