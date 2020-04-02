import pygame as pg
# game options
pg.mixer.init()
TITLE = "ROBOT GAME"
WIDTH = 800
HEIGHT = 600
FPS = 30
start_background1 = pg.image.load('images/start_background1.png')
start_background2 = pg.image.load('images/start_background2.png')
start_background3 = pg.image.load('images/start_background3.png')
start_background4 = pg.image.load('images/start_background4.png')
game_background = pg.image.load('images/deadfriends.png')
pleft = pg.image.load('images/player_left.png')
pright = pg.image.load('images/player_right.png')
hamel = pg.image.load('images/hamel_monster.png')
hamel_open = pg.image.load('images/hamel_monster_open.png')
end_background = pg.image.load('images/game_over.png')
platform_skin = pg.image.load('images/platform.png')
gleft = pg.image.load('images/Goblin2.png')
gright = pg.image.load('images/Goblin.png')
FONT_NAME = 'arial'
game_over_sound = pg.mixer.Sound('sounds/game_over_sound.wav')
game_music = pg.mixer.music.load('sounds/uzi_music.mp3')

# player property
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