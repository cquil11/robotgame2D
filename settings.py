import pygame as pg
# game options
pg.mixer.init()
TITLE = "ROBOT GAME"
WIDTH = 800
HEIGHT = 600
FPS = 30
start_background1 = pg.image.load('start_background1.png')
start_background2 = pg.image.load('start_background2.png')
start_background3 = pg.image.load('start_background3.png')
start_background4 = pg.image.load('start_background4.png')
pleft = pg.image.load('player_left.png')
pright = pg.image.load('player_right.png')
hamel = pg.image.load('hamel_monster.png')
end_background = pg.image.load('game_over.png')
FONT_NAME = 'arial'
#go_music = pg.mixer.music.load('sounds/game_over_sound.mp3')

# player properties
PLAYER_ACC = 0.9
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.8
PLAYER_JUMP = -15

# default platforms
PLATFORM_LIST = [(0, HEIGHT - 20, WIDTH / 2 - 80, 20),
                 (WIDTH / 2 + 80, HEIGHT - 20, WIDTH / 2 - 50, 20),
                 (WIDTH / 2 - 50, HEIGHT * 3 / 4, 100, 20)]
# define colors and backgrounds
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)