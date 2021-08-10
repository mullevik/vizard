from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from pygame.surface import Surface

from src.utils import Milliseconds


class Animation(object):
    frames: List[Surface]
    speed: Milliseconds  # number of milliseconds between two frames
    loop: bool  # whether to loop this animation
    start_time: Milliseconds  # when did this animation start
    current_time: Milliseconds  # internal number of ms for the animation

    def __init__(self, frames: List[Surface], speed: Milliseconds,
                 loop: bool = False):
        self.frames = frames
        self.speed = speed
        self.loop = loop
        self.start_time = 0
        self.current_time = 0

    def start(self, current_time: Milliseconds) -> None:
        """Starts the animation from the beginning."""
        self.current_time = current_time
        self.start_time = current_time

    def is_over(self) -> bool:
        return (not self.loop
                and self._get_animation_time() >
                self.speed * (len(self.frames) - 1))

    def get_image(self, current_time: Milliseconds) -> Surface:
        self.current_time = current_time
        time = self._get_animation_time()

        frame_index = time // self.speed

        if frame_index < len(self.frames):
            return self.frames[frame_index]
        else:
            # there are no images that far in the animation
            if self.loop:
                # return cyclic animation if looping is enabled
                return self.frames[frame_index % len(self.frames)]
            else:
                # return last image if looping is not enabled
                return self.frames[-1]

    def _get_animation_time(self) -> Milliseconds:
        return self.current_time - self.start_time















