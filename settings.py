import pygame as pg
import random

# game options
# Try to initialize the mixer; if it fails (headless system or missing drivers)
# continue without sound so the rest of the game can still run.
try:
    pg.mixer.init()
    MIXER_OK = True
except Exception:
    MIXER_OK = False

TITLE = "ROBOT GAME"
WIDTH = 800
HEIGHT = 600
FPS = 30
FONT_NAME = 'arial'
hs_file = "highscore.txt"


# Utility loaders with safe fallbacks
def safe_load_image(pth, fallback_size=(64, 64)):
    try:
        # Don't call convert_alpha() here because that requires a display
        # mode to be set (which may not be initialized at import time).
        # Return the raw loaded surface; callers can convert it later if desired.
        return pg.image.load(pth)
    except Exception:
        # Return a simple semi-transparent magenta surface as a visible fallback
        surf = pg.Surface(fallback_size)
        surf.fill((100, 100, 100))
        return surf


class DummySound:
    def play(self, *a, **k):
        return None
    def stop(self, *a, **k):
        return None
    def unpause(self, *a, **k):
        return None


def safe_load_sound(pth):
    if not MIXER_OK:
        return DummySound()
    try:
        return pg.mixer.Sound(pth)
    except Exception:
        return DummySound()

# IMAGES
start_background0 = safe_load_image('images/start_background1.png')
start_background1 = safe_load_image('images/start_background2.png')
start_background2 = safe_load_image('images/start_background3.png')
start_background3 = safe_load_image('images/start_background4.png')
game_background = safe_load_image('images/deadfriends.png')
pleft = safe_load_image('images/player_left.png')
pright = safe_load_image('images/player_right.png')
pleftj = safe_load_image('images/player_jump_left.png')
prightj = safe_load_image('images/player_jump_right.png')
plefth = safe_load_image('images/player_hit_left.png')
prighth = safe_load_image('images/player_hit_right.png')
monster = safe_load_image('images/monster.png')
monster_open = safe_load_image('images/hamel_monster_open.png')
end_background = safe_load_image('images/game_over.png')
level_background = safe_load_image('images/level_complete.png')
platform_image = safe_load_image('images/platform.png')
lava = safe_load_image('images/lava.png')
lava_ball = safe_load_image('images/lava_ball.png')
gleft = safe_load_image('images/Goblin2.png')
gright = safe_load_image('images/Goblin.png')
sleft = safe_load_image('images/skel_left.png')
sright = safe_load_image('images/skel_right.png')
coin = safe_load_image('images/coin.png')
heart_image = safe_load_image('images/heart.png')
FONT_NAME = 'courier new'

# Optional new generated sprites (fall back to defaults if missing)
try:
    monster_medieval = pg.image.load('images/monster_medieval.png')
except Exception:
    monster_medieval = monster

try:
    monster_medieval_pixel = pg.image.load('images/monster_medieval_pixel.png')
except Exception:
    monster_medieval_pixel = monster

try:
    arrow_skeleton = pg.image.load('images/arrow_skeleton.png')
except Exception:
    # create a tiny surface fallback
    arrow_skeleton = pg.Surface((48, 12), pg.SRCALPHA)
    arrow_skeleton.fill((120, 80, 40))

try:
    arrow_skeleton_left = pg.image.load('images/arrow_skeleton_left.png')
except Exception:
    arrow_skeleton_left = pg.transform.flip(arrow_skeleton, True, False)

# Optional animation frames for arrows
arrow_skeleton_frames = []
for i in range(3):
    try:
        fimg = pg.image.load(f'images/arrow_skeleton_anim_{i}.png')
        arrow_skeleton_frames.append(fimg)
    except Exception:
        break

# Pixel arrow fallback
try:
    arrow_skeleton_pixel = pg.image.load('images/arrow_skeleton_pixel.png')
except Exception:
    arrow_skeleton_pixel = arrow_skeleton

# SOUNDS
game_over_sound = safe_load_sound('sounds/game_over_sound.wav')
death_sound = safe_load_sound('sounds/fuck.wav')
jump_sound = safe_load_sound('sounds/jump_sound.wav')
death_sound_HIT = safe_load_sound('sounds/death_sound.wav')
lava_burning_sound = safe_load_sound('sounds/burning_sound.wav')
sword_swing = safe_load_sound('sounds/sword_sound.wav')
scream_sound = safe_load_sound('sounds/death_scream.wav')
coin_sound = safe_load_sound('sounds/coin_pickup.wav')
explosion_sound = safe_load_sound('sounds/explosion.wav')
goblin_death_sound = safe_load_sound('sounds/goblin_death.wav')
skeleton_death_sound = safe_load_sound('sounds/skeleton_death.wav')

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
backgrounds = [safe_load_image('images/start_background1.png'),
               safe_load_image('images/start_background2.png'),
               safe_load_image('images/start_background4.png'),
               safe_load_image('images/start_background3.png')]


# playing songs
def play_song(song_name):
    global current_song
    current_song = song_name
    if not MIXER_OK:
        return
    try:
        queued_song = songs.index(song_name)
        pg.mixer.music.load(songs[queued_song])
        pg.mixer.music.play(-1)
    except Exception:
        # If music fails to play, ignore and continue
        return


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
platform_arr = [[0, HEIGHT - 80, WIDTH // 2 - 80, 20, 2],
                [WIDTH // 2 + 80, HEIGHT - 80, WIDTH // 2 - 80, 20, 2],
                [WIDTH // 2 - 50, (HEIGHT * 3) // 4 - 60, 100, 20, 2],
                [50, (HEIGHT * 5) // 8 - 60, 150, 20, 2],
                [WIDTH - 200, (HEIGHT * 5) // 8 - 60, 150, 20, 2],
                [WIDTH // 2 - 75, HEIGHT // 2, 150, 20, 2],
                [100, HEIGHT // 3, 120, 20, 2]]

def reset_plat_list():
    global platform_arr
    platform_arr = [[0, HEIGHT - 80, WIDTH // 2 - 80, 20, 2],
                     [WIDTH // 2 + 80, HEIGHT - 80, WIDTH // 2 - 80, 20, 2],
                     [WIDTH // 2 - 50, (HEIGHT * 3) // 4 - 60, 100, 20, 2],
                     [50, (HEIGHT * 5) // 8 - 60, 150, 20, 2],
                     [WIDTH - 200, (HEIGHT * 5) // 8 - 60, 150, 20, 2],
                     [WIDTH // 2 - 75, HEIGHT // 2, 150, 20, 2],
                     [100, HEIGHT // 3, 120, 20, 2]]

def get_level_platforms(level):
    global platform_arr
    platform_arr = []
    
    # Level-specific seeds for consistent but varied layouts
    random.seed(level * 1000 + level)
    
    # Boss levels (every 5th) get simpler, more open layouts for fireball room
    if level % 5 == 0:
        # Simple boss arena with wide open spaces
        # Bottom layer - 2 wide platforms with gap in middle
        platform_arr.append([0, HEIGHT - 80, WIDTH // 2 - 100, 20, 2])
        platform_arr.append([WIDTH // 2 + 100, HEIGHT - 80, WIDTH // 2 - 100, 20, 2])
        
        # Middle layer - 2-3 platforms with good spacing
        platform_arr.append([80, HEIGHT - 220, 150, 20, 2])
        platform_arr.append([WIDTH - 230, HEIGHT - 220, 150, 20, 2])
        
        # Upper-middle - single central platform for mobility
        platform_arr.append([WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 20, 2])
        
        # Upper layer - 2 side platforms
        platform_arr.append([60, HEIGHT // 3, 140, 20, 2])
        platform_arr.append([WIDTH - 200, HEIGHT // 3, 140, 20, 2])
        
    else:
        # Normal levels - more complex layouts
        num_platforms = random.randint(8, 11)
        
        # Bottom layer - 2-4 platforms spread across the floor
        bottom_count = random.randint(2, 4)
        for i in range(bottom_count):
            x = random.randrange(i * (WIDTH // bottom_count), (i + 1) * (WIDTH // bottom_count) - 100)
            w = random.randrange(60, 220)
            # Ensure it doesn't go off screen
            if x + w > WIDTH:
                w = WIDTH - x
            platform_arr.append([x, HEIGHT - 80, w, 20, 2])
        
        # Middle-lower layer - scattered platforms
        mid_low_count = random.randint(2, 3)
        for i in range(mid_low_count):
            x = random.randrange(20, WIDTH - 180)
            y = random.randrange(HEIGHT - 240, HEIGHT - 140)
            w = random.randrange(70, 180)
            if x + w > WIDTH:
                w = WIDTH - x - 10
            platform_arr.append([x, y, w, 20, 2])
        
        # Middle layer - more variation in placement
        mid_count = random.randint(2, 3)
        for i in range(mid_count):
            x = random.randrange(30, WIDTH - 160)
            y = random.randrange(HEIGHT // 2 - 50, HEIGHT // 2 + 80)
            w = random.randrange(60, 150)
            if x + w > WIDTH:
                w = WIDTH - x - 10
            platform_arr.append([x, y, w, 20, 2])
        
        # Upper layer - smaller, more challenging platforms
        remaining = num_platforms - len(platform_arr)
        for i in range(remaining):
            x = random.randrange(40, WIDTH - 140)
            y = random.randrange(HEIGHT // 3 - 40, HEIGHT // 3 + 80)
            w = random.randrange(50, 130)
            if x + w > WIDTH:
                w = WIDTH - x - 10
            platform_arr.append([x, y, w, 20, 2])
    
    # Reset random seed to not affect other random calls
    random.seed()
    
    return platform_arr


# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


def finalize_images():
    """
    Convert any loaded image Surfaces for fast blitting now that a
    display has been initialized. This should be called after
    `pg.display.set_mode(...)` is called (for example from `Game.__init__`).
    It will attempt to replace module-level Surface objects with
    their converted equivalents (.convert_alpha() when alpha present,
    otherwise .convert()). Non-Surface globals are left untouched.
    """
    for name, val in list(globals().items()):
        try:
            if isinstance(val, pg.Surface):
                # prefer convert_alpha when surface has per-pixel alpha
                if val.get_flags() & pg.SRCALPHA:
                    globals()[name] = val.convert_alpha()
                else:
                    globals()[name] = val.convert()
        except Exception:
            # If any conversion fails, leave the original value.
            continue
