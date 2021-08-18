from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple

from src.constants import VERSION
from src.utils import Milliseconds, Position


class ParsingException(Exception):
    pass


class RecordedEvent(ABC):
    time: Milliseconds

    def __init__(self, time: Milliseconds):
        self.time = time

    @abstractmethod
    def serialize(self) -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def parse(text: str) -> 'RecordedEvent':
        raise NotImplementedError


class TextInput(RecordedEvent):
    text_input: str

    def __init__(self, time: Milliseconds, text_input: str):
        super().__init__(time)
        self.text_input = text_input

    def serialize(self) -> str:
        return f"I {self.time} {self.text_input}"

    @staticmethod
    def parse(text: str) -> 'TextInput':
        parts = text.split()
        if parts[0] != "I":
            raise ParsingException("Not a TextInput event")
        text_input = parts[2] if len(parts) == 3 else ""
        return TextInput(int(parts[1]), text_input)


class ShardSpawn(RecordedEvent):
    position: Position

    def __init__(self, time: Milliseconds, position: Position):
        super().__init__(time)
        self.position = position

    def serialize(self) -> str:
        return f"S {self.time} {self.position.x} {self.position.y}"

    @staticmethod
    def parse(text: str) -> 'ShardSpawn':
        parts = text.split()
        if parts[0] != "S" or len(parts) != 4:
            raise ParsingException("Not a ShardSpawn event")
        return ShardSpawn(int(parts[1]), Position(int(parts[2]), int(parts[3])))


class VersionInfo(RecordedEvent):
    info: str

    def __init__(self, time: Milliseconds):
        super().__init__(time)
        self.info = VERSION

    def serialize(self) -> str:
        return f"V {self.time} {self.info}"

    @staticmethod
    def parse(text: str) -> 'VersionInfo':
        parts = text.split()
        if parts[0] != "V" or len(parts) != 3:
            raise ParsingException("Not a VersionInfo event")
        version_info = VersionInfo(int(parts[1]))
        version_info.info = parts[2]
        return version_info


class Recording(object):
    start_time: Milliseconds
    data: List[RecordedEvent]

    def __init__(self):
        self.start_time = 0
        self.data = []

    def start(self, current_time: Milliseconds):
        self.start_time = current_time
        self.data = [VersionInfo(self.get_recording_time(current_time))]

    def record_text_input(self, current_time: Milliseconds, text_input: str) -> 'Recording':
        if text_input:
            self._store_event(TextInput(self.get_recording_time(current_time),
                                        text_input))
        return self

    def record_shard_spawn(self, current_time: Milliseconds,
                           spawn_position: Position) -> 'Recording':
        self._store_event(ShardSpawn(self.get_recording_time(current_time),
                                     spawn_position))
        return self

    def get_recording_time(self, current_time: Milliseconds) -> Milliseconds:
        return current_time - self.start_time

    def _store_event(self, event: RecordedEvent) -> 'Recording':
        self.data.append(event)
        return self

    def serialize(self) -> str:
        return "\n".join(map(lambda x: x.serialize(), self.data))

    @staticmethod
    def parse(text: str) -> 'Recording':
        lines = text.split("\n")

        events = []
        for line in lines:
            if len(line) == 0:
                continue

            first_char = line[0]

            try:
                if first_char == "I":
                    events.append(TextInput.parse(line))
                elif first_char == "S":
                    events.append(ShardSpawn.parse(line))
                elif first_char == "V":
                    events.append(VersionInfo.parse(line))
                else:
                    raise ParsingException("Unsupported recorded event")
            except ParsingException as e:
                raise e
            except Exception as e:
                raise ParsingException(f"Unexpected parsing error: {str(e)}")

        recording = Recording()
        recording.data = events
        return recording

