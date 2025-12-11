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
# Knight sprite sheet support
def load_knight_sprite_sheet(pth):
    """Load and slice a knight sprite sheet if available.

    Auto-detect frame size by assuming 4 rows (idle, walk, jump, attack)
    and using per-row frame counts [4, 6, 2, 4]. Width is divided by
    the max count to get frame width. This avoids hard-coding 40x50.
    """
    try:
        sheet = pg.image.load(pth)
        # Basic debug to help verify usage
        print(f"Knight sheet loaded: {pth} ({sheet.get_width()}x{sheet.get_height()})")
    except Exception as e:
        print(f"Knight sheet not loaded: {pth} -> {e}")
        return None
    try:
        sw, sh = sheet.get_width(), sheet.get_height()
        row_counts = [4, 6, 2, 4]
        rows = 4
        fh = sh // rows
        fw = sw // max(row_counts)
        def grab(row, count):
            frames = []
            for i in range(count):
                x = i * fw
                y = row * fh
                rect = pg.Rect(x, y, fw, fh)
                surf = pg.Surface((fw, fh), pg.SRCALPHA)
                surf.blit(sheet, (0,0), rect)
                frames.append(surf)
            return frames
        frames = {
            'idle_right': grab(0, row_counts[0]),
            'walk_right': grab(1, row_counts[1]),
            'jump_right': grab(2, row_counts[2]),
            'attack_right': grab(3, row_counts[3]),
        }
        # Mirror for left
        def mirror(arr):
            return [pg.transform.flip(s, True, False) for s in arr]
        frames['idle_left'] = mirror(frames['idle_right'])
        frames['walk_left'] = mirror(frames['walk_right'])
        frames['jump_left'] = mirror(frames['jump_right'])
        frames['attack_left'] = mirror(frames['attack_right'])
        print(f"Knight frames sliced: idle={len(frames['idle_right'])}, walk={len(frames['walk_right'])}, jump={len(frames['jump_right'])}, attack={len(frames['attack_right'])}")
        return frames
    except Exception as e:
        print(f"Knight sheet slicing failed: {e}")
        return None



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
_knight_frames = load_knight_sprite_sheet('images/sprites/player/knight_sprite_sheet.png')
pleft = safe_load_image('images/sprites/player/player_left.png') if not _knight_frames else _knight_frames['idle_left'][0]
pright = safe_load_image('images/sprites/player/player_right.png') if not _knight_frames else _knight_frames['idle_right'][0]
pleftj = safe_load_image('images/sprites/player/player_jump_left.png') if not _knight_frames else _knight_frames['jump_left'][0]
prightj = safe_load_image('images/sprites/player/player_jump_right.png') if not _knight_frames else _knight_frames['jump_right'][0]
plefth = safe_load_image('images/sprites/player/player_hit_left.png')
prighth = safe_load_image('images/sprites/player/player_hit_right.png')

# Attack animation frames
attack_normal_right = [safe_load_image(f'images/sprites/player/player_attack_normal_right_{i}.png') for i in range(3)]
attack_normal_left = [safe_load_image(f'images/sprites/player/player_attack_normal_left_{i}.png') for i in range(3)]
attack_critical_right = [safe_load_image(f'images/sprites/player/player_attack_critical_right_{i}.png') for i in range(3)]
attack_critical_left = [safe_load_image(f'images/sprites/player/player_attack_critical_left_{i}.png') for i in range(3)]
attack_heavy_right = [safe_load_image(f'images/sprites/player/player_attack_heavy_right_{i}.png') for i in range(4)]
attack_heavy_left = [safe_load_image(f'images/sprites/player/player_attack_heavy_left_{i}.png') for i in range(4)]

# IMAGES - end of game UI and sprites
end_background = safe_load_image('images/backgrounds/game_over.png')
level_background = safe_load_image('images/backgrounds/level_complete.png')
platform_image = safe_load_image('images/ui/platform.png')
lava = safe_load_image('images/ui/lava.png')
lava_ball = safe_load_image('images/ui/lava_ball.png')
gleft = safe_load_image('images/sprites/enemies/Goblin2.png')
gright = safe_load_image('images/sprites/enemies/Goblin.png')
sleft = safe_load_image('images/sprites/enemies/skel_left.png')
sright = safe_load_image('images/sprites/enemies/skel_right.png')
coin = safe_load_image('images/ui/coin.png')
heart_image = safe_load_image('images/ui/heart.png')

# Optional new generated sprites (fall back to defaults if missing)
try:
    monster_scary = pg.image.load('images/sprites/monsters/monster_scary.png')
except Exception:
    # Fallback: create a simple red circle
    monster_scary = pg.Surface((128, 128), pg.SRCALPHA)
    pg.draw.circle(monster_scary, (200, 50, 50), (64, 64), 50)

try:
    arrow_skeleton = pg.image.load('images/sprites/enemies/arrow_skeleton.png')
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
    
    # Level 1-2: Beginner-friendly layouts (cover lava completely, safe)
    if level == 1:
        # Extra wide ground platforms to cover lava completely
        platform_arr.append([0, HEIGHT - 90, WIDTH, 20, 2])          # full-width ground covering lava
        platform_arr.append([60, 320, 180, 20, 2])                   # mid-left
        platform_arr.append([120, 160, 150, 20, 2])                  # top-left
        platform_arr.append([320, 280, 170, 20, 2])                  # mid-center
        platform_arr.append([360, 360, 120, 20, 2])                  # lower-center
        platform_arr.append([560, 300, 200, 20, 2])                  # mid-right
        platform_source = "level1_safe"
        return
    
    if level == 2:
        # Level 2: Still mostly safe but with small gaps
        platform_arr.append([0, HEIGHT - 90, 300, 20, 2])            # ground left (covers left lava)
        platform_arr.append([350, HEIGHT - 90, 450, 20, 2])          # ground right (covers right lava)
        platform_arr.append([60, 320, 180, 20, 2])                   # mid-left
        platform_arr.append([320, 280, 170, 20, 2])                  # mid-center
        platform_arr.append([560, 300, 200, 20, 2])                  # mid-right
        platform_arr.append([200, 160, 150, 20, 2])                  # top
        platform_source = "level2_safe"
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
        
    # For non-boss levels 3+, use pattern rotating through 10 designs
    # level 3/13 -> pattern 1, level 4/14 -> pattern 2, etc.
    pattern = (level - 2) % 10
    
    if pattern == 0:
        # STAIRCASE LEFT - platforms ascending from left to right
        platform_arr.append([20, HEIGHT - 80, 180, 20, 2])
        platform_arr.append([220, HEIGHT - 160, 160, 20, 2])
        platform_arr.append([400, HEIGHT - 240, 140, 20, 2])
        platform_arr.append([560, HEIGHT - 320, 120, 20, 2])
        platform_arr.append([100, HEIGHT - 400, 150, 20, 2])
        platform_arr.append([450, HEIGHT - 480, 180, 20, 2])
        platform_source = "pattern_0"
        
    elif pattern == 1:
        # STAIRCASE RIGHT - platforms descending from left to right
        platform_arr.append([20, HEIGHT - 480, 160, 20, 2])
        platform_arr.append([200, HEIGHT - 400, 140, 20, 2])
        platform_arr.append([360, HEIGHT - 320, 150, 20, 2])
        platform_arr.append([530, HEIGHT - 240, 140, 20, 2])
        platform_arr.append([150, HEIGHT - 160, 180, 20, 2])
        platform_arr.append([550, HEIGHT - 80, 180, 20, 2])
        platform_source = "pattern_1"
        
    elif pattern == 2:
        # PILLARS - tall vertical columns of platforms
        platform_arr.append([80, HEIGHT - 80, 100, 20, 2])
        platform_arr.append([80, HEIGHT - 200, 100, 20, 2])
        platform_arr.append([80, HEIGHT - 320, 100, 20, 2])
        platform_arr.append([350, HEIGHT - 140, 100, 20, 2])
        platform_arr.append([350, HEIGHT - 260, 100, 20, 2])
        platform_arr.append([350, HEIGHT - 380, 100, 20, 2])
        platform_arr.append([620, HEIGHT - 80, 100, 20, 2])
        platform_arr.append([620, HEIGHT - 200, 100, 20, 2])
        platform_arr.append([620, HEIGHT - 320, 100, 20, 2])
        platform_source = "pattern_2"
        
    elif pattern == 3:
        # PYRAMID - platforms form a pyramid shape
        platform_arr.append([320, HEIGHT - 80, 160, 20, 2])
        platform_arr.append([200, HEIGHT - 180, 120, 20, 2])
        platform_arr.append([480, HEIGHT - 180, 120, 20, 2])
        platform_arr.append([100, HEIGHT - 280, 100, 20, 2])
        platform_arr.append([350, HEIGHT - 280, 100, 20, 2])
        platform_arr.append([600, HEIGHT - 280, 100, 20, 2])
        platform_arr.append([250, HEIGHT - 380, 80, 20, 2])
        platform_arr.append([470, HEIGHT - 380, 80, 20, 2])
        platform_arr.append([360, HEIGHT - 480, 80, 20, 2])
        platform_source = "pattern_3"
        
    elif pattern == 4:
        # ZIGZAG - alternating left-right platforms
        platform_arr.append([50, HEIGHT - 80, 200, 20, 2])
        platform_arr.append([550, HEIGHT - 160, 200, 20, 2])
        platform_arr.append([50, HEIGHT - 240, 200, 20, 2])
        platform_arr.append([550, HEIGHT - 320, 200, 20, 2])
        platform_arr.append([250, HEIGHT - 400, 200, 20, 2])
        platform_arr.append([50, HEIGHT - 480, 150, 20, 2])
        platform_arr.append([600, HEIGHT - 480, 150, 20, 2])
        platform_source = "pattern_4"
        
    elif pattern == 6:
        # FLOATING ISLANDS - scattered small platforms
        platform_arr.append([100, HEIGHT - 100, 90, 20, 2])
        platform_arr.append([300, HEIGHT - 150, 80, 20, 2])
        platform_arr.append([500, HEIGHT - 120, 85, 20, 2])
        platform_arr.append([650, HEIGHT - 200, 90, 20, 2])
        platform_arr.append([150, HEIGHT - 250, 100, 20, 2])
        platform_arr.append([400, HEIGHT - 280, 75, 20, 2])
        platform_arr.append([600, HEIGHT - 330, 80, 20, 2])
        platform_arr.append([200, HEIGHT - 380, 90, 20, 2])
        platform_arr.append([450, HEIGHT - 420, 85, 20, 2])
        platform_arr.append([100, HEIGHT - 480, 100, 20, 2])
        platform_arr.append([600, HEIGHT - 500, 95, 20, 2])
        platform_source = "pattern_6"
        
    elif pattern == 7:
        # PARKOUR - challenging jumps with gaps
        platform_arr.append([50, HEIGHT - 80, 140, 20, 2])
        platform_arr.append([280, HEIGHT - 140, 100, 20, 2])
        platform_arr.append([480, HEIGHT - 200, 90, 20, 2])
        platform_arr.append([640, HEIGHT - 140, 110, 20, 2])
        platform_arr.append([450, HEIGHT - 300, 100, 20, 2])
        platform_arr.append([200, HEIGHT - 360, 120, 20, 2])
        platform_arr.append([520, HEIGHT - 440, 90, 20, 2])
        platform_arr.append([100, HEIGHT - 500, 130, 20, 2])
        platform_source = "pattern_7"
        
    elif pattern == 8:
        # SPLIT ARENA - two separate sides with bridge
        platform_arr.append([20, HEIGHT - 80, 280, 20, 2])
        platform_arr.append([500, HEIGHT - 80, 280, 20, 2])
        platform_arr.append([50, HEIGHT - 200, 180, 20, 2])
        platform_arr.append([570, HEIGHT - 200, 180, 20, 2])
        platform_arr.append([80, HEIGHT - 320, 140, 20, 2])
        platform_arr.append([580, HEIGHT - 320, 140, 20, 2])
        platform_arr.append([320, HEIGHT - 260, 160, 20, 2])  # Bridge
        platform_arr.append([150, HEIGHT - 440, 120, 20, 2])
        platform_arr.append([530, HEIGHT - 440, 120, 20, 2])
        platform_source = "pattern_8"
        
    elif pattern == 9:
        # SPIRAL - platforms in a spiral pattern
        platform_arr.append([350, HEIGHT - 80, 150, 20, 2])
        platform_arr.append([550, HEIGHT - 160, 130, 20, 2])
        platform_arr.append([600, HEIGHT - 280, 120, 20, 2])
        platform_arr.append([450, HEIGHT - 380, 140, 20, 2])
        platform_arr.append([250, HEIGHT - 440, 130, 20, 2])
        platform_arr.append([80, HEIGHT - 360, 120, 20, 2])
        platform_arr.append([50, HEIGHT - 240, 140, 20, 2])
        platform_arr.append([150, HEIGHT - 120, 150, 20, 2])
        platform_source = "pattern_9"
        
    else:
        # RANDOM CHAOS - completely random placement
        num_platforms = random.randint(9, 13)
        for i in range(num_platforms):
            x = random.randrange(20, WIDTH - 180)
            y = random.randrange(HEIGHT - 500, HEIGHT - 60)
            w = random.randrange(70, 200)
            if x + w > WIDTH - 10:
                w = WIDTH - x - 20
            platform_arr.append([x, y, w, 20, 2])
        platform_source = "pattern_random"
    
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
