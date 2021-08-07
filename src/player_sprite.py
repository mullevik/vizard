import pygame
from pygame.sprite import AbstractGroup

from src.constants import TILE_SIZE_PX
from src.settings import GameSettings


class Player(pygame.sprite.Sprite):

    def __init__(self, settings: GameSettings, *groups: AbstractGroup):
        super().__init__(*groups)

        self.settings = settings

        self.image = pygame.image.load(
            "../assets/graphics/characters/vizzard/idle.png")
        self.image = pygame.transform.scale(self.image, (int(self.image.get_size()[0] * settings.scale_factor),
                                                         int(self.image.get_size()[1] * settings.scale_factor)))

        center_of_first_type = ((TILE_SIZE_PX // 2) * settings.scale_factor, (TILE_SIZE_PX + 1) * settings.scale_factor)
        self.rect = self.image.get_rect(midbottom=center_of_first_type)

    def update(self, *args, **kwargs) -> None:
        print("Player update")
