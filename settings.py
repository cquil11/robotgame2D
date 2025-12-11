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

TITLE = "CRIMSON KNIGHT"
WIDTH = 800  # Screen width
HEIGHT = 600  # Screen height
LEVEL_WIDTH = 2400  # Total level width (3x screen width for scrolling)
UI_PANEL_HEIGHT = 80
WINDOW_HEIGHT = HEIGHT + UI_PANEL_HEIGHT  # 680 total for windowed display
FPS = 30
FONT_NAME = 'courier new'
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
pleft = safe_load_image('images/player/player_left.png')
pright = safe_load_image('images/player/player_right.png')
pleftj = safe_load_image('images/player/player_jump_left.png')
prightj = safe_load_image('images/player/player_jump_right.png')
plefth = safe_load_image('images/player/player_hit_left.png')
prighth = safe_load_image('images/player/player_hit_right.png')

# Attack animation frames
attack_normal_right = [safe_load_image(f'images/player/player_attack_normal_right_{i}.png') for i in range(3)]
attack_normal_left = [safe_load_image(f'images/player/player_attack_normal_left_{i}.png') for i in range(3)]
attack_critical_right = [safe_load_image(f'images/player/player_attack_critical_right_{i}.png') for i in range(3)]
attack_critical_left = [safe_load_image(f'images/player/player_attack_critical_left_{i}.png') for i in range(3)]
attack_heavy_right = [safe_load_image(f'images/player/player_attack_heavy_right_{i}.png') for i in range(4)]
attack_heavy_left = [safe_load_image(f'images/player/player_attack_heavy_left_{i}.png') for i in range(4)]

# IMAGES - end of game UI and sprites
end_background = safe_load_image('images/backgrounds/game_over.png')
level_background = safe_load_image('images/backgrounds/level_complete.png')
platform_image = safe_load_image('images/ui/platform.png')
lava = safe_load_image('images/ui/lava.png')
lava_ball = safe_load_image('images/ui/lava_ball.png')
gleft = safe_load_image('images/enemies/Goblin2.png')
gright = safe_load_image('images/enemies/Goblin.png')
sleft = safe_load_image('images/enemies/skel_left.png')
sright = safe_load_image('images/enemies/skel_right.png')
coin = safe_load_image('images/ui/coin.png')
heart_image = safe_load_image('images/ui/heart.png')

# Optional new generated sprites (fall back to defaults if missing)
try:
    monster_scary = pg.image.load('images/monsters/monster_scary.png')
except Exception:
    # Fallback: create a simple red circle
    monster_scary = pg.Surface((128, 128), pg.SRCALPHA)
    pg.draw.circle(monster_scary, (200, 50, 50), (64, 64), 50)

try:
    arrow_skeleton = pg.image.load('images/enemies/arrow_skeleton.png')
except Exception:
    # create a tiny surface fallback
    arrow_skeleton = pg.Surface((48, 12), pg.SRCALPHA)
    arrow_skeleton.fill((120, 80, 40))

# Optional animation frames for arrows (not currently generated)
arrow_skeleton_frames = []

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
particle_layer = 4
powerup_layer = 5


# drawing player lives
def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 25 * i
        img_rect.y = y
        surf.blit(img, img_rect)


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

# track where the current platform layout came from (for debug overlay)
platform_source = "default"

def reset_plat_list():
    global platform_arr
    global platform_source
    platform_arr = [[0, HEIGHT - 80, WIDTH // 2 - 80, 20, 2],
                     [WIDTH // 2 + 80, HEIGHT - 80, WIDTH // 2 - 80, 20, 2],
                     [WIDTH // 2 - 50, (HEIGHT * 3) // 4 - 60, 100, 20, 2],
                     [50, (HEIGHT * 5) // 8 - 60, 150, 20, 2],
                     [WIDTH - 200, (HEIGHT * 5) // 8 - 60, 150, 20, 2],
                     [WIDTH // 2 - 75, HEIGHT // 2, 150, 20, 2],
                     [100, HEIGHT // 3, 120, 20, 2]]
    platform_source = "reset_plat_list"

def get_level_platforms(level):
    global platform_arr
    global platform_source
    platform_arr = []
    
    # Level-specific seeds for consistent but varied layouts
    random.seed(level * 1000 + level)
    
    # Level 1: Special winding side-scrolling layout
    if level == 1:
        # Create a winding path from left to right across LEVEL_WIDTH (2400px)
        # Ground floor platforms
        platform_arr.append([0, HEIGHT - 90, 300, 20, 2])
        platform_arr.append([350, HEIGHT - 90, 250, 20, 2])
        platform_arr.append([650, HEIGHT - 90, 200, 20, 2])
        # Mid-level platforms (staggered heights)
        platform_arr.append([200, HEIGHT - 180, 180, 20, 2])
        platform_arr.append([450, HEIGHT - 240, 200, 20, 2])
        platform_arr.append([750, HEIGHT - 200, 180, 20, 2])
        # Upper platforms
        platform_arr.append([100, HEIGHT - 320, 150, 20, 2])
        platform_arr.append([350, HEIGHT - 380, 180, 20, 2])
        platform_arr.append([600, HEIGHT - 340, 200, 20, 2])
        # Continue to right side
        platform_arr.append([900, HEIGHT - 90, 250, 20, 2])
        platform_arr.append([1200, HEIGHT - 160, 200, 20, 2])
        platform_arr.append([1050, HEIGHT - 280, 180, 20, 2])
        platform_arr.append([1300, HEIGHT - 380, 200, 20, 2])
        # Final section
        platform_arr.append([1550, HEIGHT - 90, 250, 20, 2])
        platform_arr.append([1850, HEIGHT - 180, 200, 20, 2])
        platform_arr.append([1700, HEIGHT - 300, 180, 20, 2])
        platform_arr.append([2000, HEIGHT - 240, 250, 20, 2])
        platform_arr.append([2150, HEIGHT - 90, 250, 20, 3])  # End platform
        platform_source = "level1_scrolling"
        return
    
    # Choose a layout pattern based on level
    # Boss levels (every 5th) get simpler, more open layouts for fireball room
    if level % 5 == 0:
        # Simple boss arena with wide open spaces
        platform_arr.append([0, HEIGHT - 80, WIDTH // 2 - 100, 20, 2])
        platform_arr.append([WIDTH // 2 + 100, HEIGHT - 80, WIDTH // 2 - 100, 20, 2])
        platform_arr.append([80, HEIGHT - 220, 150, 20, 2])
        platform_arr.append([WIDTH - 230, HEIGHT - 220, 150, 20, 2])
        platform_arr.append([WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 20, 2])
        platform_arr.append([60, HEIGHT // 3, 140, 20, 2])
        platform_arr.append([WIDTH - 200, HEIGHT // 3, 140, 20, 2])
        platform_source = "boss_pattern"
        return
        
    # For non-boss levels, use pattern rotating through 10 designs
    # All patterns now use LEVEL_WIDTH (2400px) for scrolling gameplay
    pattern = (level - 1) % 10
    
    if pattern == 0:
        # STAIRCASE ASCENT - climbing platforms left to right
        platform_arr.append([0, HEIGHT - 90, 280, 20, 2])
        platform_arr.append([350, HEIGHT - 160, 250, 20, 2])
        platform_arr.append([700, HEIGHT - 230, 220, 20, 2])
        platform_arr.append([100, HEIGHT - 320, 200, 20, 2])
        platform_arr.append([450, HEIGHT - 400, 200, 20, 2])
        platform_arr.append([850, HEIGHT - 480, 200, 20, 2])
        # Continue to right side
        platform_arr.append([1100, HEIGHT - 90, 280, 20, 2])
        platform_arr.append([1450, HEIGHT - 160, 250, 20, 2])
        platform_arr.append([1800, HEIGHT - 230, 220, 20, 2])
        platform_arr.append([1200, HEIGHT - 320, 200, 20, 2])
        platform_arr.append([1550, HEIGHT - 400, 200, 20, 2])
        platform_arr.append([1950, HEIGHT - 480, 200, 20, 2])
        platform_arr.append([2100, HEIGHT - 90, 300, 20, 3])
        platform_source = "pattern_0_scroll"
        
    elif pattern == 1:
        # WAVE PATTERN - undulating platforms
        platform_arr.append([0, HEIGHT - 100, 250, 20, 2])
        platform_arr.append([300, HEIGHT - 250, 220, 20, 2])
        platform_arr.append([600, HEIGHT - 350, 200, 20, 2])
        platform_arr.append([950, HEIGHT - 280, 200, 20, 2])
        platform_arr.append([1300, HEIGHT - 150, 220, 20, 2])
        platform_arr.append([1600, HEIGHT - 320, 200, 20, 2])
        platform_arr.append([1950, HEIGHT - 200, 220, 20, 2])
        platform_arr.append([2100, HEIGHT - 90, 300, 20, 3])
        platform_source = "pattern_1_scroll"
        
    elif pattern == 2:
        # VERTICAL TOWERS - tall column challenges
        platform_arr.append([50, HEIGHT - 90, 180, 20, 2])
        platform_arr.append([50, HEIGHT - 200, 180, 20, 2])
        platform_arr.append([50, HEIGHT - 310, 180, 20, 2])
        platform_arr.append([400, HEIGHT - 120, 180, 20, 2])
        platform_arr.append([400, HEIGHT - 250, 180, 20, 2])
        platform_arr.append([400, HEIGHT - 380, 180, 20, 2])
        platform_arr.append([850, HEIGHT - 90, 180, 20, 2])
        platform_arr.append([850, HEIGHT - 200, 180, 20, 2])
        platform_arr.append([1300, HEIGHT - 120, 180, 20, 2])
        platform_arr.append([1300, HEIGHT - 280, 180, 20, 2])
        platform_arr.append([1750, HEIGHT - 90, 180, 20, 2])
        platform_arr.append([1750, HEIGHT - 210, 180, 20, 2])
        platform_arr.append([2100, HEIGHT - 90, 300, 20, 3])
        platform_source = "pattern_2_scroll"
        
    elif pattern == 3:
        # NARROW PASSAGE - tight, challenging platforming
        platform_arr.append([0, HEIGHT - 90, 220, 20, 2])
        platform_arr.append([320, HEIGHT - 180, 180, 20, 2])
        platform_arr.append([600, HEIGHT - 120, 200, 20, 2])
        platform_arr.append([900, HEIGHT - 280, 160, 20, 2])
        platform_arr.append([1150, HEIGHT - 150, 180, 20, 2])
        platform_arr.append([1450, HEIGHT - 300, 170, 20, 2])
        platform_arr.append([1750, HEIGHT - 140, 180, 20, 2])
        platform_arr.append([2000, HEIGHT - 230, 200, 20, 2])
        platform_arr.append([2100, HEIGHT - 90, 300, 20, 3])
        platform_source = "pattern_3_scroll"
        
    elif pattern == 4:
        # WIDE OPEN - fewer, larger platforms
        platform_arr.append([0, HEIGHT - 100, 380, 20, 2])
        platform_arr.append([500, HEIGHT - 200, 350, 20, 2])
        platform_arr.append([1000, HEIGHT - 150, 360, 20, 2])
        platform_arr.append([1450, HEIGHT - 280, 340, 20, 2])
        platform_arr.append([1900, HEIGHT - 100, 380, 20, 3])
        platform_source = "pattern_4_scroll"
        
    elif pattern == 5:
        # ZIGZAG JUMP - alternating heights and sides
        platform_arr.append([0, HEIGHT - 90, 240, 20, 2])
        platform_arr.append([350, HEIGHT - 200, 200, 20, 2])
        platform_arr.append([650, HEIGHT - 100, 220, 20, 2])
        platform_arr.append([950, HEIGHT - 260, 200, 20, 2])
        platform_arr.append([1250, HEIGHT - 120, 220, 20, 2])
        platform_arr.append([1550, HEIGHT - 280, 200, 20, 2])
        platform_arr.append([1850, HEIGHT - 140, 230, 20, 2])
        platform_arr.append([2100, HEIGHT - 90, 300, 20, 3])
        platform_source = "pattern_5_scroll"
        
    elif pattern == 6:
        # FLOATING ISLANDS - scattered platforms with gaps
        platform_arr.append([50, HEIGHT - 100, 150, 20, 2])
        platform_arr.append([300, HEIGHT - 200, 130, 20, 2])
        platform_arr.append([600, HEIGHT - 140, 140, 20, 2])
        platform_arr.append([900, HEIGHT - 280, 120, 20, 2])
        platform_arr.append([1200, HEIGHT - 160, 140, 20, 2])
        platform_arr.append([1500, HEIGHT - 300, 130, 20, 2])
        platform_arr.append([1850, HEIGHT - 100, 140, 20, 2])
        platform_arr.append([2100, HEIGHT - 90, 300, 20, 3])
        platform_source = "pattern_6_scroll"
        
    elif pattern == 7:
        # SPIRAL CLIMB - platforms spiral upward
        platform_arr.append([0, HEIGHT - 90, 250, 20, 2])
        platform_arr.append([350, HEIGHT - 180, 220, 20, 2])
        platform_arr.append([700, HEIGHT - 280, 200, 20, 2])
        platform_arr.append([1050, HEIGHT - 380, 180, 20, 2])
        platform_arr.append([1400, HEIGHT - 320, 200, 20, 2])
        platform_arr.append([1750, HEIGHT - 200, 220, 20, 2])
        platform_arr.append([2100, HEIGHT - 90, 300, 20, 3])
        platform_source = "pattern_7_scroll"
        
    elif pattern == 8:
        # GAUNTLET - continuous challenging platforms
        platform_arr.append([0, HEIGHT - 90, 180, 20, 2])
        platform_arr.append([250, HEIGHT - 180, 170, 20, 2])
        platform_arr.append([500, HEIGHT - 100, 180, 20, 2])
        platform_arr.append([750, HEIGHT - 240, 160, 20, 2])
        platform_arr.append([1000, HEIGHT - 130, 180, 20, 2])
        platform_arr.append([1250, HEIGHT - 280, 170, 20, 2])
        platform_arr.append([1500, HEIGHT - 120, 180, 20, 2])
        platform_arr.append([1750, HEIGHT - 260, 170, 20, 2])
        platform_arr.append([2000, HEIGHT - 100, 200, 20, 2])
        platform_arr.append([2100, HEIGHT - 90, 300, 20, 3])
        platform_source = "pattern_8_scroll"
        
    else:  # pattern == 9
        # MAZE - complex winding path
        platform_arr.append([0, HEIGHT - 90, 200, 20, 2])
        platform_arr.append([300, HEIGHT - 180, 180, 20, 2])
        platform_arr.append([150, HEIGHT - 270, 170, 20, 2])
        platform_arr.append([450, HEIGHT - 200, 200, 20, 2])
        platform_arr.append([750, HEIGHT - 150, 200, 20, 2])
        platform_arr.append([600, HEIGHT - 280, 180, 20, 2])
        platform_arr.append([1050, HEIGHT - 100, 200, 20, 2])
        platform_arr.append([1350, HEIGHT - 220, 190, 20, 2])
        platform_arr.append([1200, HEIGHT - 340, 170, 20, 2])
        platform_arr.append([1600, HEIGHT - 150, 200, 20, 2])
        platform_arr.append([1950, HEIGHT - 240, 190, 20, 2])
        platform_arr.append([2100, HEIGHT - 90, 300, 20, 3])
        platform_source = "pattern_9_scroll"
    
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
