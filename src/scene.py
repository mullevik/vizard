import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import pygame
import yaml
from pygame.event import Event
from pygame.surface import Surface
from pygame.time import Clock

from src.constants import FRAME_RATE
from src.environment import Environment, EnvironmentRenderer
from src.player import Player, PlayerSprite, HorizontalMoveAction
from src.settings import GameSettings


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
                    return DefaultScene.__name__

            self.screen.fill("gray")

            pygame.display.update()
            self.clock.tick(FRAME_RATE)


class DefaultScene(Scene):

    def __init__(self, screen: Surface, clock: Clock):
        super().__init__(screen, clock)

        self.settings = GameSettings(
            **yaml.load(open("../config.yaml"), Loader=yaml.FullLoader))

        self.environment = Environment(self.settings,
                                       open("../assets/maps/default.txt", "r").read())
        self.environment_renderer = EnvironmentRenderer(self.environment, self.settings)

        self.player = Player()
        self.player.set_position(self.environment.get_starting_position())
        self.player_sprite = PlayerSprite(self.player, self.settings)
        self.player_group = pygame.sprite.GroupSingle(self.player_sprite)

    def run(self) -> bool:

        while True:
            for event in self.extract_events():

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    print("ESCAPE FROM DEFAULT SCENE")
                    return None

                if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                    self.player.apply_action(HorizontalMoveAction(self.environment, -1))
                    print("MOVE LEFT")
                if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                    self.player.apply_action(HorizontalMoveAction(self.environment, 1))
                    print("MOVE UP")

            self.screen.fill("dimgray")

            self.environment_renderer.render(self.screen)
            self.player_group.draw(self.screen)
            self.player_group.update()

            pygame.display.update()
            self.clock.tick(FRAME_RATE)


