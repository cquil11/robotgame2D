"""Game utility functions for save/load and other helpers."""
import pygame as pg
import json
from os import path
from settings import *


def save_game(game):
    """Save minimal player/game state to a JSON file."""
    try:
        save = {
            'level': game.level,
            'score': game.score,
            'player': {
                'max_hearts': getattr(game.player, 'max_hearts', 100),
                'hearts': getattr(game.player, 'hearts', 100),
                'max_mana': getattr(game.player, 'max_mana', 100),
                'mana': getattr(game.player, 'mana', 100),
                'attack_power': getattr(game.player, 'attack_power', 1),
                'speed_mult': getattr(game.player, 'speed_mult', 1.0),
                'max_combo': getattr(game.player, 'max_combo', 5)
            }
        }
        save_path = path.join(getattr(game, 'dir', '.'), 'savegame.json')
        with open(save_path, 'w') as f:
            json.dump(save, f, indent=2)
    except Exception as e:
        # If saving fails, print error but don't crash
        print('Failed to save game:', e)


def exit_now(game):
    """Request a graceful shutdown of the game.

    Instead of calling sys.exit directly (which is abrupt and can make
    nested modal loops difficult to manage during testing), this method
    sets flags that the main loop will observe and then performs a
    pygame quit. Handlers should call this to request shutdown.
    """
    # Request a graceful exit; top-level code should stop when this is set.
    # Do not call pg.quit() here — top-level loop will call pg.quit() after
    # observing these flags so we avoid closing the display from inside
    # nested modal handlers.
    try:
        game.playing = False
        game.running = False
        game.should_exit = True
    except Exception:
        # If we can't set attributes for some reason, fallback to raising
        raise SystemExit(0)


def wait_for_key(game):
    """Wait for a key press to continue."""
    waiting = True
    while waiting:
        game.clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                waiting = False
                game.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    play_song('sounds/uzi_music.mp3')
                    waiting = False
                if event.key == pg.K_ESCAPE:
                    if game.playing:
                        game.playing = False
                    game.running = False
                    waiting = False
