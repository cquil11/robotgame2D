import pygame as pg
import random
from settings import *


def apply_upgrade(game, upgrade):
    if not hasattr(game, 'player') or not game.player:
        return
    if upgrade == "max_hearts":
        game.player.max_hearts = getattr(game.player, 'max_hearts', 100) + 10
        game.player.hearts = game.player.max_hearts
    elif upgrade == "attack_power":
        game.player.attack_power = getattr(game.player, 'attack_power', 1) + 1
    elif upgrade == "speed_mult":
        game.player.speed_mult = round(getattr(game.player, 'speed_mult', 1.0) + 0.1, 2)
    elif upgrade == "max_mana":
        game.player.max_mana = getattr(game.player, 'max_mana', 100) + 10
        game.player.mana = game.player.max_mana
    elif upgrade == "max_combo":
        game.player.max_combo = getattr(game.player, 'max_combo', 5) + 1


def show_upgrade_screen(game):
    if not game.running or getattr(game, 'should_exit', False):
        return
    
    # All possible upgrades
    all_upgrades = [
        ("+10 Max Health", "max_hearts"),
        ("+1 Attack Power", "attack_power"),
        ("+0.1 Speed", "speed_mult"),
        ("+10 Max Mana", "max_mana"),
        ("+1 Max Combo", "max_combo"),
    ]
    
    # Randomly select 3 upgrades to display
    upgrades = random.sample(all_upgrades, 3)
    
    selected = 0
    waiting = True
    while waiting and game.running and not getattr(game, 'should_exit', False):
        game.clock.tick(FPS)
        game.screen.fill(BLACK)
        game.draw_text("Choose an Upgrade!", 48, (0, 255, 0), WIDTH // 2, HEIGHT // 2 - 140)

        button_rects = []
        # Larger buttons with better spacing
        button_width = 400
        button_height = 70
        start_y = HEIGHT // 2 - 50
        spacing = 90
        
        for i, (label, _) in enumerate(upgrades):
            rect = pg.Rect(WIDTH // 2 - button_width // 2, start_y + i * spacing, button_width, button_height)
            color = (120, 120, 40) if i == selected else (80, 80, 80)
            pg.draw.rect(game.screen, color, rect, 0)
            pg.draw.rect(game.screen, (255, 255, 255), rect, 3)
            text_color = (255, 255, 0) if i == selected else (255, 255, 255)
            # Use smaller font size to fit text
            game.draw_text(label, 24, text_color, rect.centerx, rect.centery)
            button_rects.append(rect)

        game.draw_text("Use UP/DOWN or mouse, ENTER to select", 18, (200, 200, 200), WIDTH // 2, HEIGHT - 100)

        save_quit_rect = pg.Rect(WIDTH // 2 - 120, HEIGHT - 55, 240, 40)
        pg.draw.rect(game.screen, (160, 80, 80), save_quit_rect, 0)
        pg.draw.rect(game.screen, (255, 255, 255), save_quit_rect, 2)
        game.draw_text("Save & Quit", 16, (255, 255, 255), save_quit_rect.centerx, save_quit_rect.centery)

        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                game.running = False
                waiting = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    selected = (selected - 1) % len(upgrades)
                if event.key == pg.K_DOWN:
                    selected = (selected + 1) % len(upgrades)
                if event.key == pg.K_RETURN:
                    apply_upgrade(game, upgrades[selected][1])
                    waiting = False
                if event.key in (pg.K_q, pg.K_ESCAPE):
                    game.exit_now()
                    waiting = False
            if event.type == pg.MOUSEMOTION:
                mx, my = event.pos
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint((mx, my)):
                        selected = i
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint((mx, my)):
                        apply_upgrade(game, upgrades[i][1])
                        waiting = False
                if save_quit_rect.collidepoint((mx, my)):
                    game.save_game()
                    game.exit_now()
                    waiting = False
