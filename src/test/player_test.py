import unittest

from src.action import ActionException
from src.environment import Environment, EnvironmentException
from src.player import Player, HorizontalMoveAction, VerticalMoveAction, \
    GrassStartJumpAction, GrassEndJumpAction, ContourJumpAction
from src.settings import GameSettings
from src.utils import Position, CardinalDirection


class SimplePlayerTest(unittest.TestCase):

    def setUp(self) -> None:
        dummy_map = "..........\n" \
                    "..//o//...\n" \
                    "....S.....\n" \
                    "//..//// .\n" \
                    ".........."

        self.settings = GameSettings(scale_factor=1.)
        self.environment = Environment(self.settings, dummy_map)
        self.player = Player()
        self.player.set_position(self.environment.get_starting_position())

    def test_player_should_start_at_the_start_position(self):
        self.assertEqual((4, 2), self.player.get_position())

    def test_player_should_move_horizontally_within_bounds(self):
        # One step right
        self.player.apply_action(HorizontalMoveAction(self.environment, 1))
        self.assertEqual((5, 2), self.player.get_position())

        # Two steps left
        self.player.apply_action(HorizontalMoveAction(self.environment, -2))
        self.assertEqual((3, 2), self.player.get_position())

        # Three steps left
        self.player.apply_action(HorizontalMoveAction(self.environment, -3))
        self.assertEqual((0, 2), self.player.get_position())

        # Nine steps right
        self.player.apply_action(HorizontalMoveAction(self.environment, 9))
        self.assertEqual((9, 2), self.player.get_position())

    def test_player_should_not_move_horizontally_outside_the_bounds(self):
        # Five step right - OK
        self.player.apply_action(HorizontalMoveAction(self.environment, 5))
        self.assertEqual((9, 2), self.player.get_position())

        # One more step right - not OK
        self.assertRaises(ActionException, lambda: self.player.apply_action(
            HorizontalMoveAction(self.environment, 1)))

        # Ten steps right - not OK
        self.assertRaises(ActionException, lambda: self.player.apply_action(
            HorizontalMoveAction(self.environment, 10)))

        # Nine steps left - OK
        self.player.apply_action(HorizontalMoveAction(self.environment, -9))
        self.assertEqual((0, 2), self.player.get_position())

        # One more step left - not OK
        self.assertRaises(ActionException, lambda: self.player.apply_action(
            HorizontalMoveAction(self.environment, -1)))

        # 500 steps left - not OK
        self.assertRaises(ActionException, lambda: self.player.apply_action(
            HorizontalMoveAction(self.environment, -500)))

    def test_player_should_not_move_horizontally_on_gaps(self):
        # One step down - OK
        self.player.apply_action(VerticalMoveAction(self.environment, 1))
        self.assertEqual((4, 3), self.player.get_position())

        # Four steps right - not OK
        self.assertRaises(ActionException, lambda: self.player.apply_action(
            HorizontalMoveAction(self.environment, 4)))

    def test_player_should_move_vertically_within_bounds(self):
        # One step up
        self.player.apply_action(VerticalMoveAction(self.environment, -1))
        self.assertEqual((4, 1), self.player.get_position())

        # Three steps down
        self.player.apply_action(VerticalMoveAction(self.environment, 3))
        self.assertEqual((4, 4), self.player.get_position())

        # Four steps up
        self.player.apply_action(VerticalMoveAction(self.environment, -4))
        self.assertEqual((4, 0), self.player.get_position())

    def test_player_should_not_move_vertically_outside_the_bounds(self):
        # Two steps up - OK
        self.player.apply_action(VerticalMoveAction(self.environment, -2))
        self.assertEqual((4, 0), self.player.get_position())

        # One more step up - not OK
        self.assertRaises(ActionException, lambda: self.player.apply_action(
            VerticalMoveAction(self.environment, -1)))

        # 120 step up - not OK
        self.assertRaises(ActionException, lambda: self.player.apply_action(
            VerticalMoveAction(self.environment, -120)))

        # Four steps down - OK
        self.player.apply_action(VerticalMoveAction(self.environment, 4))
        self.assertEqual((4, 4), self.player.get_position())

        # One more step down - not OK
        self.assertRaises(ActionException, lambda: self.player.apply_action(
            VerticalMoveAction(self.environment, 1)))

        # 60 step down - not OK
        self.assertRaises(ActionException, lambda: self.player.apply_action(
            VerticalMoveAction(self.environment, 60)))

    def test_player_should_not_move_vertically_on_gaps(self):
        # Four steps right - OK
        self.player.apply_action(HorizontalMoveAction(self.environment, 4))
        self.assertEqual((8, 2), self.player.get_position())

        # One step down - not OK
        self.assertRaises(ActionException, lambda: self.player.apply_action(
            VerticalMoveAction(self.environment, 1)))


class GrassJumpsTest(unittest.TestCase):

    def setUp(self) -> None:
        #            0         10        20 "
        #            0123456789|123456789|12"
        dummy_map = "S.//o///..oo//o///.. \n" \
                    " ..//..              "

        self.settings = GameSettings(scale_factor=1.)
        self.environment = Environment(self.settings, dummy_map)
        self.player = Player()
        self.player.set_position(self.environment.get_starting_position())

    def test_player_should_start_at_the_start_position(self):
        self.assertEqual((0, 0), self.player.get_position())

    def test_player_should_normal_grass_jump_correctly(self):
        this = self

        def jump_right():
            this.player.apply_action(
                GrassStartJumpAction(this.environment, CardinalDirection.EAST))

        def jump_left():
            this.player.apply_action(
                GrassStartJumpAction(this.environment, CardinalDirection.WEST))

        jump_right()
        self.assertEqual((2, 0), self.player.get_position())
        jump_right()
        self.assertEqual((4, 0), self.player.get_position())
        jump_right()
        self.assertEqual((5, 0), self.player.get_position())
        jump_right()
        self.assertEqual((10, 0), self.player.get_position())
        jump_right()
        self.assertEqual((12, 0), self.player.get_position())
        jump_right()
        self.assertEqual((14, 0), self.player.get_position())
        jump_right()
        self.assertEqual((15, 0), self.player.get_position())
        jump_right()
        self.assertEqual((3, 1), self.player.get_position())
        self.assertRaises(ActionException, jump_right)

        jump_left()
        self.assertEqual((17, 0), self.player.get_position())
        jump_left()
        self.assertEqual((14, 0), self.player.get_position())
        jump_left()
        self.assertEqual((13, 0), self.player.get_position())
        jump_left()
        self.assertEqual((11, 0), self.player.get_position())
        jump_left()
        self.assertEqual((7, 0), self.player.get_position())
        jump_left()
        self.assertEqual((4, 0), self.player.get_position())
        jump_left()
        self.assertEqual((3, 0), self.player.get_position())
        self.assertRaises(ActionException, jump_left)

    def test_player_should_stone_grass_jump_correctly(self):
        this = self

        def jump_right():
            this.player.apply_action(
                GrassStartJumpAction(this.environment, CardinalDirection.EAST,
                                     ignore_stones=True))

        def jump_left():
            this.player.apply_action(
                GrassStartJumpAction(this.environment, CardinalDirection.WEST,
                                     ignore_stones=True))

        jump_right()
        self.assertEqual((2, 0), self.player.get_position())
        jump_right()
        self.assertEqual((10, 0), self.player.get_position())
        jump_right()
        self.assertEqual((3, 1), self.player.get_position())
        self.assertRaises(ActionException, jump_right)

        jump_left()
        self.assertEqual((17, 0), self.player.get_position())
        jump_left()
        self.assertEqual((7, 0), self.player.get_position())
        self.assertRaises(ActionException, jump_left)

    def test_player_should_normal_end_jump_correctly(self):
        this = self

        def jump_right():
            this.player.apply_action(
                GrassEndJumpAction(this.environment, CardinalDirection.EAST))

        def jump_left():
            this.player.apply_action(
                GrassEndJumpAction(this.environment, CardinalDirection.WEST))

        jump_right()
        self.assertEqual((3, 0), self.player.get_position())
        jump_right()
        self.assertEqual((4, 0), self.player.get_position())
        jump_right()
        self.assertEqual((7, 0), self.player.get_position())
        jump_right()
        self.assertEqual((11, 0), self.player.get_position())
        jump_right()
        self.assertEqual((13, 0), self.player.get_position())
        jump_right()
        self.assertEqual((14, 0), self.player.get_position())
        jump_right()
        self.assertEqual((17, 0), self.player.get_position())
        jump_right()
        self.assertEqual((4, 1), self.player.get_position())
        self.assertRaises(ActionException, jump_right)

        jump_left()
        self.assertEqual((3, 1), self.player.get_position())
        jump_left()
        self.assertEqual((15, 0), self.player.get_position())
        jump_left()
        self.assertEqual((14, 0), self.player.get_position())
        jump_left()
        self.assertEqual((12, 0), self.player.get_position())
        jump_left()
        self.assertEqual((10, 0), self.player.get_position())
        jump_left()
        self.assertEqual((5, 0), self.player.get_position())
        jump_left()
        self.assertEqual((4, 0), self.player.get_position())
        jump_left()
        self.assertEqual((2, 0), self.player.get_position())
        self.assertRaises(ActionException, jump_left)

    def test_player_should_stone_end_jump_correctly(self):
        this = self

        def jump_right():
            this.player.apply_action(
                GrassEndJumpAction(this.environment, CardinalDirection.EAST,
                                   ignore_stones=True))

        def jump_left():
            this.player.apply_action(
                GrassEndJumpAction(this.environment, CardinalDirection.WEST,
                                   ignore_stones=True))

        jump_right()
        self.assertEqual((7, 0), self.player.get_position())
        jump_right()
        self.assertEqual((17, 0), self.player.get_position())
        jump_right()
        self.assertEqual((4, 1), self.player.get_position())
        self.assertRaises(ActionException, jump_right)

        jump_left()
        self.assertEqual((3, 1), self.player.get_position())
        jump_left()
        self.assertEqual((10, 0), self.player.get_position())
        jump_left()
        self.assertEqual((2, 0), self.player.get_position())
        self.assertRaises(ActionException, jump_left)

    def test_player_should_end_jump_in_special_cases_correctly(self):
        this = self
        #            0123456789
        dummy_map = "o/.S./////"

        self.environment = Environment(self.settings, dummy_map)
        self.player.set_position(self.environment.get_starting_position())

        def jump_right():
            this.player.apply_action(
                GrassEndJumpAction(this.environment, CardinalDirection.EAST))

        def jump_left():
            this.player.apply_action(
                GrassEndJumpAction(this.environment, CardinalDirection.WEST))

        jump_right()
        self.assertEqual((9, 0), self.player.get_position())
        self.assertRaises(ActionException, jump_right)

        jump_left()
        self.assertEqual((5, 0), self.player.get_position())
        jump_left()
        self.assertEqual((1, 0), self.player.get_position())
        jump_left()
        self.assertEqual((0, 0), self.player.get_position())
        self.assertRaises(ActionException, jump_left)


class ContourJumpTest(unittest.TestCase):

    def setUp(self) -> None:
        #            0         10        20 "
        #            0123456789|123456789|12"
        dummy_map = "  .o/o///.Soo//o///.. \n" \
                    " ..//..               "
        self.settings = GameSettings(scale_factor=1.)
        self.environment = Environment(self.settings, dummy_map)
        self.player = Player()
        self.player.set_position(self.environment.get_starting_position())

    def test_player_should_start_at_the_start_position(self):
        self.assertEqual((10, 0), self.player.get_position())

    def test_player_should_normal_contour_jump_correctly(self):
        this = self

        def jump_right():
            this.player.apply_action(
                ContourJumpAction(this.environment, CardinalDirection.EAST))

        def jump_left():
            this.player.apply_action(
                ContourJumpAction(this.environment, CardinalDirection.WEST))

        jump_right()
        self.assertEqual((20, 0), self.player.get_position())
        jump_right()
        self.assertEqual((20, 0), self.player.get_position())

        jump_left()
        self.assertEqual((2, 0), self.player.get_position())
        jump_left()
        self.assertEqual((2, 0), self.player.get_position())

    def test_player_should_vegetation_contour_jump_correctly(self):
        this = self

        def jump_right():
            this.player.apply_action(
                ContourJumpAction(this.environment, CardinalDirection.EAST,
                                  to_vegetation=True))

        def jump_left():
            this.player.apply_action(
                ContourJumpAction(this.environment, CardinalDirection.WEST,
                                  to_vegetation=True))

        jump_right()
        self.assertEqual((18, 0), self.player.get_position())
        jump_right()
        self.assertEqual((18, 0), self.player.get_position())

        jump_left()
        self.assertEqual((3, 0), self.player.get_position())
        jump_left()
        self.assertEqual((3, 0), self.player.get_position())


if __name__ == '__main__':
    unittest.main()
