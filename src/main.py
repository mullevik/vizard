import sys

import pygame
import yaml

from src.constants import TILE_SIZE_PX
from src.player_sprite import Player
from src.settings import GameSettings

if __name__ == '__main__':

    settings = GameSettings(**yaml.load(open("../config.yaml")))

    clock = pygame.time.Clock()

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Vizzard")

    tile_surface = pygame.image.load(
        "../assets/graphics/environment/tile_ground.png").convert()
    tile_surface = pygame.transform.scale(tile_surface, (int(tile_surface.get_size()[0] * settings.scale_factor),
                                                         int(tile_surface.get_size()[1] * settings.scale_factor)))

    player_group = pygame.sprite.GroupSingle(Player(settings))

    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                print("Successful termination")
                sys.exit(0)

        screen.fill("dimgray")

        screen.blit(tile_surface, (0, 0))

        player_group.draw(screen)
        player_group.update()

        pygame.display.update()
        clock.tick(60)
