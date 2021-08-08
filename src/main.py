import sys

import pygame

from src.scene import DefaultScene, EmptyScene

if __name__ == '__main__':

    clock = pygame.time.Clock()
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Vizzard")

    scene_classes = {
        EmptyScene.__name__: EmptyScene,
        DefaultScene.__name__: DefaultScene
    }

    active_scene = DefaultScene(screen, clock)

    # Application loop
    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                print("Successful termination")
                sys.exit(0)

        followup_scene_name = active_scene.run()

        if followup_scene_name in scene_classes:
            active_scene = scene_classes[followup_scene_name](screen, clock)
        else:
            print("No followup scene - switching to EmptyScene")
            active_scene = EmptyScene(screen, clock)







