from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, TYPE_CHECKING

import pygame
from pygame.surface import Surface

from src.constants import ANIM_VIZARD_DASH, ANIM_VIZARD_IDLE
from src.utils import Milliseconds, load_scaled_surfaces

if TYPE_CHECKING:
    from src.scene import GameScene


class AnimationException(Exception):
    pass


class Animation(object):
    """
    Class defining a discrete animation of multiple frames.
    The 'speed' determines the number of milliseconds between two
    frames and is constant during the whole animation.
    """
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

    def start(self, current_time: Milliseconds = None) -> None:
        """Starts the animation from the beginning."""
        self.current_time = current_time
        self.start_time = current_time

    def get_start_time(self) -> Milliseconds:
        """Returns the start_time.
        :return: the timestamp that marks the beginning of this animation
        """
        return self.start_time

    def get_duration(self) -> Milliseconds:
        return len(self.frames) * self.speed

    def is_over(self) -> bool:
        return (not self.loop
                and self._get_animation_time() >= self.get_duration())

    def get_image(self, current_time: Milliseconds) -> Surface:
        """Get the corresponding animation frame.
        :return: the surface of the frame that should be active at 'current_time'
        """
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

    def copy(self) -> 'Animation':
        """Creates a new copy of this animation. The frames are
        shallow-copied, other attributes are deep-copied.
        :return a copy of this animation"""
        # return Animation(self.frames, self.speed, self.loop)
        return Animation(self.frames, self.speed, self.loop)


class LinearAlphaFadeAnimation(Animation):
    """
    Animates frames so that the first frame is opaque and the
    last frame is transparent. Frames in between are interpolated
    linearly.
    """

    def __init__(self, frames: List[Surface], speed: Milliseconds,
                 loop: bool = False):
        super().__init__(frames, speed, loop)

    def get_image(self, current_time: Milliseconds) -> Surface:
        image = super().get_image(current_time)
        time = self._get_animation_time()
        duration = self.get_duration()

        # determine how much alpha should the image have (from 1. to 0.)
        alpha_fraction = (duration - time) / duration if time < duration else 0
        # rescale it to the 0-255 values (255 is opaque)
        alpha = int(255 * alpha_fraction)

        image.set_alpha(alpha)
        return image

    def copy(self) -> 'LinearAlphaFadeAnimation':
        return LinearAlphaFadeAnimation(self.frames, self.speed, self.loop)


class FallbackAnimator(object):
    """
    An animator that has one looping animation (idle or fallback)
    and multiple one-shot animations.
    Whenever a one-shot animation ends,
    the animator switches to the looping animation.
    """
    fallback_animation_name: str
    animations: Dict[str, Animation]
    current_animation: Animation

    def __init__(self, animations: Dict[str, Animation]):
        self.animations = animations

        n_looping_animations = 0
        for animation_name, animation in animations.items():
            if animation.loop:
                self.fallback_animation_name = animation_name
                n_looping_animations += 1

        if n_looping_animations != 1:
            raise AnimationException(f"Wrong number of looping animations provided, "
                                     f"expected 1, got {n_looping_animations}")

        self.current_animation = animations[self.fallback_animation_name]

    def start(self, current_time: Milliseconds) -> None:
        """Start animating the looping animation."""
        self.current_animation.start(current_time)

    def start_animation(self, animation_name: str,
                        current_time: Milliseconds) -> None:
        """Start any animation by its name.
        The new animation starts immediately."""
        if animation_name not in self.animations:
            raise AnimationException(f"Animation '{animation_name}' not found "
                                     f"in this animator")
        self.current_animation = self.animations[animation_name]
        self.current_animation.start(current_time)

    def get_image(self, current_time: Milliseconds) -> Surface:
        """Get the corresponding frame of current animation.
        :return: the surface of the animation frame"""

        current_animation_frame = self.current_animation.get_image(current_time)

        if not self.current_animation.is_over():
            # current animation frame is from the correct animation
            return current_animation_frame
        else:
            # current animation frame is already out of date
            # calculate when should had the fallback animation started
            end = self.current_animation.get_start_time() + \
                  self.current_animation.get_duration()

            if end > current_time:
                raise AnimationException("Unexpected animator timing")

            # switch to fallback animation
            self.current_animation = self.animations[self.fallback_animation_name]
            self.current_animation.start(end)
            return self.current_animation.get_image(current_time)


class AnimationManager(object):

    animations: Dict[str, Animation]

    def __init__(self, scene: 'GameScene'):
        scale_factor = scene.settings.scale_factor

        idle_frames = load_scaled_surfaces(ANIM_VIZARD_IDLE, scale_factor)
        dash_frames = load_scaled_surfaces(ANIM_VIZARD_DASH, scale_factor)
        dash_image = dash_frames[0]

        self.animations = {
            "idle": Animation(idle_frames, 600, loop=True),
            "dash": Animation(dash_frames, 100),
            "dash-right-particle":
                LinearAlphaFadeAnimation([dash_image.copy()], 300),
            "dash-left-particle": LinearAlphaFadeAnimation(
                [pygame.transform.flip(dash_image, True, False)], 300),
        }

    def get_animation(self, name: str) -> Animation:
        return self.animations[name].copy()


