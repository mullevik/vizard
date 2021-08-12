import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

import pygame
from pygame.event import Event

if TYPE_CHECKING:
    from src.scene import Scene, EmptyScene, GameScene


class EventHandler(ABC):

    scene: 'Scene'

    def __init__(self, scene: 'Scene'):
        self.scene = scene

    @abstractmethod
    def handle_events(self, events: List[Event]) -> None:
        raise NotImplementedError


class AppEventHandler(EventHandler):

    def __init__(self, scene: 'Scene'):
        super().__init__(scene)

    def handle_events(self, events: List[Event]) -> None:

        for event in events:

            if event.type == pygame.QUIT:
                pygame.quit()
                print("Successful termination")
                sys.exit(0)


class TextEventHandler(EventHandler):
    text: str

    def __init__(self, scene: 'GameScene'):
        super().__init__(scene)
        self.text = ""

    def handle_events(self, events: List[Event]) -> None:
        self.text = ""  # reset the text before handling events
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.text += event.unicode

    def get_text_from_this_tick(self) -> str:
        """Return the text inputted during the last game tick.
        :return: text that may be an empty string
        """
        return self.text


