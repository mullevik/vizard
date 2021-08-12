import logging

import pygame
import yaml

from src.constants import *
from src.scene import GameScene, EmptyScene
from src.settings import GameSettings
from src.utils import load_scaled_surface

if __name__ == '__main__':

    logging.basicConfig(format='[%(asctime)s] %(levelname).1s - %(message)s',
                        level=logging.DEBUG)
    log = logging.getLogger(__name__)

    settings = GameSettings(
        **yaml.load(open("../config.yaml"), Loader=yaml.FullLoader))
    clock = pygame.time.Clock()
    pygame.init()
    screen = pygame.display.set_mode((int(WIDTH_IN_TILES * TILE_SIZE_PX * settings.scale_factor),
                                      int(HEIGHT_IN_TILES * TILE_SIZE_PX * settings.scale_factor)))
    pygame.display.set_caption("Vizard")
    pygame.display.set_icon(load_scaled_surface(IMG_VIZARD, 1.))

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
            log.debug("No followup scene - switching to EmptyScene")
            active_scene = EmptyScene(screen, clock)







