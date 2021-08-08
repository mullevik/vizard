from enum import Enum
from typing import NamedTuple

import pygame
from pygame import Surface


class Position(NamedTuple):
    x: int
    y: int


class CardinalDirection(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3



def load_scaled_surface(path_to_asset: str, scale_factor: float,
                        has_alpha: bool = True) -> Surface:
    surface = pygame.image.load(path_to_asset)
    surface = surface.convert_alpha() if has_alpha else surface.convert()
    surface = pygame.transform.scale(surface, (int(surface.get_size()[0] * scale_factor),
                                              int(surface.get_size()[1] * scale_factor)))

    return surface