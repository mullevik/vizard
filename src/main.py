import sys

import pygame

from src.player_sprite import Player

if __name__ == '__main__':

    clock = pygame.time.Clock()

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Vizzard")

    tile_surface = pygame.image.load(
        "../assets/graphics/environment/tile_ground.png").convert()
    tile_surface = pygame.transform.scale(tile_surface, (80, 80))

    player_group = pygame.sprite.GroupSingle(Player())

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
