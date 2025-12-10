import pygame as pg
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
    upgrades = [
        ("+10 Max Hearts", "max_hearts"),
        ("+1 Attack Power", "attack_power"),
        ("+0.1 Speed Mult", "speed_mult"),
        ("+10 Max Mana", "max_mana"),
        ("+1 Max Combo", "max_combo"),
    ]
    selected = 0
    waiting = True
    while waiting and game.running and not getattr(game, 'should_exit', False):
        game.clock.tick(FPS)
        game.screen.fill(BLACK)
        game.draw_text("Choose an Upgrade!", 48, (0, 255, 0), WIDTH // 2, HEIGHT // 2 - 120)

        button_rects = []
        for i, (label, _) in enumerate(upgrades):
            rect = pg.Rect(WIDTH // 2 - 180, HEIGHT // 2 - 50 + i * 60, 360, 50)
            color = (120, 120, 40) if i == selected else (80, 80, 80)
            pg.draw.rect(game.screen, color, rect, 0)
            pg.draw.rect(game.screen, (255, 255, 255), rect, 2)
            text_color = (255, 255, 0) if i == selected else (255, 255, 255)
            game.draw_text(label, 28, text_color, rect.centerx, rect.centery)
            button_rects.append(rect)

        game.draw_text("Use UP/DOWN or mouse, ENTER to select", 20, (255, 255, 255), WIDTH // 2, HEIGHT - 80)

        quit_rect = pg.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 270, 160, 44)
        pg.draw.rect(game.screen, (160, 80, 80), quit_rect, 0)
        pg.draw.rect(game.screen, (255, 255, 255), quit_rect, 2)
        game.draw_text("Quit", 28, (255, 255, 255), quit_rect.centerx, quit_rect.centery)

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
                if quit_rect.collidepoint((mx, my)):
                    game.exit_now()
                    waiting = False
