import unittest
from dataclasses import dataclass
from typing import cast

import pygame

from src.animation import Animation, FallbackAnimator, AnimationException, \
    LinearAlphaFadeAnimation
from src.environment import Environment, EnvironmentException
from src.settings import GameSettings
from src.utils import Position


@dataclass
class MockedAlphaSurface:
    frame: str  # test frame
    alpha: int = 255

    def set_alpha(self, value: int):
        self.alpha = value

    def get_alpha(self) -> int:
        return self.alpha


class AnimationTest(unittest.TestCase):

    def test_animation_should_end_correctly(self):
        dummy_frames = ["0", "1", "2", "3", "4"]
        dummy_delay = 100
        a = Animation(dummy_frames, dummy_delay)

        self.assertEqual(500, a.get_duration())

        # start animation at 10_000-th millisecond
        a.start(10_000)
        self.assertFalse(a.is_over())
        self.assertEqual("0", a.get_image(10_000))
        self.assertEqual("0", a.get_image(10_050))
        self.assertFalse(a.is_over())
        self.assertEqual("1", a.get_image(10_100))
        self.assertEqual("1", a.get_image(10_199))
        self.assertFalse(a.is_over())
        self.assertEqual("3", a.get_image(10_333))
        self.assertEqual("3", a.get_image(10_366))
        self.assertFalse(a.is_over())
        self.assertEqual("4", a.get_image(10_400))
        self.assertFalse(a.is_over())
        self.assertEqual("4", a.get_image(10_500))
        self.assertTrue(a.is_over())
        self.assertEqual("4", a.get_image(22_222))
        self.assertTrue(a.is_over())

    def test_animation_should_loop_forever(self):
        dummy_frames = ["0", "1", "2"]
        dummy_delay = 10
        a = Animation(dummy_frames, dummy_delay, loop=True)

        # start animation at 100-th millisecond
        a.start(100)
        self.assertFalse(a.is_over())
        self.assertEqual("0", a.get_image(100))
        self.assertEqual("0", a.get_image(101))
        self.assertFalse(a.is_over())
        self.assertEqual("2", a.get_image(120))
        self.assertEqual("2", a.get_image(129))
        self.assertFalse(a.is_over())
        self.assertEqual("0", a.get_image(130))
        self.assertFalse(a.is_over())
        self.assertEqual("1", a.get_image(145))
        self.assertFalse(a.is_over())
        self.assertEqual("2", a.get_image(150))
        self.assertFalse(a.is_over())
        self.assertEqual("1", a.get_image(410))
        self.assertFalse(a.is_over())


class LinearAlphaFadeAnimationTest(unittest.TestCase):

    def test_animation_should_end_correctly(self):

        dummy_frames = [
            MockedAlphaSurface("A"),
            MockedAlphaSurface("B"),
            MockedAlphaSurface("C"),
            MockedAlphaSurface("D"),
        ]
        a = LinearAlphaFadeAnimation(dummy_frames, 100)

        self.assertEqual(400, a.get_duration())

        # start animation at 10_000-th millisecond
        a.start(10_000)
        self.assertFalse(a.is_over())
        self.assertEqual("A", cast(MockedAlphaSurface, a.get_image(10_000)).frame)
        self.assertEqual(255, a.get_image(10_000).get_alpha())

        self.assertEqual("A",
                         cast(MockedAlphaSurface, a.get_image(10_050)).frame)
        self.assertGreater(255, a.get_image(10_050).get_alpha())
        self.assertLess(255 / 4 * 3, a.get_image(10_050).get_alpha())

        self.assertEqual("B",
                         cast(MockedAlphaSurface, a.get_image(10_100)).frame)
        self.assertGreater(255, a.get_image(10_100).get_alpha())
        self.assertLess(255 / 4 * 2, a.get_image(10_100).get_alpha())

        self.assertEqual("D",
                         cast(MockedAlphaSurface, a.get_image(10_300)).frame)
        self.assertGreater(255 / 4 * 2, a.get_image(10_300).get_alpha())
        self.assertLess(0, a.get_image(10_300).get_alpha())

        self.assertEqual(0, a.get_image(10_400).get_alpha())


class FallbackAnimatorTest(unittest.TestCase):

    def test_animator_should_be_initialized_correctly(self):
        dummy_frames = ["A", "B", "C"]
        dummy_delay = 100
        a1 = Animation(dummy_frames, dummy_delay, loop=True)

        animator = FallbackAnimator({"0": a1})

        animator.start(10_000)
        self.assertEqual("A", animator.get_image(10_000))

    def test_animator_should_not_initialize_with_bad_animations(self):
        dummy_frames = ["A", "B", "C"]
        dummy_delay = 100
        a1 = Animation(dummy_frames, dummy_delay, loop=True)

        dummy_frames = ["E", "F", "G"]
        dummy_delay = 50
        a2 = Animation(dummy_frames, dummy_delay, loop=True)

        dummy_frames = ["H", "I", "J"]
        dummy_delay = 10
        a3 = Animation(dummy_frames, dummy_delay)

        dummy_frames = ["K", "L", "M"]
        dummy_delay = 2000
        a4 = Animation(dummy_frames, dummy_delay)

        self.assertRaises(AnimationException,
                          lambda: FallbackAnimator({"0": a1, "1": a2}))
        self.assertRaises(AnimationException,
                          lambda: FallbackAnimator({"2": a3, "3": a4}))

    def test_animator_should_animate_correctly(self):
        a1 = Animation(["A", "B"], 100, loop=True)

        a2 = Animation(["C", "D"], 10)

        animator = FallbackAnimator({"0": a1, "1": a2})
        animator.start(10_000)

        self.assertEqual("A", animator.get_image(10_000))
        self.assertEqual("B", animator.get_image(10_120))
        # looping animation loops
        self.assertEqual("A", animator.get_image(10_210))

        # start other animation
        animator.start_animation("1", 10_210)
        self.assertEqual("C", animator.get_image(10_210))
        self.assertEqual("C", animator.get_image(10_219))
        self.assertEqual("D", animator.get_image(10_225))
        # fallback to looping animation
        self.assertEqual("A", animator.get_image(10_235))
        self.assertEqual("A", animator.get_image(10_329))
        self.assertEqual("B", animator.get_image(10_330))


if __name__ == '__main__':
    unittest.main()
