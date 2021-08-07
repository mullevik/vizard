import unittest

from src.environment import Environment, EnvironmentException
from src.settings import GameSettings
from src.utils import Position


class EnvironmentTest(unittest.TestCase):

    def setUp(self) -> None:
        self.settings = GameSettings(scale_factor=1.)

    def test_simple_environment_creation(self):
        dummy_map = "S...."

        e = Environment(self.settings, dummy_map)
        self.assertEqual(10, len(e.get_all_tiles()))

        # first row is walkable
        for tile in e.get_all_tiles()[:5]:
            self.assertTrue(tile.is_walkable())
            self.assertFalse(tile.is_dirt())

        # second row is non-walkable dirt
        for tile in e.get_all_tiles()[5:]:
            self.assertFalse(tile.is_walkable())
            self.assertTrue(tile.is_dirt())

    def test_standard_environment_creation(self):
        dummy_map = "/o/..\n" \
                    "S.../"

        e = Environment(self.settings, dummy_map)
        self.assertEqual(15, len(e.get_all_tiles()))

        # First tile is walkable grass and not dirt
        first_tile = e.tile_at(Position(0, 0))
        self.assertTrue(first_tile.is_walkable())
        self.assertFalse(first_tile.is_dirt())
        self.assertTrue(first_tile.is_grass())

        # Second tile is walkable stone and not dirt
        second_tile = e.tile_at(Position(1, 0))
        self.assertTrue(second_tile.is_walkable())
        self.assertFalse(second_tile.is_dirt())
        self.assertTrue(second_tile.is_stone())

        # Last tile is walkable grass with dirt
        last_tile = e.tile_at(Position(4, 1))
        self.assertTrue(last_tile.is_walkable())
        self.assertTrue(last_tile.is_dirt())
        self.assertTrue(last_tile.is_grass())

    def test_wrong_environment_should_not_be_created(self):
        settings = self.settings
        dummy_map = "....."  # no start

        def create():
            return Environment(settings, dummy_map)

        self.assertRaises(EnvironmentException, create)

        dummy_map = "...\n" \
                    "S..."  # different row sizes

        self.assertRaises(EnvironmentException, create)


if __name__ == '__main__':
    unittest.main()
