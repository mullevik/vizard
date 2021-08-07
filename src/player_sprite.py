import pygame
from pygame.sprite import AbstractGroup


class Player(pygame.sprite.Sprite):

    def __init__(self, *groups: AbstractGroup):
        super().__init__(*groups)

        self.image = pygame.image.load(
            "../assets/graphics/characters/vizzard/idle.png")
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect(midbottom=(40, 80))

    def update(self, *args, **kwargs) -> None:
        print("Player update")
