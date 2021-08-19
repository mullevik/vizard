from dataclasses import dataclass
from typing import Dict
import logging

log = logging.getLogger(__name__)


class Key(str):
    pass


class GameSettings:

    scale_factor: float
    controls: Dict[str, str]
    buffer_keys: str
    key_event_map: Dict[Key, str]

    def __init__(self,
                 scale_factor: float = 5.,
                 controls: Dict[str, Key] = None,
                 buffer_keys: str = "g"):
        self.scale_factor = scale_factor
        self.controls = controls
        self.buffer_keys = buffer_keys

        self.key_event_map = {}

        if controls is None:
            log.warning("No controls found")
            return
        for event_name, key_char in controls.items():
            if isinstance(key_char, str):
                self.key_event_map[key_char] = event_name
            elif isinstance(key_char, int):
                # decode byte into an ascii string character
                self.key_event_map[
                    bytes([key_char]).decode('ascii')] = event_name
            else:
                raise TypeError(f"Unknown key type ({type(key_char)}) "
                                f"in controls")


