import pygame as pg
import random

# game options
pg.mixer.init()
TITLE = "ROBOT GAME"
WIDTH = 800
HEIGHT = 600
FPS = 30

# IMAGES
start_background0 = pg.image.load('images/start_background1.png')
start_background1 = pg.image.load('images/start_background2.png')
start_background2 = pg.image.load('images/start_background3.png')
start_background3 = pg.image.load('images/start_background4.png')
game_background = pg.image.load('images/deadfriends.png')
pleft = pg.image.load('images/player_left.png')
pright = pg.image.load('images/player_right.png')
pleftj = pg.image.load('images/player_jump_left.png')
prightj = pg.image.load('images/player_jump_right.png')
plefth = pg.image.load('images/player_hit_left.png')
prighth = pg.image.load('images/player_hit_right.png')
hamel_monster = pg.image.load('images/monster.png')
hamel_open = pg.image.load('images/hamel_monster_open.png')
end_background = pg.image.load('images/game_over.png')
level_background = pg.image.load('images/level_complete.png')
platform_320 = pg.image.load('images/plat_320.png')
platform_100 = pg.image.load('images/plat_100.png')
platform_150 = pg.image.load('images/plat_150.png')
lava = pg.image.load('images/lava.png')
lava_ball = pg.image.load('images/lava_ball.png')
gleft = pg.image.load('images/Goblin2.png')
gright = pg.image.load('images/Goblin.png')
sleft = pg.image.load('images/skel_left.png')
sright = pg.image.load('images/skel_right.png')
coin = pg.image.load('images/coin.png')
FONT_NAME = 'courier new'

# SOUNDS
game_over_sound = pg.mixer.Sound('sounds/game_over_sound.wav')
death_sound = pg.mixer.Sound('sounds/fuck.wav')
jump_sound = pg.mixer.Sound('sounds/jump_sound.wav')
death_sound_HIT = pg.mixer.Sound('sounds/death_sound.wav')
lava_burning_sound = pg.mixer.Sound('sounds/burning_sound.wav')
sword_swing = pg.mixer.Sound('sounds/sword_sound.wav')
scream_sound = pg.mixer.Sound('sounds/death_scream.wav')
coin_sound = pg.mixer.Sound('sounds/coin_pickup.wav')
hamel_sound = pg.mixer.Sound('sounds/hamel_intro.wav')

# MUSIC
songs = ['sounds/uzi_music.mp3', 'sounds/death_song.mp3', 'sounds/computer_startup.mp3', 'sounds/game_music.mp3']
current_song = None

# Mobs and Items Arrays
goblins_arr = []
coin_arr = []
skel_arr = []
player_arr = []
monster_arr = []
platform_arr = []


# Layers
platform_layer = 1
lava_layer = 1
player_layer = 1
mob_layer = 3
coin_layer = 2
projectile_layer = 2
monster_layer = 3


# drawing player lives
def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 25 * i
        img_rect.y = y
        surf.blit(img, img_rect)


# main menu background
backgrounds = [pg.image.load('images/start_background1.png'),
               pg.image.load('images/start_background2.png'),
               pg.image.load('images/start_background4.png'),
               pg.image.load('images/start_background3.png')]


# playing songs
def play_song(song_name):
    global current_song
    current_song = song_name
    queued_song = songs.index(song_name)
    pg.mixer.music.load(songs[queued_song])
    pg.mixer.music.play(-1)


# player property
PLAYER_ACC = 0.9
PLAYER_FRICTION = -0.13
PLAYER_GRAV = 0.8
PLAYER_JUMP = -15

# enemy property
BOSS_ACC = 0.5
BOSS_DECEL = -0.10
MOB_SPEED = random.randrange(2, 4)

# default platforms
platform_arr = [[0, HEIGHT - 80, WIDTH / 2 - 80, 20, 2],
                [WIDTH / 2 + 80, HEIGHT - 80, WIDTH / 2 - 80, 20, 2],
                [WIDTH / 2 - 50, (HEIGHT * 3 / 4) - 60, 100, 20, 2],
                [50, (HEIGHT * 5 / 8) - 60, 150, 20, 2],
                [WIDTH-200, (HEIGHT * 5 / 8) - 60, 150, 20, 2]]

def reset_plat_list():
    global platform_arr
    platform_arr = [[0, HEIGHT - 80, WIDTH / 2 - 80, 20, 2],
                     [WIDTH / 2 + 80, HEIGHT - 80, WIDTH / 2 - 80, 20, 2],
                     [WIDTH / 2 - 50, (HEIGHT * 3 / 4) - 60, 100, 20, 2],
                     [50, (HEIGHT * 5 / 8) - 60, 150, 20, 2],
                     [WIDTH - 200, (HEIGHT * 5 / 8) - 60, 150, 20, 2]]


# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
