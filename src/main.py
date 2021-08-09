import sys

import pygame
import yaml

from src.constants import WIDTH_IN_TILES, TILE_SIZE_PX, HEIGHT_IN_TILES
from src.scene import GameScene, EmptyScene
from src.settings import GameSettings

if __name__ == '__main__':

    settings = GameSettings(
        **yaml.load(open("../config.yaml"), Loader=yaml.FullLoader))
    clock = pygame.time.Clock()
    pygame.init()
    screen = pygame.display.set_mode((int(WIDTH_IN_TILES * TILE_SIZE_PX * settings.scale_factor),
                                      int(HEIGHT_IN_TILES * TILE_SIZE_PX * settings.scale_factor)))
    pygame.display.set_caption("Vizzard")

    scene_classes = {
        EmptyScene.__name__: EmptyScene,
        GameScene.__name__: GameScene
    }

    active_scene = GameScene(screen, clock)

    # Application loop
    while True:

        followup_scene_name = active_scene.run()

        if followup_scene_name in scene_classes:
            active_scene = scene_classes[followup_scene_name](screen, clock)
        else:
            print("No followup scene - switching to EmptyScene")
            active_scene = EmptyScene(screen, clock)







