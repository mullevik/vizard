import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict, Any
import logging
log = logging.getLogger(__name__)

import pygame
from pygame.event import Event

if TYPE_CHECKING:
    from src.scene import Scene, GameScene


class EventName(str):
    pass


class Observer(ABC):

    @abstractmethod
    def subscribe(self) -> EventName:
        """Subscribe self to some event name.
        :returns the event name to which this observer just subscribed"""

    @abstractmethod
    def update(self, data: Any) -> None:
        """This method is called when an event - to which this observer
        is subscribed - happens."""


subscribers: Dict[EventName, List[Observer]] = {}


def subscribe(event_name: EventName, observer: Observer) -> EventName:
    """Subscribe an observer to a specific event name.
    :returns the event name to which the observer just subscribed"""
    if event_name in subscribers:
        subscribers[event_name].append(observer)
    subscribers[event_name] = [observer]
    return event_name


def notify(event_name: EventName, *args, **kwargs) -> None:
    """Notify all observers subscribed to an event with event name."""
    n_observers = 0
    if event_name in subscribers:
        for observer in subscribers[event_name]:
            n_observers += 1
            observer.update(*args, **kwargs)

    log.debug(f"Notifying {n_observers} observers "
              f"of event '{event_name}'")


def unsubscribe_all() -> None:
    global subscribers
    subscribers = {}


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


