import random
from dataclasses import dataclass
from typing import List, TYPE_CHECKING, Tuple, Dict, Any

from pygame import Surface

from src.constants import *
from src.settings import GameSettings
from src.utils import Position, load_scaled_surface

from src.renderer import AbstractRenderer


class EnvironmentException(Exception):
    pass


class CharacterEncodedMap(str):
    """String representing a character-encoded map layout"""
    pass


@dataclass
class Tile:
    walkable: bool
    dirt: bool
    grass: bool
    stone: bool

    def is_walkable(self) -> bool:
        return self.walkable

    def is_dirt(self) -> bool:
        return self.dirt

    def is_grass(self) -> bool:
        return self.grass

    def is_stone(self) -> bool:
        return self.stone


class Environment(object):
    tiles: List[List[Tile]]  # tile matrix indexed by (y, x)
    starting_position: Position

    def __init__(self, settings: GameSettings,
                 encoded_map: CharacterEncodedMap):
        self.settings = settings
        self.tiles = self._construct_tiles(encoded_map)
        self.starting_position = self._get_starting_position(encoded_map)

    def get_tile_matrix(self) -> List[List[Tile]]:
        return self.tiles

    def get_all_tiles(self) -> List[Tile]:
        tiles = []
        for row in self.tiles:
            tiles.extend(row)
        return tiles

    def get_tile_dimensions(self) -> Tuple[int, int]:
        """:return: (width, height) - in number of tiles"""
        height = len(self.tiles)
        width = len(self.tiles[0])
        return width, height

    def get_starting_position(self) -> Position:
        return self.starting_position

    def tile_at(self, position: Position):
        return self.tiles[position.y][position.x]

    def contains(self, position: Position):
        w, h = self.get_tile_dimensions()
        if 0 <= position.x < w and 0 <= position.y < h:
            return True
        return False

    def _construct_tiles(self,
                         encoded_map: CharacterEncodedMap) -> List[List[Tile]]:
        """
        :param encoded_map: constructs the tiles from a character encoded map
        :return: matrix of tiles
        """
        character_matrix = [[char for char in line]
                            for line in encoded_map.split("\n")]

        if len(character_matrix) < 1:
            raise EnvironmentException("Not a valid map encoding - bad size")

        height = len(character_matrix) + 1

        width = len(character_matrix[0])
        for row in character_matrix:
            if len(row) != width:
                raise EnvironmentException(
                    "Not a valid map encoding - all rows must have the same size")

        tile_matrix = [[None for _ in range(width)] for _ in range(height)]
        tile_matrix = self._construct_bottom_row(tile_matrix)
        for y in range(height - 1):
            for x in range(width):
                tile_matrix[y][x] = self._construct_tile(Position(x, y),
                                                         character_matrix)
        return tile_matrix

    def _construct_bottom_row(self, tile_matrix: List[List[Tile]]) -> List[
        List[Tile]]:
        width = len(tile_matrix[0])
        height = len(tile_matrix)

        for i in range(width):
            tile_matrix[height - 1][i] = Tile(False, True, False, False)

        return tile_matrix

    def _construct_tile(self, position: Position,
                        character_matrix: List[List[str]]) -> Tile:
        target_character = character_matrix[position.y][position.x]
        character_above = character_matrix[position.y - 1][
            position.x] if position.y > 0 else None

        walkable = True if target_character in (".", "/", "o", "S") else False
        dirt = True if character_above in (".", "/", "o", "S") else False
        grass = True if target_character == "/" else False
        stone = True if target_character == "o" else False

        return Tile(walkable, dirt, grass, stone)

    def _get_starting_position(self, encoded_map) -> Position:
        starting_positions = []

        for y, row in enumerate(encoded_map.split("\n")):
            for x, character in enumerate(row):
                if character == "S":
                    starting_positions.append(Position(x, y))

        if len(starting_positions) != 1:
            raise EnvironmentException(
                f"Wrong number of starting positions (expected 1, got {len(starting_positions)})")
        return starting_positions[0]


class EnvironmentRenderer(AbstractRenderer):
    # matrix of tile surfaces - one tile can have multiple overlapping surfaces
    surfaces: List[List[List[Surface]]]

    def __init__(self, environment: Environment, settings: GameSettings):
        self.environment = environment
        self.settings = settings

        self.surfaces = self._prepare_surfaces_for_tiles()

    def render(self, screen: Surface, *args, **kwargs):
        vertical_shift = args[0]

        w, h = self.environment.get_tile_dimensions()

        for y in range(h):
            for x in range(w):

                surfaces = self.surfaces[y][x]

                coordinates = (
                    int(x * TILE_SIZE_PX * self.settings.scale_factor),
                    int((
                                y - vertical_shift) * TILE_SIZE_PX * self.settings.scale_factor))

                for surface in surfaces:
                    screen.blit(surface, coordinates)

    def _prepare_surfaces_for_tiles(self) -> List[List[List[Surface]]]:
        tile_matrix = self.environment.get_tile_matrix()
        surfaces = [[None for _ in row]
                    for row in tile_matrix]

        for y in range(len(tile_matrix)):
            for x in range(len(tile_matrix[y])):
                surfaces[y][x] = \
                    self._prepare_surfaces_for_tile(Position(x, y),
                                                    tile_matrix)

        return surfaces

    def _prepare_surfaces_for_tile(self, position: Position,
                                   tile_matrix: List[List[Tile]]) -> List[
        Surface]:
        surfaces = []
        tile = tile_matrix[position.y][position.x]
        dirt_map = self._construct_dirt_map(tile_matrix)
        scale_factor = self.settings.scale_factor

        if tile.is_dirt():
            surfaces.append(self._prepare_dirt_surface(position, dirt_map))
        if tile.is_grass():
            surfaces.append(
                load_scaled_surface(random.choice(IMG_TILE_GRASS_LIST),
                                    scale_factor))
        if tile.is_stone():
            surfaces.append(
                load_scaled_surface(random.choice(IMG_TILE_STONE_LIST),
                                    scale_factor))
        return surfaces

    def _prepare_dirt_surface(self, position: Position,
                              dirt_map: List[List[bool]]) -> Surface:
        scale_factor = self.settings.scale_factor

        # mask explanation:
        # 0 - must not be dirt,
        # 1 - must be dirt,
        # 2 - doesnt matter
        tile_options = [
            {
                "mask": [
                    [2, 2, 2],
                    [1, 1, 1],
                    [0, 0, 0],
                ],
                "image": load_scaled_surface(IMG_TILE_DIRT_SIDES, scale_factor)
            },
            {
                "mask": [
                    [2, 2, 2],
                    [1, 1, 1],
                    [1, 0, 1],
                ],
                "image": load_scaled_surface(IMG_TILE_DIRT_SIDES_TOP, scale_factor)
            },
            {
                "mask": [
                    [2, 2, 2],
                    [1, 1, 0],
                    [1, 0, 2],
                ],
                "image": load_scaled_surface(IMG_TILE_DIRT_LEFT_TOP,
                                             scale_factor)
            },
            {
                "mask": [
                    [2, 2, 2],
                    [0, 1, 1],
                    [2, 0, 1],
                ],
                "image": pygame.transform.flip(load_scaled_surface(IMG_TILE_DIRT_LEFT_TOP,
                                             scale_factor), True, False)
            },
            {
                "mask": [
                    [2, 2, 2],
                    [1, 1, 1],
                    [1, 0, 0],
                ],
                "image": load_scaled_surface(IMG_TILE_DIRT_LEFT_SIDE,
                                             scale_factor)
            },
            {
                "mask": [
                    [2, 2, 2],
                    [1, 1, 1],
                    [0, 0, 1],
                ],
                "image": pygame.transform.flip(
                    load_scaled_surface(IMG_TILE_DIRT_LEFT_SIDE,
                                        scale_factor), True, False)
            },
            {
                "mask": [
                    [2, 2, 2],
                    [1, 1, 0],
                    [0, 0, 0],
                ],
                "image": load_scaled_surface(IMG_TILE_DIRT_LEFT_SOLO,
                                             scale_factor)
            },
            {
                "mask": [
                    [2, 2, 2],
                    [0, 1, 1],
                    [0, 0, 0],
                ],
                "image": pygame.transform.flip(
                    load_scaled_surface(IMG_TILE_DIRT_LEFT_SOLO,
                                        scale_factor), True, False)
            },
            {
                "mask": [
                    [2, 2, 2],
                    [2, 2, 2],
                    [2, 2, 2],
                ],
                "image": load_scaled_surface(IMG_TILE_DIRT, scale_factor,
                                             has_alpha=False)
            }
        ]

        for tile_option in tile_options:
            if self._does_tile_fit(position, tile_option["mask"], dirt_map):
                return tile_option["image"]
        raise EnvironmentException("Smooth tiling ended unexpectedly")

    @staticmethod
    def _does_tile_fit(position: Position,
                       tile_mask: List[List[int]],
                       dirt_map: List[List[bool]]) -> bool:
        """
        :returns True if the tile option fits into the dirt_map, False otherwise.
        """
        x_lb = position.x
        x_ub = position.x + 3
        y_lb = position.y
        y_ub = position.y + 3

        for y, dirt_y in zip((0, 1, 2), range(y_lb, y_ub)):
            for x, dirt_x in zip((0, 1, 2), range(x_lb, x_ub)):
                is_dirt = dirt_map[dirt_y][dirt_x]
                mask_number = tile_mask[y][x]
                if mask_number == 0 and is_dirt:
                    return False
                if mask_number == 1 and not is_dirt:
                    return False

        return True

    def _construct_dirt_map(self, tile_matrix: List[List[Tile]]
                            ) -> List[List[bool]]:
        """
        :returns a matrix of size h + 2 x w + 2 that contains booleans -
        True position means there is a dirt
        False position means there is not dirt
        """
        w, h = self.environment.get_tile_dimensions()

        dirt_map = [[False for _ in range(len(tile_matrix[0]) + 2)]
                    for _ in range(len(tile_matrix) + 2)]

        # for x in range(w):
        #     dirt_map[h + 1][x] = True

        for y in range(h):
            for x in range(w):
                if tile_matrix[y][x].is_dirt():
                    dirt_map[y + 1][x + 1] = True

        return dirt_map
