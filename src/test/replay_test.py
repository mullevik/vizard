import unittest
from typing import cast

from src.animation import Animation, FallbackAnimator, AnimationException
from src.constants import VERSION
from src.environment import Environment, EnvironmentException
from src.replay import Recording, VersionInfo, TextInput, ShardSpawn
from src.settings import GameSettings
from src.utils import Position


class ReplayTest(unittest.TestCase):

    def test_should_record_correctly(self):
        r = Recording()
        r.start(10_000)

        r.record_text_input(10_100, "kLhi")
        r.record_text_input(10_200, "k")
        r.record_shard_spawn(10_300, Position(1, 1))
        r.record_text_input(10_500, "I")

        self.assertEqual(5, len(r.data))
        self.assertEqual(0, r.data[0].time)
        self.assertIsInstance(r.data[0], VersionInfo)
        self.assertEqual(100, r.data[1].time)
        self.assertIsInstance(r.data[1], TextInput)
        self.assertEqual(200, r.data[2].time)
        self.assertIsInstance(r.data[2], TextInput)
        self.assertEqual(300, r.data[3].time)
        self.assertIsInstance(r.data[3], ShardSpawn)
        self.assertEqual(500, r.data[4].time)
        self.assertIsInstance(r.data[4], TextInput)

    def test_should_serialize_correctly(self):
        r = Recording()
        r.start(10_000)

        r.record_text_input(10_100, "kLhi")
        r.record_text_input(10_200, "k")
        r.record_shard_spawn(10_300, Position(1, 1))
        r.record_text_input(10_500, "I")

        output = r.serialize()

        self.assertEqual(5, len(output.split("\n")))
        self.assertEqual(f"V 0 {VERSION}\nI 100 kLhi\nI 200 k\nS 300 1 1\nI 500 I",
                         output)

    def test_should_parse_correctly(self):
        input_string = "V 0 test\nI 100 kLhi\nI 200 k\nS 300 1 1\nI 500 I\n"

        r = Recording.parse(input_string)

        self.assertEqual(5, len(r.data))
        self.assertEqual(0, r.data[0].time)
        self.assertEqual("test", cast(VersionInfo, r.data[0]).info)
        self.assertIsInstance(r.data[0], VersionInfo)
        self.assertEqual("kLhi", cast(TextInput, r.data[1]).text_input)
        self.assertEqual(100, r.data[1].time)
        self.assertIsInstance(r.data[1], TextInput)
        self.assertEqual("k", cast(TextInput, r.data[2]).text_input)
        self.assertEqual(200, r.data[2].time)
        self.assertIsInstance(r.data[2], TextInput)
        self.assertEqual((1, 1), cast(ShardSpawn, r.data[3]).position)
        self.assertEqual(300, r.data[3].time)
        self.assertIsInstance(r.data[3], ShardSpawn)
        self.assertEqual(500, r.data[4].time)
        self.assertEqual("I", cast(TextInput, r.data[4]).text_input)
        self.assertIsInstance(r.data[4], TextInput)


if __name__ == '__main__':
    unittest.main()
