import os
from enum import Enum
from typing import NamedTuple, List

import pygame
from pygame import Surface


class Milliseconds(int):
    pass


class Position(NamedTuple):
    x: int
    y: int

    def __repr__(self):
        return f"(x={self.x}, y={self.y})"

    def __str__(self):
        return self.__repr__()


class Point(NamedTuple):
    x: float
    y: float

    def __repr__(self):
        return f"(x={self.x}, y={self.y})"

    def __str__(self):
        return self.__repr__()


class CardinalDirection(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


def load_scaled_surface(path_to_asset: str, scale_factor: float,
                        has_alpha: bool = True) -> Surface:
    surface = pygame.image.load(path_to_asset)
    surface = surface.convert_alpha() if has_alpha else surface.convert()
    surface = pygame.transform.scale(surface, (
        int(surface.get_size()[0] * scale_factor),
        int(surface.get_size()[1] * scale_factor)
    ))

    return surface


def load_scaled_surfaces(path_to_directory: str, scale_factor: float,
                         has_alpha: bool = True) -> List[Surface]:
    files = os.listdir(path_to_directory)
    return [load_scaled_surface(os.path.join(path_to_directory, file),
                                scale_factor, has_alpha=has_alpha)
            for file in sorted(files)]
