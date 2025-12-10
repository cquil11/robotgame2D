# Headless smoke test for importing settings and sprites
# Uses SDL dummy drivers so this can run without opening a real window or audio device.
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame as pg
print('pygame before init:', pg.display.get_init(), pg.mixer.get_init())
pg.init()
# create a tiny dummy display so image operations that require a video mode succeed
try:
    pg.display.set_mode((1,1))
except Exception as e:
    print('display set_mode failed:', e)

# Import game modules
try:
    import sys
    # ensure repo root is on sys.path so sibling modules can be imported
    repo_root = os.path.dirname(os.path.dirname(__file__))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    import settings
    import sprites
    print('Imported settings and sprites')
except Exception as e:
    print('Import error:', e)
    raise

# Try to instantiate a Player and a Goblin to exercise constructors
try:
    p = sprites.Player(None)
    print('Player created, image size:', p.image.get_size())
except Exception as e:
    print('Player creation failed:', e)

try:
    g = sprites.Goblin(None)
    print('Goblin created, position:', g.rect.x, g.rect.y)
except Exception as e:
    print('Goblin creation failed:', e)

print('Smoke test completed')
