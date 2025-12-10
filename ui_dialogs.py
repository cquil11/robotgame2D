import os
import pygame as pg
from os import path
from settings import *


def show_boss_warning(game):
    if not game.running:
        return
    game.draw_menu_background()
    game.draw_text("BOSS FIGHT!", 70, RED, WIDTH / 2, HEIGHT / 2 - 80)
    game.draw_text(f"Level {game.level}", 40, YELLOW, WIDTH / 2, HEIGHT / 2 - 10)
    game.draw_text("Prepare yourself...", 30, WHITE, WIDTH / 2, HEIGHT / 2 + 50)
    game.draw_text("Press ENTER to begin", 25, WHITE, WIDTH / 2, HEIGHT / 2 + 100)
    pg.display.flip()
    pg.time.wait(1500)
    waiting = True
    while waiting:
        game.clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                waiting = False
                game.running = False
                game.playing = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    waiting = False


def show_go_screen(game):
    goblins_arr.clear()
    coin_arr.clear()
    player_arr.clear()
    monster_arr.clear()
    skel_arr.clear()
    reset_plat_list()
    if not game.running:
        return
    game.screen.fill(BLACK)
    title_y = HEIGHT / 2 - 80
    score_y = HEIGHT / 2 - 20
    
    # Check if this is a new highscore using the highscores module
    is_new_hs = False
    try:
        from highscores import is_highscore, add_highscore
        is_new_hs = is_highscore(game.score, game.dir)
    except Exception as e:
        print(f"Error checking highscore: {e}")
        pass
    
    # Helper function to save highscore if needed
    def save_hs_if_needed():
        if is_new_hs:
            try:
                from screens import get_player_name
                player_name = get_player_name(game)
                if player_name and len(player_name.strip()) > 0:
                    from highscores import add_highscore
                    add_highscore(player_name, game.score, game.dir)
                elif not player_name:
                    # Fallback: use default name
                    from highscores import add_highscore
                    add_highscore("Player", game.score, game.dir)
            except Exception as e:
                print(f"Error saving highscore: {e}")
                # Fallback: try to save with default name anyway
                try:
                    from highscores import add_highscore
                    add_highscore("Player", game.score, game.dir)
                except Exception as e2:
                    print(f"Fallback also failed: {e2}")
    
    if is_new_hs:
        game.highscore = game.score
        game.draw_text("NEW HIGH SCORE!!!!!!", 40, GREEN, WIDTH / 2, title_y)
    else:
        game.draw_text("HIGH SCORE:: " + str(game.highscore), 40, GREEN, WIDTH / 2, title_y)
    game.draw_text("FINAL SCORE:: " + str(game.score), 40, GREEN, WIDTH / 2, score_y)
    pg.display.flip()
    game_over_sound.stop()
    play_song('sounds/death_song.mp3')
    pg.mixer.music.unpause()
    menu_rect = pg.Rect(WIDTH / 2 - 120, HEIGHT / 2 + 100, 240, 48)
    quit_rect = pg.Rect(WIDTH / 2 + 160, HEIGHT / 2 + 100, 160, 48)
    waiting = True
    while waiting:
        game.clock.tick(FPS)
        game.screen.fill(BLACK)
        if is_new_hs:
            game.draw_text("NEW HIGH SCORE!!!!!!", 40, GREEN, WIDTH / 2, title_y)
        else:
            game.draw_text("HIGH SCORE:: " + str(game.highscore), 40, GREEN, WIDTH / 2, title_y)
        game.draw_text("FINAL SCORE:: " + str(game.score), 40, GREEN, WIDTH / 2, score_y)
        game.draw_button("Return to Menu", menu_rect, (80, 120, 200), (120, 160, 240), text_size=20)
        game.draw_button("Quit", quit_rect, (160, 80, 80), (220, 120, 120), text_size=18)
        game.draw_text("Press ENTER to return to menu, or Q/ESC to Quit", 18, WHITE, WIDTH / 2, HEIGHT - 60)
        pg.display.flip()
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                # Save highscore if needed before quitting via window close
                save_hs_if_needed()
                waiting = False
                game.running = False
                game.playing = False
            if ev.type == pg.KEYDOWN:
                if ev.key == pg.K_RETURN:
                    # Save highscore if needed before returning to menu
                    save_hs_if_needed()
                    waiting = False
                if ev.key == pg.K_q or ev.key == pg.K_ESCAPE:
                    # Save highscore if needed before quitting
                    save_hs_if_needed()
                    try:
                        game.exit_now()
                        waiting = False
                    except SystemExit:
                        raise
                    except Exception:
                        game.playing = False
                        game.running = False
                        waiting = False
            if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                if menu_rect.collidepoint((mx, my)):
                    # Save highscore if needed when clicking menu button
                    save_hs_if_needed()
                    waiting = False
                elif quit_rect.collidepoint((mx, my)):
                    # Save highscore if needed before quitting
                    save_hs_if_needed()
                    try:
                        game.exit_now()
                        waiting = False
                    except SystemExit:
                        raise
                    except Exception:
                        game.playing = False
                        game.running = False
                        waiting = False


def show_confirm_dialog(game, title, message, yes_text='Yes', no_text='No'):
    if not getattr(game, 'running', True):
        return False
    w = 600
    h = 220
    rect = pg.Rect((WIDTH - w) // 2, (HEIGHT - h) // 2, w, h)
    yes_rect = pg.Rect(rect.left + 60, rect.bottom - 80, 140, 48)
    no_rect = pg.Rect(rect.right - 200, rect.bottom - 80, 140, 48)
    waiting = True
    confirmed = False
    while waiting and getattr(game, 'running', True):
        game.clock.tick(FPS)
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                game.running = False
                waiting = False
                confirmed = False
                break
            if ev.type == pg.KEYDOWN:
                if ev.key == pg.K_y:
                    confirmed = True
                    waiting = False
                    break
                if ev.key == pg.K_n or ev.key == pg.K_ESCAPE:
                    confirmed = False
                    waiting = False
                    break
            if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                if yes_rect.collidepoint((mx, my)):
                    confirmed = True
                    waiting = False
                    break
                if no_rect.collidepoint((mx, my)):
                    confirmed = False
                    waiting = False
                    break
        overlay = pg.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        game.screen.blit(overlay, (0, 0))
        pg.draw.rect(game.screen, (30, 30, 30), rect)
        pg.draw.rect(game.screen, WHITE, rect, 2)
        game.draw_text(title, 28, WHITE, rect.centerx, rect.top + 18)
        game.draw_text(message, 20, WHITE, rect.centerx, rect.top + 70)
        game.draw_button(yes_text, yes_rect, (80, 160, 80), (120, 220, 120), text_size=20)
        game.draw_button(no_text, no_rect, (160, 80, 80), (220, 120, 120), text_size=20)
        pg.display.flip()
    return bool(confirmed)


def show_save_quit_dialog(game, title="Exit Game", message="Do you want to save before quitting?"):
    if not getattr(game, 'running', True):
        return 'cancel'
    w = 700
    h = 260
    rect = pg.Rect((WIDTH - w) // 2, (HEIGHT - h) // 2, w, h)
    save_rect = pg.Rect(rect.left + 40, rect.bottom - 86, 180, 56)
    quit_rect = pg.Rect(rect.centerx - 90, rect.bottom - 86, 180, 56)
    cancel_rect = pg.Rect(rect.right - 220, rect.bottom - 86, 180, 56)
    waiting = True
    result = 'cancel'
    while waiting and getattr(game, 'running', True):
        game.clock.tick(FPS)
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                game.running = False
                waiting = False
                result = 'cancel'
                break
            if ev.type == pg.KEYDOWN:
                if ev.key == pg.K_s:
                    result = 'save'
                    waiting = False
                    break
                if ev.key == pg.K_q:
                    result = 'quit'
                    waiting = False
                    break
                if ev.key == pg.K_ESCAPE:
                    result = 'cancel'
                    waiting = False
                    break
            if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                if save_rect.collidepoint((mx, my)):
                    result = 'save'
                    waiting = False
                    break
                if quit_rect.collidepoint((mx, my)):
                    result = 'quit'
                    waiting = False
                    break
                if cancel_rect.collidepoint((mx, my)):
                    result = 'cancel'
                    waiting = False
                    break
        overlay = pg.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        game.screen.blit(overlay, (0, 0))
        pg.draw.rect(game.screen, (30, 30, 30), rect)
        pg.draw.rect(game.screen, WHITE, rect, 2)
        game.draw_text(title, 28, WHITE, rect.centerx, rect.top + 18)
        game.draw_text(message, 20, WHITE, rect.centerx, rect.top + 70)
        game.draw_button("Save & Quit", save_rect, (80, 160, 80), (120, 220, 120), text_size=20)
        game.draw_button("Quit", quit_rect, (200, 80, 80), (240, 120, 120), text_size=20)
        game.draw_button("Cancel", cancel_rect, (100, 100, 100), (160, 160, 160), text_size=20)
        game.draw_text("Press S to Save & Quit, Q to Quit without saving, or ESC to Cancel", 16, WHITE, rect.centerx, rect.bottom - 120)
        pg.display.flip()
    return result
