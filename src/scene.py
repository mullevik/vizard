import random
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import pygame
import yaml
from pygame.event import Event
from pygame.surface import Surface
from pygame.time import Clock

from src.action import ActionException
from src.constants import FRAME_RATE
from src.environment import Environment, EnvironmentRenderer
from src.player import Player, PlayerSprite, HorizontalMoveAction, \
    VerticalMoveAction, GrassStartJumpAction, GrassEndJumpAction
from src.settings import GameSettings
from src.shard import ShardSprite, Shard
from src.utils import Position, CardinalDirection


class SceneException(Exception):
    pass


class Scene(ABC):
    screen: Surface
    clock: Clock

    def __init__(self, screen: Surface, clock: Clock):
        self.screen = screen
        self.clock = clock

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

    # noinspection PyMethodMayBeStatic
    def extract_events(self) -> List[Event]:
        """
        Handles general purpose events like closing the window.
        Every scene should override this method with its custom event handling,
        but it should always call this super().handle_events() first.
        """
        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                pygame.quit()
                print("Successful termination")
                sys.exit(0)

        return events

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
            for event in self.extract_events():

                if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    print("Starting game")
                    return GameScene.__name__

            self.screen.fill("gray")

            pygame.display.update()
            self.clock.tick(FRAME_RATE)


class GameScene(Scene):

    def __init__(self, screen: Surface, clock: Clock):
        super().__init__(screen, clock)

        self.settings = GameSettings(
            **yaml.load(open("../config.yaml"), Loader=yaml.FullLoader))

        self.environment = Environment(self.settings,
                                       open("../assets/maps/default.txt",
                                            "r").read())
        self.environment_renderer = EnvironmentRenderer(self.environment,
                                                        self.settings)

        self.player = Player()
        self.player.set_position(self.environment.get_starting_position())
        self.player_sprite = PlayerSprite(self.player, self.settings)
        self.player_group = pygame.sprite.GroupSingle(self.player_sprite)

        self.shard_group = pygame.sprite.Group([])

        self.spawn_shard(Position(3, 1))

    def spawn_shard(self, position: Position):
        self.shard_group.add(ShardSprite(self, Shard(position)))

    def spawn_random_shard(self):
        w, h = self.environment.get_tile_dimensions()
        random_position = None
        while not random_position or \
                not self.environment.tile_at(random_position).is_walkable():
            x = random.randint(0, w - 1)
            y = random.randint(0, h - 2)
            random_position = Position(x, y)

        self.spawn_shard(random_position)

    def handle_collisions(self):
        colliding_sprites = pygame.sprite.spritecollide(
            self.player_sprite, self.shard_group, dokill=False,
            collided=self.is_player_colliding_with_shard)

        if colliding_sprites:
            print("COLLISION")
            number_of_shards = len(colliding_sprites)
            self.shard_group.remove(colliding_sprites)
            for i in range(number_of_shards):
                self.spawn_random_shard()

    @staticmethod
    def is_player_colliding_with_shard(player: PlayerSprite,
                                       shard: ShardSprite):
        return player.rect.colliderect(shard.hitbox)

    def run(self) -> bool:

        is_shift_active = False
        while True:

            for event in self.extract_events():

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    print("ESCAPE FROM DEFAULT SCENE")
                    return None

                if event.type == pygame.KEYDOWN and event.key == pygame.K_LSHIFT:
                    is_shift_active = True
                if event.type == pygame.KEYUP and event.key == pygame.K_LSHIFT:
                    is_shift_active = False

                try:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                        self.player.apply_action(
                            HorizontalMoveAction(self.environment, -1))
                        print("MOVE LEFT")
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_j:
                        self.player.apply_action(
                            VerticalMoveAction(self.environment, 1))
                        print("MOVE DOWN")
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_k:
                        self.player.apply_action(
                            VerticalMoveAction(self.environment, -1))
                        print("MOVE UP")
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                        self.player.apply_action(
                            HorizontalMoveAction(self.environment, 1))
                        print("MOVE RIGHT")
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                        self.player.apply_action(
                            GrassStartJumpAction(self.environment,
                                                 CardinalDirection.EAST))
                        print("GRASS-START JUMP RIGHT (consider stones")
                    if (event.type == pygame.KEYDOWN
                            and event.key == pygame.K_e and not is_shift_active):
                        self.player.apply_action(
                            GrassEndJumpAction(self.environment,
                                               CardinalDirection.EAST))
                        print("GRASS-END JUMP RIGHT (consider stones)")

                    if (event.type == pygame.KEYDOWN
                            and event.key == pygame.K_e and is_shift_active):
                        self.player.apply_action(
                            GrassEndJumpAction(self.environment,
                                               CardinalDirection.EAST,
                                               ignore_stones=True))
                        print("GRASS-END JUMP RIGHT (ignore stones)")

                    if (event.type == pygame.KEYDOWN
                            and event.key == pygame.K_b and not is_shift_active):
                        self.player.apply_action(
                            GrassEndJumpAction(self.environment,
                                               CardinalDirection.WEST))
                        print("GRASS-END JUMP LEFT (consider stones)")

                    if (event.type == pygame.KEYDOWN
                            and event.key == pygame.K_b and is_shift_active):
                        self.player.apply_action(
                            GrassEndJumpAction(self.environment,
                                               CardinalDirection.WEST,
                                               ignore_stones=True))
                        print("GRASS-END JUMP LEFT (ignore stones)")

                except ActionException as e:
                    print(f"INVALID ACTION: {e}")

            self.screen.fill("cadetblue2")

            self.environment_renderer.render(self.screen)
            self.player_group.update()
            self.player_group.draw(self.screen)

            self.shard_group.update()
            self.shard_group.draw(self.screen)

            self.handle_collisions()

            pygame.display.update()
            self.clock.tick(FRAME_RATE)
