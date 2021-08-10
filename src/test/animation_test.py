import unittest

from src.animation import Animation
from src.environment import Environment, EnvironmentException
from src.settings import GameSettings
from src.utils import Position


class AnimationTest(unittest.TestCase):

    def test_animation_should_end_correctly(self):
        dummy_frames = ["0", "1", "2", "3", "4"]
        dummy_delay = 100
        a = Animation(dummy_frames, dummy_delay)

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


if __name__ == '__main__':
    unittest.main()
