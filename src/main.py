import sys

import pygame
import yaml

from src.constants import TILE_SIZE_PX
from src.environment import Environment, EnvironmentRenderer
from src.player import Player, PlayerSprite, HorizontalMoveAction
from src.settings import GameSettings

if __name__ == '__main__':

    settings = GameSettings(
        **yaml.load(open("../config.yaml"), Loader=yaml.FullLoader))

    clock = pygame.time.Clock()

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Vizzard")

    environment = Environment(settings,
                              open("../assets/maps/default.txt", "r").read())
    environment_renderer = EnvironmentRenderer(environment, settings)

    player = Player()
    player.set_position(environment.get_starting_position())
    player_sprite = PlayerSprite(player, settings)
    player_group = pygame.sprite.GroupSingle(player_sprite)

    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                print("Successful termination")
                sys.exit(0)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                player.apply_action(HorizontalMoveAction(environment, -1))
                print("MOVE LEFT")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                player.apply_action(HorizontalMoveAction(environment, 1))
                print("MOVE UP")

        screen.fill("dimgray")

        environment_renderer.render(screen)
        player_group.draw(screen)
        player_group.update()

        pygame.display.update()
        clock.tick(60)
