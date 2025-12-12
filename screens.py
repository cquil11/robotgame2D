"""Screen and menu functions for the game."""
import pygame as pg
import os
from os import path
from settings import *
from ui_dialogs import show_confirm_dialog, show_save_quit_dialog
from highscores import load_highscores, add_highscore, is_highscore
import json


def draw_text(game, text, size, colors, x, y):
    """Draw text on the screen."""
    font = pg.font.Font(game.font_name, size)
    text_surface = font.render(text, True, colors)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (int(x), int(y))
    game.screen.blit(text_surface, text_rect)


def draw_button(game, text, rect, inactive_color, active_color, text_size=20):
    """Draw a rectangular button with centered text. Returns True if mouse is over it."""
    mx, my = pg.mouse.get_pos()
    hovered = rect.collidepoint((mx, my))
    color = active_color if hovered else inactive_color
    pg.draw.rect(game.screen, color, rect)
    # border
    pg.draw.rect(game.screen, WHITE, rect, 2)
    # draw label
    draw_text(game, text, text_size, WHITE, rect.centerx, rect.centery - (text_size // 2))
    return hovered


def draw_start_background(game):
    """Draw the start screen background alternating between selected images."""
    try:
        if getattr(game, 'start_backgrounds', None) and len(game.start_backgrounds) > 0:
            # Strict: always use the first loaded start background (start_background4)
            try:
                game.screen.blit(game.start_backgrounds[0], (0, 0))
                return
            except Exception:
                pass
    except Exception:
        pass
    # fallback: fill or procedurally generate (handled by caller if desired)
    game.screen.fill(BLACK)


def show_start_screen(game):
    """Start/menu screen - present New / Load / Quit options (text-based)."""
    options = ["New Game", "Load Game", "Instructions", "High Scores", "Quit"]
    selected = 0
    # Play background music for menu
    try:
        play_song('sounds/uzi_music.mp3')
    except Exception:
        pass

    # Refresh loaded save each time we enter the menu so displayed info is current
    try:
        game.loaded_save = game.load_game()
    except Exception:
        game.loaded_save = None

    while True:
        game.clock.tick(FPS)
        # Poll events once per frame and reuse for both keyboard and mouse handling
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                game.running = False
                return 'quit'
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP or event.key == pg.K_w:
                    selected = (selected - 1) % len(options)
                if event.key == pg.K_DOWN or event.key == pg.K_s:
                    selected = (selected + 1) % len(options)
                if event.key == pg.K_RETURN:
                    choice = options[selected]
                    if choice == 'New Game':
                        # If a save exists, confirm to avoid accidental overwrite
                        if getattr(game, 'loaded_save', None):
                            try:
                                confirmed = show_confirm_dialog(game, "Start New Game", "A saved game exists. Start New Game and overwrite the save?", yes_text='Start New', no_text='Cancel')
                            except Exception:
                                confirmed = False
                            if confirmed:
                                try:
                                    save_path = path.join(getattr(game, 'dir', '.'), 'savegame.json')
                                    if os.path.exists(save_path):
                                        os.remove(save_path)
                                except Exception:
                                    pass
                                return 'new'
                        else:
                            return 'new'
                    if choice == 'Load Game':
                        # attempt to load save; if present, mark to apply and start
                        loaded = game.load_game()
                        if loaded:
                            game.loaded_save = loaded
                            # applied_saved_game will be set in start_level when applying
                            game.applied_saved_game = False
                            return 'load'
                        else:
                            # flash a "No Save" message for a short time
                            game.screen.fill(BLACK)
                            draw_text(game, "No savegame found.", 28, WHITE, WIDTH/2, WINDOW_HEIGHT/2)
                            pg.display.flip()
                            pg.time.wait(1000)
                    if choice == 'Instructions':
                        show_instructions_screen(game)
                    if choice == 'High Scores':
                        show_highscores_screen(game)
                    if choice == 'Quit':
                        try:
                            confirmed = show_confirm_dialog(game, "Quit Game", "Are you sure you want to quit?")
                        except Exception:
                            confirmed = False
                        if confirmed:
                            try:
                                game.exit_now()
                            except SystemExit:
                                raise
                            except Exception:
                                game.playing = False
                                game.running = False
                                waiting = False
        # Simple gradient background instead of image
        game.screen.fill(BLACK)
        for i in range(WINDOW_HEIGHT):
            shade = int(20 + (i / WINDOW_HEIGHT) * 40)
            pg.draw.line(game.screen, (shade, shade, shade + 20), (0, i), (WIDTH, i))
        
        draw_text(game, TITLE, 64, GREEN, WIDTH/2, WINDOW_HEIGHT/4)

        # We'll support mouse hover/click: compute centers for each option
        option_x = WIDTH/2
        option_w = 350  # Width of hitbox
        option_h = 35   # Height of each button hitbox
        button_rects = []  # Store rects for precise collision detection
        for i, opt in enumerate(options):
            oy = WINDOW_HEIGHT/2 + i * 40
            color = YELLOW if i == selected else WHITE
            draw_text(game, opt, 30, color, option_x, oy)
            # Create rect for this button (centered around text)
            button_rect = pg.Rect(option_x - option_w/2, oy - option_h/2, option_w, option_h)
            button_rects.append(button_rect)

        # show save summary inline (under Load Game option) if present
        if getattr(game, 'loaded_save', None):
            try:
                sd = game.loaded_save
                lvl = sd.get('level', '?')
                sc = sd.get('score', '?')
                # place summary right under the Load Game option (index 1)
                draw_text(game, f"Saved: Level {lvl}  Score {sc}", 18, WHITE, option_x, WINDOW_HEIGHT/2 + 40 + 20)
            except Exception:
                pass

        # show hint
        draw_text(game, "Use UP/DOWN, MOUSE or ENTER to choose", 18, WHITE, WIDTH/2, WINDOW_HEIGHT - 60)
        pg.display.flip()

        # handle simple mouse hover and click using the previously-polled events
        for ev in [e for e in events if e.type in (pg.MOUSEMOTION, pg.MOUSEBUTTONDOWN)]:
            if ev.type == pg.MOUSEMOTION:
                mx, my = ev.pos
                for i, button_rect in enumerate(button_rects):
                    if button_rect.collidepoint(mx, my):
                        selected = i
                        break
            if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                # treat left click as selecting the current hovered option
                choice = options[selected]
                # jump to selection handling by simulating Enter
                if choice == 'New Game':
                    if getattr(game, 'loaded_save', None):
                        try:
                            confirmed = show_confirm_dialog(game, "Start New Game", "A saved game exists. Start New Game and overwrite the save?", yes_text='Start New', no_text='Cancel')
                        except Exception:
                            confirmed = False
                        if confirmed:
                            try:
                                save_path = path.join(getattr(game, 'dir', '.'), 'savegame.json')
                                if os.path.exists(save_path):
                                    os.remove(save_path)
                            except Exception:
                                pass
                            return 'new'
                    else:
                        return 'new'
                if choice == 'Load Game':
                    loaded = game.load_game()
                    if loaded:
                        game.loaded_save = loaded
                        game.applied_saved_game = False
                        return 'load'
                    else:
                        game.screen.fill(BLACK)
                        draw_text(game, "No savegame found.", 28, WHITE, WIDTH/2, WINDOW_HEIGHT/2)
                        pg.display.flip()
                        pg.time.wait(1000)
                if choice == 'Instructions':
                    show_instructions_screen(game)
                if choice == 'High Scores':
                    show_highscores_screen(game)
                if choice == 'Quit':
                    try:
                        confirmed = show_confirm_dialog(game, "Quit Game", "Are you sure you want to quit?")
                    except Exception:
                        confirmed = False
                    if confirmed:
                        game.running = False
                        return 'quit'


def show_pause_screen(game):
    """Game pause screen - modal loop until resume or quit."""
    # If a graceful exit was requested (user chose Quit/Save&Quit), skip
    # showing the game over screen. Otherwise always show Game Over so the
    # player sees their final score on death even if `self.running` was
    # toggled by other handlers.
    if getattr(game, 'should_exit', False):
        return
    # Draw pause overlay with clickable buttons
    waiting = True
    while waiting:
        game.clock.tick(FPS)
        # Precompute button rects so they're available during event handling
        resume_rect = pg.Rect(WIDTH/2 - 150, WINDOW_HEIGHT/2 - 20, 140, 48)
        savequit_rect = pg.Rect(WIDTH/2 + 10, WINDOW_HEIGHT/2 - 20, 160, 48)
        quit_rect = pg.Rect(WIDTH/2 - 70, WINDOW_HEIGHT/2 + 50, 140, 48)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                waiting = False
                game.running = False
                game.playing = False
                game.paused = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    # Resume
                    game.paused = False
                    waiting = False
                elif event.key == pg.K_s:
                    # Press 'S' to Save & Quit from pause
                    try:
                        choice = 'save'
                        try:
                            game.save_game()
                        except Exception:
                            pass
                        try:
                            game.exit_now()
                            waiting = False
                        except SystemExit:
                            raise
                        except Exception:
                            game.paused = False
                            game.playing = False
                            game.running = False
                            waiting = False
                    except Exception:
                        # If anything goes wrong, fall back to normal pause
                        pass
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if resume_rect.collidepoint((mx, my)):
                    game.paused = False
                    waiting = False
                if savequit_rect.collidepoint((mx, my)):
                    # Offer the 3-way Save/Quit/Cancel modal
                    try:
                        choice = show_save_quit_dialog(game, "Exit Game", "Do you want to save before quitting?")
                    except Exception:
                        choice = 'cancel'
                    if choice == 'save':
                        try:
                            game.save_game()
                        except Exception:
                            pass
                        # Ensure game exits after saving
                        try:
                            game.exit_now()
                            waiting = False
                        except SystemExit:
                            raise
                        except Exception:
                            # Fallback: set flags so outer loops stop
                            game.paused = False
                            game.playing = False
                            game.running = False
                            waiting = False
                    elif choice == 'quit':
                        try:
                            game.exit_now()
                        except SystemExit:
                            raise
                        except Exception:
                            game.paused = False
                            game.playing = False
                            game.running = False
                            waiting = False
                    else:
                        # cancel -> remain paused
                        pass
                if quit_rect.collidepoint((mx, my)):
                    try:
                        choice = show_save_quit_dialog(game, "Exit Game", "Do you want to save before quitting?")
                    except Exception:
                        choice = 'cancel'
                    if choice == 'save':
                        try:
                            game.save_game()
                        except Exception:
                            pass
                        try:
                            game.exit_now()
                            waiting = False
                        except SystemExit:
                            raise
                        except Exception:
                            game.paused = False
                            game.playing = False
                            game.running = False
                            waiting = False
                    elif choice == 'quit':
                        try:
                            game.exit_now()
                        except SystemExit:
                            raise
                        except Exception:
                            game.paused = False
                            game.playing = False
                            game.running = False
                            waiting = False

        # Draw overlay and pause text while waiting
        overlay = pg.Surface((WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        game.screen.blit(overlay, (0, 0))
        draw_text(game, "PAUSED", 64, WHITE, WIDTH / 2, WINDOW_HEIGHT / 2 - 120)
        # buttons
        draw_button(game, "Resume", resume_rect, (80, 120, 200), (120, 160, 240), text_size=22)
        draw_button(game, "Save & Quit", savequit_rect, (80, 160, 80), (120, 220, 120), text_size=20)
        draw_button(game, "Quit", quit_rect, (160, 80, 80), (220, 120, 120), text_size=20)
        pg.display.flip()


def show_level_complete(game):
    """Level complete screen - show stats and options."""
    # Handle mouse clicks for buttons
    for event in pg.event.get():
        if event.type == pg.QUIT:
            waiting = False
            game.running = False
            game.playing = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                waiting = False
            if event.key == pg.K_s:
                try:
                    game.save_game()
                except Exception:
                    pass
                try:
                    game.exit_now()
                    waiting = False
                except SystemExit:
                    raise
                except Exception:
                    game.playing = False
                    game.running = False
                    waiting = False
            if event.key == pg.K_q:
                try:
                    choice = show_save_quit_dialog(game, "Exit Game", "Do you want to save before quitting?")
                except Exception:
                    choice = 'cancel'
                if choice == 'save':
                    try:
                        game.save_game()
                    except Exception:
                        pass
                    try:
                        game.exit_now()
                        waiting = False
                    except SystemExit:
                        raise
                    except Exception:
                        game.playing = False
                        game.running = False
                        waiting = False
                if choice == 'quit':
                    try:
                        game.exit_now()
                        waiting = False
                    except SystemExit:
                        raise
                    except Exception:
                        game.playing = False
                        game.running = False
                        waiting = False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if getattr(game, 'should_exit', False):
                return
            waiting = True
            while waiting:
                # create buttons: Continue, Save & Quit, Quit (define every frame)
                cont_rect = pg.Rect(WIDTH/2 - 260, WINDOW_HEIGHT/2 + 120, 180, 48)
                save_rect = pg.Rect(WIDTH/2 - 10, WINDOW_HEIGHT/2 + 120, 200, 48)
                quit_rect = pg.Rect(WIDTH/2 + 220, WINDOW_HEIGHT/2 + 120, 160, 48)
                game.clock.tick(FPS)
                # Draw menu background and stats/buttons every frame
                game.screen.fill(BLACK)
                completed_level = max(1, game.level - 1)
                draw_text(game, "LEVEL " + str(completed_level) + " COMPLETE!", 56, GREEN, WIDTH/2, WINDOW_HEIGHT/2 - 120)
                if game.damage_taken_this_level == 0:
                    draw_text(game, "PERFECT CLEAR! +1000", 32, (255, 215, 0), WIDTH/2, WINDOW_HEIGHT/2 - 80)
                draw_text(game, "Level: " + str(completed_level), 26, WHITE, WIDTH/2, WINDOW_HEIGHT/2 - 50)
                if game.max_streak > 0:
                    draw_text(game, "Best Streak: " + str(game.max_streak) + "x", 24, YELLOW, WIDTH/2, WINDOW_HEIGHT/2 - 20)
                if game.accuracy_attempts > 0:
                    accuracy = int((game.accuracy_hits / game.accuracy_attempts) * 100)
                    acc_color = GREEN if accuracy >= 70 else YELLOW if accuracy >= 50 else WHITE
                    draw_text(game, "Accuracy: " + str(accuracy) + "%", 24, acc_color, WIDTH/2, WINDOW_HEIGHT/2 + 10)
                draw_text(game, "Enemies Defeated: " + str(game.total_kills), 24, WHITE, WIDTH/2, WINDOW_HEIGHT/2 + 40)
                draw_text(game, "Press ENTER for Level " + str(game.level), 26, WHITE, WIDTH/2, WINDOW_HEIGHT/2 + 40)
                draw_button(game, "Continue", cont_rect, (80, 120, 200), (120, 160, 240), text_size=18)
                draw_button(game, "Save & Quit", save_rect, (80, 160, 80), (120, 220, 120), text_size=16)
                draw_button(game, "Quit", quit_rect, (160, 80, 80), (220, 120, 120), text_size=16)
                pg.display.flip()
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        waiting = False
                        game.running = False
                        game.playing = False
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_RETURN:
                            waiting = False
                        if event.key == pg.K_s:
                            try:
                                game.save_game()
                            except Exception:
                                pass
                            try:
                                game.exit_now()
                                waiting = False
                            except SystemExit:
                                raise
                            except Exception:
                                game.playing = False
                                game.running = False
                                waiting = False
                        if event.key == pg.K_q:
                            try:
                                choice = show_save_quit_dialog(game, "Exit Game", "Do you want to save before quitting?")
                            except Exception:
                                choice = 'cancel'
                            if choice == 'save':
                                try:
                                    game.save_game()
                                except Exception:
                                    pass
                                try:
                                    game.exit_now()
                                    waiting = False
                                except SystemExit:
                                    raise
                                except Exception:
                                    game.playing = False
                                    game.running = False
                                    waiting = False
                            if choice == 'quit':
                                try:
                                    game.exit_now()
                                    waiting = False
                                except SystemExit:
                                    raise
                                except Exception:
                                    game.playing = False
                                    game.running = False
                                    waiting = False
                    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = event.pos
                        if cont_rect.collidepoint((mx, my)):
                            waiting = False
                        elif save_rect.collidepoint((mx, my)):
                            try:
                                game.save_game()
                            except Exception:
                                pass
                            try:
                                game.exit_now()
                                waiting = False
                            except SystemExit:
                                raise
                            except Exception:
                                game.playing = False
                                game.running = False
                                waiting = False
                        elif quit_rect.collidepoint((mx, my)):
                            try:
                                choice = show_save_quit_dialog(game, "Exit Game", "Do you want to save before quitting?")
                            except Exception:
                                choice = 'cancel'
                            if choice == 'save':
                                try:
                                    game.save_game()
                                except Exception:
                                    pass
                                try:
                                    game.exit_now()
                                    waiting = False
                                except SystemExit:
                                    raise
                                except Exception:
                                    game.playing = False
                                    game.running = False
                                    waiting = False
                            if choice == 'quit':
                                try:
                                    game.exit_now()
                                    waiting = False
                                except SystemExit:
                                    raise
                                except Exception:
                                    game.playing = False
                                    game.running = False
                                    waiting = False
                        game.running = False


def show_instructions_screen(game):
    """Display game instructions."""
    waiting = True
    while waiting and game.running:
        game.clock.tick(FPS)
        game.screen.fill(BLACK)
        
        # Gradient background using full window height
        for i in range(WINDOW_HEIGHT):
            shade = int(20 + (i / WINDOW_HEIGHT) * 40)
            pg.draw.line(game.screen, (shade, shade, shade + 20), (0, i), (WIDTH, i))
        
        draw_text(game, "HOW TO PLAY", 64, GREEN, WIDTH/2, 50)
        
        # Controls Section
        draw_text(game, "CONTROLS", 40, YELLOW, WIDTH/2, 130)
        controls = [
            ("Arrow Keys / WASD", "Move left/right"),
            ("SPACEBAR / W", "Jump"),
            ("Left Click", "Sword Attack (hold for heavy attack)"),
            ("Right Click", "Activate Shield (3s duration, 6s cooldown)"),
            ("R or E", "Cast Fireball (costs 15 mana)"),
            ("ESC", "Pause game"),
        ]
        
        y = 180
        for key, action in controls:
            draw_text(game, f"{key}:", 20, (100, 200, 255), WIDTH/2 - 150, y)
            draw_text(game, action, 20, WHITE, WIDTH/2 + 80, y)
            y += 35
        
        # Gameplay Section
        draw_text(game, "GAMEPLAY", 40, YELLOW, WIDTH/2, y + 20)
        y += 70
        
        gameplay = [
            "• Defeat all enemies to advance to the next level",
            "• Collect hearts to restore health",
            "• Collect coins for bonus points",
            "• Choose stat upgrades after completing each level",
            "• Every 5th level features a powerful boss battle",
            "• Shield blocks all projectile damage (arrows & fireballs)",
        ]
        
        for line in gameplay:
            draw_text(game, line, 20, WHITE, WIDTH/2, y)
            y += 35
        
        # Scoring Section
        draw_text(game, "SCORING & BONUSES", 40, YELLOW, WIDTH/2, y + 20)
        y += 70
        
        scoring = [
            "• Build kill streaks to multiply your score",
            "• Perfect clear (no damage) = +1,000 bonus points",
            "• Elite enemies (golden) = 3x score and health",
            "• Complete levels quickly for time bonuses",
            "• Combo attacks increase damage and scoring",
        ]
        
        for line in scoring:
            draw_text(game, line, 20, WHITE, WIDTH/2, y)
            y += 35
        
        # Footer
        draw_text(game, "Press ENTER or ESC to return to menu", 22, (150, 255, 150), WIDTH/2, WINDOW_HEIGHT - 40)
        
        pg.display.flip()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game.running = False
                waiting = False
            if event.type == pg.KEYDOWN:
                if event.key in (pg.K_RETURN, pg.K_ESCAPE):
                    waiting = False


def show_highscores_screen(game):
    """Display top 5 highscores."""
    waiting = True
    while waiting and game.running:
        game.clock.tick(FPS)
        game.screen.fill(BLACK)
        
        # Gradient background
        for i in range(WINDOW_HEIGHT):
            shade = int(20 + (i / WINDOW_HEIGHT) * 40)
            pg.draw.line(game.screen, (shade, shade, shade + 20), (0, i), (WIDTH, i))
        
        draw_text(game, "TOP SCORES", 56, GREEN, WIDTH/2, 60)
        
        # Load scores from the correct directory
        try:
            scores_dir = getattr(game, 'dir', '.')
            scores = load_highscores(scores_dir)
        except Exception as e:
            scores = []
        
        if len(scores) == 0:
            draw_text(game, "No scores yet!", 32, WHITE, WIDTH/2, WINDOW_HEIGHT/2)
        else:
            y = 160
            for idx, score_data in enumerate(scores):
                rank = idx + 1
                name = str(score_data.get('name', 'Unknown'))[:15]  # Truncate long names
                score = int(score_data.get('score', 0))
                
                medal = ""
                color = WHITE
                if rank == 1:
                    medal = "#1"
                    color = (255, 215, 0)  # Gold
                elif rank == 2:
                    medal = "#2"
                    color = (192, 192, 192)  # Silver
                elif rank == 3:
                    medal = "#3"
                    color = (205, 127, 50)  # Bronze
                else:
                    medal = f"#{rank}"
                    color = WHITE
                
                # Format: "#1 PlayerName ........ 12345"
                text_str = f"{medal:<4} {name:<16} {score:>6}"
                draw_text(game, text_str, 24, color, WIDTH/2, y)
                y += 50
        
        draw_text(game, "Press ENTER to return to menu", 20, WHITE, WIDTH/2, WINDOW_HEIGHT - 60)
        pg.display.flip()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game.running = False
                waiting = False
            if event.type == pg.KEYDOWN:
                if event.key in (pg.K_RETURN, pg.K_ESCAPE):
                    waiting = False


def get_player_name(game):
    """Get player name for highscore entry."""
    name = ""
    entering = True
    blink_timer = 0
    while entering and game.running:
        game.clock.tick(FPS)
        game.screen.fill(BLACK)
        blink_timer += 1
        
        # Gradient background
        for i in range(HEIGHT):
            shade = int(20 + (i / HEIGHT) * 40)
            pg.draw.line(game.screen, (shade, shade, shade + 20), (0, i), (WIDTH, i))
        
        draw_text(game, "NEW HIGH SCORE!", 56, (255, 215, 0), WIDTH/2, 100)
        draw_text(game, f"Score: {game.score}", 32, YELLOW, WIDTH/2, 180)
        draw_text(game, "Enter your name (max 15 characters):", 24, WHITE, WIDTH/2, 280)
        
        # Draw input box
        input_box = pg.Rect(WIDTH/2 - 150, 340, 300, 40)
        pg.draw.rect(game.screen, WHITE, input_box, 2)
        
        display_name = name if len(name) < 15 else name[:15]
        # Add blinking cursor
        if (blink_timer // 15) % 2 == 0:
            cursor = "|" if len(name) < 15 else ""
        else:
            cursor = ""
        draw_text(game, display_name + cursor, 28, WHITE, input_box.centerx, input_box.centery - 5)
        
        # Highlight instructions in bright color
        draw_text(game, "Press ENTER to confirm", 20, (0, 255, 0), WIDTH/2, 420)
        
        # Add additional hint in smaller text
        draw_text(game, "or ESC to skip (name will be 'Player')", 14, (150, 150, 150), WIDTH/2, 450)
        
        pg.display.flip()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game.running = False
                entering = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    if len(name.strip()) > 0:
                        entering = False
                elif event.key == pg.K_ESCAPE:
                    name = ""
                    entering = False
                elif event.key == pg.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isprintable() and len(name) < 15:
                    name += event.unicode
    
    return name.strip() if name.strip() else "Player"
