import pygame as pg
# game options
pg.mixer.init()
TITLE = "ROBOT GAME"
WIDTH = 800
HEIGHT = 600
FPS = 30
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
hamel_monster = pg.image.load('images/hamel_monster.png')
hamel_open = pg.image.load('images/hamel_monster_open.png')
castle_background = pg.image.load('images/castle_background_800x600.png')
end_background = pg.image.load('images/game_over.png')
level_background = pg.image.load('images/level_complete.png')
platform_320 = pg.image.load('images/plat_320.png')
platform_100 = pg.image.load('images/plat_100.png')
platform_150 = pg.image.load('images/plat_150.png')
lava = pg.image.load('images/lava.png')
lava_ball = pg.image.load('images/lava_ball.png')
gleft = pg.image.load('images/Goblin2.png')
gright = pg.image.load('images/Goblin.png')
coin = pg.image.load('images/coin.png')
FONT_NAME = 'courier new'

game_over_sound = pg.mixer.Sound('sounds/game_over_sound.wav')
death_sound = pg.mixer.Sound('sounds/fuck.wav')
jump_sound = pg.mixer.Sound('sounds/jump_sound2.wav')
death_sound_HIT = pg.mixer.Sound('sounds/death_sound.wav')
lava_burning_sound = pg.mixer.Sound('sounds/burning_sound.wav')
sword_swing = pg.mixer.Sound('sounds/sword_sound.wav')
scream_sound = pg.mixer.Sound('sounds/death_scream.wav')
coin_sound = pg.mixer.Sound('sounds/coin_pickup.wav')


songs = ['sounds/uzi_music.mp3', 'sounds/death_song.mp3', 'sounds/computer_startup.mp3', 'sounds/game_music.mp3']
current_song = None
goblins_arr = []
coin_arr = []



"""def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 25 * i
        img_rect.y = y
        surf.blit(img, img_rect)"""


backgrounds = [pg.image.load('images/start_background1.png'),
               pg.image.load('images/start_background2.png'),
               pg.image.load('images/start_background4.png'),
               pg.image.load('images/start_background3.png')]


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


# default platforms
PLATFORM_LIST = [(0, HEIGHT - 80, WIDTH / 2 - 80, 20),
                 (WIDTH / 2 + 80, HEIGHT - 80, WIDTH / 2 - 80, 20),
                 (WIDTH / 2 - 50, (HEIGHT * 3 / 4) - 60, 100, 20),
                 (50, (HEIGHT * 5 / 8) - 60, 150, 20),
                 (WIDTH-200, (HEIGHT * 5 / 8) - 60, 150, 20)]

# define colors and backgrounds
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)