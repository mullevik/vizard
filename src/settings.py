from dataclasses import dataclass
from typing import Dict
import logging

log = logging.getLogger(__name__)


class Key(str):
    pass


class GameSettings:

    scale_factor: float
    controls: Dict[str, str]
    key_event_map: Dict[Key, str]

    def __init__(self, scale_factor: float = 5., controls: Dict[str, Key] = None):
        self.scale_factor = scale_factor
        self.controls = controls
        self.key_event_map = {}

        if controls is None:
            log.warning("No controls found")
            return
        for event_name, key_char in controls.items():
            self.key_event_map[key_char] = event_name


