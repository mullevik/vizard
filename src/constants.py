import pygame

VERSION = "Vizard_0.1"

TILE_SIZE_PX = 16
TICK_SPEED = 64
WIDTH_IN_TILES = 20
HEIGHT_IN_TILES = 12


# asset paths

IMG_VIZARD =            "../assets/graphics/characters/vizard/vizard.png"
ANIM_VIZARD_IDLE =      "../assets/graphics/characters/vizard/animation/idle/"
ANIM_VIZARD_DASH =      "../assets/graphics/characters/vizard/animation/dash/"
ANIM_VIZARD_ASCENT =    "../assets/graphics/characters/vizard/animation/ascent/"
ANIM_VIZARD_DESCENT =   "../assets/graphics/characters/vizard/animation/descent/"
ANIM_VIZARD_BLINK_IN =  "../assets/graphics/characters/vizard/animation/blink-in/"

IMG_SHARD =             "../assets/graphics/effects/shard/shard.png"
ANIM_SHARD_IDLE =       "../assets/graphics/effects/shard/animation/idle/"

ANIM_PARTICLE_BLINK_IN = "../assets/graphics/particles/animation/blink-in/"
ANIM_PARTICLE_BLINK_OUT = "../assets/graphics/particles/animation/blink-out/"
ANIM_PARTICLE_SHARD_COLLECTED = "../assets/graphics/particles/animation/shard-collected/"

IMG_TILE_DIRT =         "../assets/graphics/environment/tile_dirt.png"
IMG_TILE_GRASS_LIST = [
                        "../assets/graphics/environment/tile_grass_01.png",
                        "../assets/graphics/environment/tile_grass_02.png",
]
IMG_TILE_STONE_LIST = [
                        "../assets/graphics/environment/tile_stone_01.png",
                        "../assets/graphics/environment/tile_stone_02.png",
]


# fonts
PIXEL_FONT_SMALL = pygame.font.Font('../assets/fonts/joystix.monospace.ttf', 20)
