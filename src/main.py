import sys

import pygame

from src.scene import GameScene, EmptyScene

if __name__ == '__main__':

    clock = pygame.time.Clock()
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
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







