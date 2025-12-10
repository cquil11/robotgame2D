# Headless simulation for quick automated checks
# Sets SDL dummy drivers, initializes pygame, creates minimal fake game
# and runs a short update loop to exercise Player/Goblin/Fireball logic.

import os
import sys
import time
from types import SimpleNamespace

# Ensure dummy drivers are set BEFORE importing pygame
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

# Make repo root importable when run from tools/
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import pygame as pg

print('Starting headless simulation...')

pg.init()
try:
    pg.mixer.init()
except Exception:
    pass

# Import project modules (settings provides constants)
try:
    from settings import *  # noqa: F401,F403
    from sprites import Player, Goblin, Fireball
except Exception as e:
    print('Failed to import project modules:', e)
    raise

# Create a fake game object with minimal attributes expected by sprites
fake = SimpleNamespace()
fake.screen = pg.Surface((WIDTH, HEIGHT))
fake.all_sprites = pg.sprite.Group()
fake.goblins = pg.sprite.Group()
fake.skeletons = pg.sprite.Group()
fake.coins = pg.sprite.Group()
fake.fireballs = pg.sprite.Group()
fake.platforms = pg.sprite.Group()
fake.lava = pg.sprite.Group()
fake.monster = pg.sprite.Group()
fake.monsterbullet = pg.sprite.Group()

# Basic game state
fake.level = 1

# Instantiate player and a goblin
try:
    player = Player(fake)
    goblin = Goblin(fake)
except TypeError:
    # some constructors expect more args; try passing common defaults
    try:
        player = Player(fake)
    except Exception as e:
        print('Failed to create Player:', e)
        raise

# Add to groups
fake.all_sprites.add(player)
# Place goblin near player for quick interaction
try:
    goblin.rect.x = player.rect.x + 60
    goblin.rect.y = player.rect.y
except Exception:
    pass
fake.all_sprites.add(goblin)
fake.goblins.add(goblin)

print('Created Player and Goblin:')
print(' Player rect:', getattr(player, 'rect', None))
print(' Goblin rect:', getattr(goblin, 'rect', None))

# Record initial health for assertion
initial_g_health = getattr(goblin, 'health', None)
print(' Initial goblin starting health:', initial_g_health)

# Simulate the player casting a fireball at the goblin position
try:
    target = (goblin.rect.centerx, goblin.rect.centery)
    fb = player.cast_fireball(target)
    if fb:
        fake.fireballs.add(fb)
        fake.all_sprites.add(fb)
        print('Fireball created, target at', target)
    else:
        print('Player.cast_fireball returned None (insufficient mana or other).')
except Exception as e:
    print('Error creating fireball:', e)
    fb = None

# Run a short update loop for a few ticks
ticks = 60
hit_occurred = False
for t in range(ticks):
    fake.all_sprites.update()
    # Check collisions: fireball vs goblin
    if fb and fb.alive():
        hit_g = pg.sprite.spritecollide(fb, fake.goblins, False)
        if hit_g:
            print(f'[{t}] Fireball hit goblin!')
            hit_occurred = True
            break
    time.sleep(0.01)

# Final state report
p_hearts = getattr(player, 'hearts', 'N/A')
g_health = getattr(goblin, 'health', 'N/A')
p_hearts = getattr(player, 'hearts', 'N/A')
print('Final state:')
print(' Goblin health:', g_health)
print(' Player hearts:', p_hearts)
print(' Alive sprites:', len(fake.all_sprites))
print(' Hit occurred flag:', hit_occurred)
# Simple automated assertions for CI/regression checks
try:
    assert fb is not None, 'No fireball was created'
    # Accept either an explicit collision detection OR a reduction in health
    health_decreased = False
    try:
        if isinstance(initial_g_health, (int, float)) and isinstance(g_health, (int, float)):
            health_decreased = g_health < initial_g_health
    except Exception:
        health_decreased = False
    assert hit_occurred or health_decreased, 'Fireball did not damage the goblin as expected'
    print('HEADLESS TEST: PASS')
except AssertionError as e:
    print('HEADLESS TEST: FAIL -', e)

print('Headless simulation complete.')

pg.quit()
