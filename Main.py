



import pygame as pg
from pygame.locals import *
import random
from settings import *
from sprites import *
from os import path
import os
from datetime import datetime
import json
import time
import sys


class Game:
    def show_upgrade_screen(self):
        """Display an upgrade menu after each level. Player chooses one upgrade."""
        if not self.running or getattr(self, 'should_exit', False):
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
        while waiting and self.running and not getattr(self, 'should_exit', False):
            self.clock.tick(FPS)
            self.screen.fill(BLACK)
            self.draw_text("Choose an Upgrade!", 48, (0,255,0), WIDTH//2, HEIGHT//2 - 120)
            for i, (label, _) in enumerate(upgrades):
                color = (255,255,0) if i == selected else (255,255,255)
                self.draw_text(label, 32, color, WIDTH//2, HEIGHT//2 - 40 + i*50)
            self.draw_text("Use UP/DOWN or mouse, ENTER to select", 20, (255,255,255), WIDTH//2, HEIGHT - 80)
            # Draw buttons for mouse
            button_rects = []
            for i, (label, _) in enumerate(upgrades):
                rect = pg.Rect(WIDTH//2 - 180, HEIGHT//2 - 50 + i*50, 360, 44)
                pg.draw.rect(self.screen, (80,80,80) if i != selected else (120,120,40), rect, 0)
                pg.draw.rect(self.screen, (255,255,255), rect, 2)
                button_rects.append(rect)
            # Draw Quit button
            quit_rect = pg.Rect(WIDTH//2 - 80, HEIGHT//2 + 220, 160, 44)
            pg.draw.rect(self.screen, (160,80,80), quit_rect, 0)
            pg.draw.rect(self.screen, (255,255,255), quit_rect, 2)
            self.draw_text("Quit", 28, (255,255,255), quit_rect.centerx, quit_rect.centery-14)
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        selected = (selected - 1) % len(upgrades)
                    if event.key == pg.K_DOWN:
                        selected = (selected + 1) % len(upgrades)
                    if event.key == pg.K_RETURN:
                        self.apply_upgrade(upgrades[selected][1])
                        waiting = False
                    if event.key == pg.K_q or event.key == pg.K_ESCAPE:
                        self.exit_now()
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
                            self.apply_upgrade(upgrades[i][1])
                            waiting = False
                    if quit_rect.collidepoint((mx, my)):
                        self.exit_now()
                        waiting = False

    def apply_upgrade(self, upgrade):
        """Apply the selected upgrade to the player object."""
        if not hasattr(self, 'player') or not self.player:
            return
        if upgrade == "max_hearts":
            self.player.max_hearts = getattr(self.player, 'max_hearts', 100) + 10
            self.player.hearts = self.player.max_hearts
        elif upgrade == "attack_power":
            self.player.attack_power = getattr(self.player, 'attack_power', 1) + 1
        elif upgrade == "speed_mult":
            self.player.speed_mult = round(getattr(self.player, 'speed_mult', 1.0) + 0.1, 2)
        elif upgrade == "max_mana":
            self.player.max_mana = getattr(self.player, 'max_mana', 100) + 10
            self.player.mana = self.player.max_mana
        elif upgrade == "max_combo":
            self.player.max_combo = getattr(self.player, 'max_combo', 5) + 1
        # Optionally, play a sound or show a message here

    def __init__(self):
        # initialize game windows
        pg.init()
        pg.mixer.init()
        # Open a fullscreen, scaled window by default. Set the env var
        # ROBOTGAME_WINDOWED=1 to run in a normal windowed mode (useful for
        # developer testing so the display doesn't take over the monitor).
        if os.environ.get('ROBOTGAME_WINDOWED') == '1':
            self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        else:
            # Fullscreen + SCALED keeps logical WIDTH/HEIGHT while filling the screen
            self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN | pg.SCALED)
        # Finalize images (convert surfaces) now that a display exists
        try:
            finalize_images()
        except Exception:
            # If finalize_images isn't present or fails, continue without converting
            pass
        pg.display.set_caption("My Game")
        self.clock = pg.time.Clock()
        play_song('sounds/computer_startup.mp3')
        # Preload menu background(s).
        # Requirement: the start menu must use only start_background4 if present.
        # Also: other menus must NOT reuse existing image files from the images folder.
        # To satisfy that, we'll attempt to load `start_background4.png` for the start
        # screen, and we will generate simple procedural surfaces for the other menus
        # at runtime (so they are not reused from the images folder).
        self.start_backgrounds = []
        self.menu_backgrounds = []
        try:
            # Load only the explicit start background file if it's available.
            p = path.join(getattr(self, 'dir', '.'), 'images', 'start_background4.png')
            if os.path.exists(p):
                try:
                    img = pg.image.load(p).convert()
                    img = pg.transform.scale(img, (WIDTH, HEIGHT))
                    self.start_backgrounds.append(img)
                except Exception:
                    # If loading fails, fall back to generated start background below
                    pass

            # Procedurally generate a small set of medieval-themed menu backgrounds
            # (these are created in memory and do not rely on image files in the
            # repository). They provide visual variety for pause/level-complete/game-over.
            for i in range(3):
                surf = pg.Surface((WIDTH, HEIGHT)).convert()
                # Base color varies per index for subtle variety
                base = (40 + i * 20, 36 + i * 10, 48 + i * 15)
                surf.fill(base)

                # Draw a few simple castle/tower silhouettes
                tower_color = (30, 30, 30)
                tower_w = 80 + (i * 10)
                for t in range(4):
                    tx = 40 + t * (tower_w + 40) + (i * 8)
                    th = 180 + (t % 3) * 40 + (i * 10)
                    pg.draw.rect(surf, tower_color, (tx, HEIGHT - th - 40, tower_w, th))
                    # battlements
                    for b in range(4):
                        bx = tx + b * (tower_w // 4) + 6
                        pg.draw.rect(surf, (20, 20, 20), (bx, HEIGHT - th - 56, 12, 12))

                # Add small warm window dots for depth
                for wx in range(6):
                    wx_x = 60 + wx * 140 + (i * 6)
                    for wy in range(3):
                        wy_y = HEIGHT - 120 - wy * 50 - (i * 6)
                        pg.draw.rect(surf, (200, 170, 80), (wx_x, wy_y, 8, 16))

                # Dark vignette overlay to make menu text readable
                vign = pg.Surface((WIDTH, HEIGHT)).convert_alpha()
                vign.fill((0, 0, 0, 140))
                surf.blit(vign, (0, 0))

                self.menu_backgrounds.append(surf)
        except Exception:
            # In the unlikely event generation fails, ensure lists exist
            self.start_backgrounds = self.start_backgrounds or []
            self.menu_backgrounds = self.menu_backgrounds or []
        self.running = True
        self.paused = False
        # Flag to request a graceful quit from UI handlers (avoids sys.exit)
        self.should_exit = False
        self.font_name = pg.font.match_font(FONT_NAME)
        self.level = 1
        # Basic gameplay state defaults. These ensure methods like start_level
        # can be called even if `new()` wasn't invoked first (for example when
        # loading a saved game directly from the menu).
        self.score = 0
        self.kill_streak = 0
        self.max_streak = 0
        self.total_kills = 0
        self.accuracy_hits = 0
        self.accuracy_attempts = 0
        self.level_start_time = pg.time.get_ticks()
        self.time_bonus_active = True
        self.damage_taken_this_level = 0
        self.coin_count = 0
        # Flag used to ensure saved game is applied only once
        self.applied_saved_game = False
        self.load_data()

    def load_data(self):
        # load high score
        self.dir = path.dirname(__file__)
        try:
            with open(path.join(self.dir, hs_file), 'r') as f:
                self.highscore = int(f.read())
        except:
            self.highscore = 0
        # attempt to load a saved game (if present)
        try:
            self.loaded_save = self.load_game()
        except Exception:
            self.loaded_save = None

    def load_game(self):
        """Read savegame.json from the project dir and return the saved dict or None."""
        save_path = path.join(getattr(self, 'dir', '.'), 'savegame.json')
        try:
            with open(save_path, 'r') as f:
                data = json.load(f)
                # attach file mtime for display in menus
                try:
                    mtime = os.path.getmtime(save_path)
                    data['_mtime'] = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                except Exception:
                    data['_mtime'] = None
                return data
        except Exception:
            return None

    def new(self):
        # start new game
        self.score = 0
        self.kill_streak = 0  # Consecutive kills without taking damage
        self.max_streak = 0  # Track highest streak
        self.total_kills = 0  # Total enemies killed
        self.accuracy_hits = 0  # Successful hits
        self.accuracy_attempts = 0  # Total attacks (sword swings + fireballs)
        self.level_start_time = pg.time.get_ticks()  # Track level start time
        self.time_bonus_active = True  # Time bonus for completing levels quickly
        self.damage_taken_this_level = 0  # Track for perfect clear bonus
        self.coin_count = 0
        self.level = 1
        self.start_level()
    
    def start_level(self):
        # Start or restart a level
        # Clear arrays from previous level (but keep player in player_arr)
        goblins_arr.clear()
        coin_arr.clear()
        monster_arr.clear()
        skel_arr.clear()
        # Reset level timer and damage tracking
        self.level_start_time = pg.time.get_ticks()
        self.time_bonus_active = True
        self.damage_taken_this_level = 0  # Reset for perfect clear bonus
        # Get platforms for this level
        # If we have a loaded save, apply it once before generating platforms
        if getattr(self, 'loaded_save', None) and not getattr(self, 'applied_saved_game', False):
            try:
                self.level = int(self.loaded_save.get('level', self.level))
                self.score = int(self.loaded_save.get('score', getattr(self, 'score', 0)))
            except Exception:
                pass
            self.applied_saved_game = True
        get_level_platforms(self.level)
        
        self.all_sprites = pg.sprite.Group()
        self.player = Player(self)
        # Only add player to array if it's empty
        if len(player_arr) == 0:
            player_arr.append(self.player)
        else:
            player_arr[0] = self.player  # Update reference
        self.all_sprites.add(self.player)

        # If we applied a loaded save, restore player attributes (if present)
        if getattr(self, 'applied_saved_game', False) and getattr(self, 'loaded_save', None):
            pdata = self.loaded_save.get('player', {}) if isinstance(self.loaded_save, dict) else {}
            if pdata:
                try:
                    for attr in ('max_hearts', 'hearts', 'max_mana', 'mana', 'attack_power', 'speed_mult', 'max_combo'):
                        if attr in pdata:
                            try:
                                setattr(self.player, attr, pdata[attr])
                            except Exception:
                                pass
                except Exception:
                    pass
        self.platforms = pg.sprite.Group()
        self.lava = pg.sprite.Group()
        self.goblins = pg.sprite.Group()
        self.skeletons = pg.sprite.Group()
        self.monster = pg.sprite.Group()
        self.coins = pg.sprite.Group()
        self.fireballs = pg.sprite.Group()  # Fireball projectiles
        self.skeleton_arrows = pg.sprite.Group()
        self.hearts = pg.sprite.Group()  # Health pickups
        
        # Add monster only on every 5th level
        if self.level % 5 == 0:
            mon = Monster(self, WIDTH / 2, 30)
            self.monster.add(mon)
            self.all_sprites.add(mon)
            monster_arr.append(mon)
        else:
            # Mixed enemy spawns for variety - both goblins and skeletons from level 1
            total_enemies = min(8 + self.level * 2, 15)  # Scale up to 15 total
            
            # Progressive difficulty - enemies get faster every 3 levels
            difficulty_tier = (self.level - 1) // 3
            speed_boost = 1.0 + (difficulty_tier * 0.15)  # 15% faster per tier
            
            # Random mix ratio - more varied each level
            goblin_ratio = random.uniform(0.4, 0.7)  # 40-70% goblins
            num_goblins = int(total_enemies * goblin_ratio)
            num_skeletons = total_enemies - num_goblins
            
            # Spawn goblins
            for i in range(num_goblins):
                # 10% chance for elite (golden) goblin on level 3+
                is_elite = self.level >= 3 and random.random() < 0.1
                goblin = Goblin(self, is_elite=is_elite, speed_mult=speed_boost)
                self.all_sprites.add(goblin)
                self.goblins.add(goblin)
                goblins_arr.append(goblin)
            
            # Spawn skeletons (from level 1 now)
            for i in range(num_skeletons):
                # 10% chance for elite (golden) skeleton on level 3+
                is_elite = self.level >= 3 and random.random() < 0.1
                skeleton = Skeleton(self, is_elite=is_elite, speed_mult=speed_boost)
                self.all_sprites.add(skeleton)
                self.skeletons.add(skeleton)
                skel_arr.append(skeleton)

        for i in range(0, 4):
            self.coin_count += 1
            coin = Coin(self)
            self.all_sprites.add(coin)
            self.coins.add(coin)
            coin_arr.append(coin)
        
        # Spawn health hearts (2-3 per level)
        num_hearts = random.randint(2, 3)
        for i in range(num_hearts):
            heart = Heart(self)
            self.all_sprites.add(heart)
            self.hearts.add(heart)
        
        # Only create monster bullet if monster exists
        self.monsterbullet = pg.sprite.Group()
        if self.level % 5 == 0:
            bullet = MonsterBullet()
            self.all_sprites.add(bullet)
            self.monsterbullet.add(bullet)
        
        for plat in platform_arr:
            p = Platform(self, *plat)
            self.all_sprites.add(p)
            self.platforms.add(p)
        bottom_lava = Lava(0, HEIGHT - 40, 800, 20)
        self.all_sprites.add(bottom_lava)
        self.lava.add(bottom_lava)
        self.level_started = True  # Level is now ready for completion checking
        self.run()

    def run(self):
        # game loops
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def update(self):
        self.score += 1
        # Only spawn monster bullets if monster exists (every 5th level)
        if self.level % 5 == 0 and len(monster_arr) > 0:
            if self.score <= 1000:
                if self.score % 150 == 0:
                    self.all_sprites.add(MonsterBullet())
                    self.monsterbullet.add(MonsterBullet())
            elif self.score <= 1500:
                if self.score % 100 == 0:
                    self.all_sprites.add(MonsterBullet())
                    self.monsterbullet.add(MonsterBullet())
            elif self.score <= 2000:
                if self.score % 100 == 0:
                    self.all_sprites.add(MonsterBullet())
                    self.monsterbullet.add(MonsterBullet())
            else:
                if self.score % 25 == 0:
                    self.all_sprites.add(MonsterBullet())
                    self.monsterbullet.add(MonsterBullet())
        self.game_clock = pg.time.Clock()
        # game loop update
        self.all_sprites.update()
        
        # Check for sword attacks hitting goblins, skeletons, and monster
        if self.player.attacking:
            self.accuracy_attempts += 1  # Track attack attempt
            attack_rect = self.player.get_attack_rect()
            damage = self.player.get_attack_damage()
            hit_something = False
            if attack_rect:
                for goblin in self.goblins:
                    if attack_rect.colliderect(goblin.rect):
                        old_health = goblin.health
                        goblin.take_damage(damage)
                        hit_something = True
                        # Increment combo only on successful hit
                        self.player.increment_combo()
                        # Check if killed
                        if goblin.health <= 0 and old_health > 0:
                            self.total_kills += 1
                            self.kill_streak += 1
                            self.max_streak = max(self.max_streak, self.kill_streak)
                        # Scoring with elite bonus and high streak multiplier
                        base_score = 50
                        elite_mult = 3.0 if getattr(goblin, 'is_elite', False) else 1.0
                        combo_mult = self.player.attack_combo
                        streak_bonus = 1 + (self.kill_streak * 0.1)  # 10% bonus per streak
                        # Streak 10+ doubles all score
                        if self.kill_streak >= 10:
                            streak_bonus *= 2
                        self.score += int(base_score * elite_mult * combo_mult * streak_bonus)
                        
                for skeleton in self.skeletons:
                    if attack_rect.colliderect(skeleton.rect):
                        old_health = skeleton.health
                        skeleton.take_damage(damage)
                        hit_something = True
                        # Increment combo only on successful hit
                        self.player.increment_combo()
                        # Check if killed
                        if skeleton.health <= 0 and old_health > 0:
                            self.total_kills += 1
                            self.kill_streak += 1
                            self.max_streak = max(self.max_streak, self.kill_streak)
                        # Skeletons worth more with elite bonus
                        base_score = 75
                        elite_mult = 3.0 if getattr(skeleton, 'is_elite', False) else 1.0
                        combo_mult = self.player.attack_combo
                        streak_bonus = 1 + (self.kill_streak * 0.1)
                        # Streak 10+ doubles all score
                        if self.kill_streak >= 10:
                            streak_bonus *= 2
                        self.score += int(base_score * elite_mult * combo_mult * streak_bonus)
                        
                # Check for monster boss damage
                for monster in self.monster:
                    if attack_rect.colliderect(monster.rect):
                        old_health = monster.health
                        monster.take_damage(damage)
                        hit_something = True
                        # Increment combo only on successful hit
                        self.player.increment_combo()
                        # Check if killed
                        if monster.health <= 0 and old_health > 0:
                            self.total_kills += 1
                            self.kill_streak += 1
                            self.max_streak = max(self.max_streak, self.kill_streak)
                        # Boss worth most points
                        base_score = 100
                        combo_mult = self.player.attack_combo
                        streak_bonus = 1 + (self.kill_streak * 0.1)
                        self.score += int(base_score * combo_mult * streak_bonus)
                
                # Track accuracy
                if hit_something:
                    self.accuracy_hits += 1
        
        # Check fireball collisions with enemies
        for fireball in self.fireballs:
            self.accuracy_attempts += 1  # Track fireball cast
            hit_something = False
            
            # Check goblin hits
            hit_goblins = pg.sprite.spritecollide(fireball, self.goblins, False)
            for goblin in hit_goblins:
                old_health = goblin.health
                goblin.take_damage(3)  # Fireballs do 3 damage
                hit_something = True
                # Spawn explosion visual + splash damage (exclude the directly hit goblin)
                try:
                    exp = Explosion(self, fireball.rect.center, radius=48, damage=2, exclude_sprite=goblin)
                    self.all_sprites.add(exp)
                except Exception:
                    pass
                # Check if killed
                if goblin.health <= 0 and old_health > 0:
                    self.total_kills += 1
                    self.kill_streak += 1
                    self.max_streak = max(self.max_streak, self.kill_streak)
                # Fireball scoring with elite and streak bonus
                base_score = 75
                elite_mult = 3.0 if getattr(goblin, 'is_elite', False) else 1.0
                streak_bonus = 1 + (self.kill_streak * 0.1)
                if self.kill_streak >= 10:
                    streak_bonus *= 2
                self.score += int(base_score * elite_mult * streak_bonus)
                fireball.kill()
                break
            
            # Check skeleton hits
            hit_skeletons = pg.sprite.spritecollide(fireball, self.skeletons, False)
            for skeleton in hit_skeletons:
                old_health = skeleton.health
                skeleton.take_damage(3)  # Fireballs do 3 damage
                hit_something = True
                # Explosion effect (exclude direct target)
                try:
                    exp = Explosion(self, fireball.rect.center, radius=48, damage=2, exclude_sprite=skeleton)
                    self.all_sprites.add(exp)
                except Exception:
                    pass
                # Check if killed
                if skeleton.health <= 0 and old_health > 0:
                    self.total_kills += 1
                    self.kill_streak += 1
                    self.max_streak = max(self.max_streak, self.kill_streak)
                # Fireball scoring with elite and streak bonus
                base_score = 100
                elite_mult = 3.0 if getattr(skeleton, 'is_elite', False) else 1.0
                streak_bonus = 1 + (self.kill_streak * 0.1)
                if self.kill_streak >= 10:
                    streak_bonus *= 2
                self.score += int(base_score * elite_mult * streak_bonus)
                fireball.kill()
                break
            
            # Check monster boss hits
            hit_monsters = pg.sprite.spritecollide(fireball, self.monster, False)
            for monster in hit_monsters:
                old_health = monster.health
                monster.take_damage(3)  # Fireballs do 3 damage
                hit_something = True
                # Explosion effect for boss hit
                try:
                    exp = Explosion(self, fireball.rect.center, radius=64, damage=3, exclude_sprite=monster)
                    self.all_sprites.add(exp)
                except Exception:
                    pass
                # Check if killed
                if monster.health <= 0 and old_health > 0:
                    self.total_kills += 1
                    self.kill_streak += 1
                    self.max_streak = max(self.max_streak, self.kill_streak)
                # Fireball scoring with streak bonus
                base_score = 150
                streak_bonus = 1 + (self.kill_streak * 0.1)
                self.score += int(base_score * streak_bonus)
                fireball.kill()
                break
            
            # Track accuracy
            if hit_something:
                self.accuracy_hits += 1
        
        # Check if all enemies are dead - advance to next level
        # Only check after level has started (enemies have spawned)
        if self.level_started:
            # On boss levels, check monster; on normal levels, check goblins/skeletons
            if self.level % 5 == 0:
                # Boss level - check if monster is dead
                if len(self.monster) == 0 and len(monster_arr) == 0:
                    # Calculate time bonus/penalty
                    level_time = (pg.time.get_ticks() - self.level_start_time) / 1000  # seconds
                    if level_time < 60 and self.time_bonus_active:  # Under 60 seconds = bonus
                        time_bonus = int((60 - level_time) * 10)  # 10 points per second saved
                        self.score += time_bonus
                    elif level_time > 120:  # Over 2 minutes = penalty
                        time_penalty = int((level_time - 120) * 5)  # 5 points per second over
                        self.score = max(0, self.score - time_penalty)
                    # Perfect clear bonus - no damage taken
                    if self.damage_taken_this_level == 0:
                        self.score += 1000
                    # Regenerate 10 health between levels (respect player's max_hearts)
                    self.player.hearts = min(self.player.hearts + 10, getattr(self.player, 'max_hearts', 100))
                    self.level += 1
                    self.show_level_complete()
                    # If the player requested a graceful exit during the level-complete
                    # modal (Save & Quit / Quit), abort progression to the next level.
                    if getattr(self, 'should_exit', False):
                        return
                    # Show upgrade menu after every level
                    self.show_upgrade_screen()
                    if getattr(self, 'should_exit', False):
                        return
                    self.start_level()
            else:
                # Normal level - check if goblins and skeletons are dead
                if len(self.goblins) == 0 and len(goblins_arr) == 0 and len(self.skeletons) == 0 and len(skel_arr) == 0:
                    # Calculate time bonus/penalty
                    level_time = (pg.time.get_ticks() - self.level_start_time) / 1000  # seconds
                    if level_time < 45 and self.time_bonus_active:  # Under 45 seconds = bonus
                        time_bonus = int((45 - level_time) * 10)  # 10 points per second saved
                        self.score += time_bonus
                    elif level_time > 90:  # Over 90 seconds = penalty
                        time_penalty = int((level_time - 90) * 5)  # 5 points per second over
                        self.score = max(0, self.score - time_penalty)
                    # Perfect clear bonus - no damage taken
                    if self.damage_taken_this_level == 0:
                        self.score += 1000
                    # Regenerate 10 health between levels (respect player's max_hearts)
                    self.player.hearts = min(self.player.hearts + 10, getattr(self.player, 'max_hearts', 100))
                    self.level += 1
                    self.show_level_complete()
                    # If player asked to quit at level-complete, abort progression
                    if getattr(self, 'should_exit', False):
                        return
                    # Show upgrade menu after every level
                    self.show_upgrade_screen()
                    if getattr(self, 'should_exit', False):
                        return
                    # Show boss warning if next level is a boss level
                    if self.level % 5 == 0:
                        self.show_boss_warning()
                    if getattr(self, 'should_exit', False):
                        return
                    self.start_level()
        
        hits_lava = pg.sprite.spritecollide(self.player, self.lava, False)
        hits_bullet = pg.sprite.spritecollide(self.player, self.monsterbullet, False)
        # Check for arrow hits from skeletons
        hits_arrows = pg.sprite.spritecollide(self.player, self.skeleton_arrows, True) if hasattr(self, 'skeleton_arrows') else []
        hits_goblin = pg.sprite.spritecollide(self.player, self.goblins, False)
        # Check goblin attacks - must be attacking to damage
        goblin_attack_hit = False
        for goblin in hits_goblin:
            attack_rect = goblin.get_attack_rect()
            if attack_rect and self.player.rect.colliderect(attack_rect):
                goblin_attack_hit = True
                break
        hits_skeleton = pg.sprite.spritecollide(self.player, self.skeletons, False)
        # Check monster damage using the smaller damage_hitbox
        hits_monster = False
        for monster in self.monster:
            if self.player.rect.colliderect(monster.damage_hitbox):
                hits_monster = True
                break
        """hits_coin = pg.sprite.spritecollide(self.player, self.coins, False)
        hits_sword = pg.sprite.spritecollide(self.player, self.goblins, False)"""
        # DEATH
        if hits_lava:
            self.player.pos.y = hits_lava[0].rect.bottom
            self.player.vel.y = 0
            pg.mixer.music.stop()
            self.player.hearts -= 10
            self.damage_taken_this_level += 10
            self.kill_streak = 0  # Reset streak on damage
            if self.player.hearts < 0:
                lava_burning_sound.play()
                play_song('sounds/death_song.mp3')
                self.playing = False
        elif hits_bullet:
            self.player.hearts -= 5
            self.damage_taken_this_level += 5
            self.kill_streak = 0  # Reset streak on damage
            if self.player.hearts < 0:
                pg.mixer.music.stop()
                play_song('sounds/death_song.mp3')
                pg.time.wait(500)
                self.playing = False
        elif hits_arrows:
            # Arrows from skeletons hit the player
            # hits_arrows is a list of Arrow instances (removed on hit)
            total_damage = 0
            for arrow in hits_arrows:
                total_damage += getattr(arrow, 'damage', 4)
            self.player.hearts -= total_damage
            self.damage_taken_this_level += total_damage
            self.kill_streak = 0  # Reset streak on damage
            death_sound_HIT.play()
            if self.player.hearts < 0:
                pg.mixer.music.stop()
                play_song('sounds/death_song.mp3')
                pg.time.wait(500)
                self.playing = False
        elif goblin_attack_hit:
            # Goblin attack hit - only when goblin is attacking
            self.player.hearts -= 4
            self.damage_taken_this_level += 4
            self.kill_streak = 0  # Reset streak on damage
            death_sound_HIT.play()
            if self.player.hearts < 0:
                pg.mixer.music.stop()
                play_song('sounds/death_song.mp3')
                pg.time.wait(500)
                self.playing = False
        elif hits_skeleton:
            # Skeletons do more damage
            self.player.hearts -= 6
            self.damage_taken_this_level += 6
            self.kill_streak = 0  # Reset streak on damage
            death_sound_HIT.play()
            if self.player.hearts < 0:
                pg.mixer.music.stop()
                play_song('sounds/death_song.mp3')
                pg.time.wait(500)
                self.playing = False
        elif hits_monster:
            # Monster boss does heavy damage
            self.player.hearts -= 8
            self.damage_taken_this_level += 8
            self.kill_streak = 0  # Reset streak on damage
            death_sound_HIT.play()
            if self.player.hearts < 0:
                pg.mixer.music.stop()
                play_song('sounds/death_song.mp3')
                pg.time.wait(500)
                self.playing = False
        # Centralized death cleanup: when the player dies, remove any saved game
        # so the player is forced back to level 1 on next run, and clear the
        # in-memory loaded save so menus won't offer to continue it.
        if self.player.hearts < 0:
            try:
                save_path = path.join(getattr(self, 'dir', '.'), 'savegame.json')
                if os.path.exists(save_path):
                    os.remove(save_path)
            except Exception:
                pass
            # Clear loaded save and reset level so restart always begins at level 1
            self.loaded_save = None
            self.level = 1
        # check if player hits platform
        if self.player.vel.y > 0:
            hits_plat = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits_plat:
                # Use collision_rect if available, otherwise use rect
                plat_top = hits_plat[0].collision_rect.top if hasattr(hits_plat[0], 'collision_rect') else hits_plat[0].rect.top
                self.player.pos.y = plat_top
                self.player.vel.y = 0

    def events(self):
        # game loop events
        events = pg.event.get()
        for event in events:
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    # Toggle pause; if entering paused state, open the pause screen
                    self.paused = not self.paused
                    if self.paused:
                        self.show_pause_screen()
                # Jump mapped to SPACE or W/UP for convenience
                if not self.paused:
                    if event.key == pg.K_SPACE or event.key == pg.K_w or event.key == pg.K_UP:
                        try:
                            self.player.jump()
                        except Exception:
                            pass
            # Mouse buttons: left = sword attack, right = fireball
            if event.type == pg.MOUSEBUTTONDOWN and not self.paused:
                if event.button == 1:  # Left mouse button -> melee hit
                    try:
                        self.player.hit()
                    except Exception:
                        pass
                elif event.button == 3:  # Right mouse button -> cast fireball
                    mouse_pos = pg.mouse.get_pos()
                    fireball = self.player.cast_fireball(mouse_pos)
                    if fireball:
                        self.fireballs.add(fireball)
                        self.all_sprites.add(fireball)

    def draw(self):
        # game loop draw poop
        # self.screen.blit(game_background, (0, 0))
        self.screen.fill(BLACK)
        
        # Low health warning - red tint overlay
        if self.player.hearts < 25:
            overlay = pg.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(30)  # Semi-transparent
            overlay.fill((255, 0, 0))
            self.screen.blit(overlay, (0, 0))
        
        self.all_sprites.draw(self.screen)
        self.draw_text("LEVEL: " + str(self.level), 20, WHITE, WIDTH * 3 / 4 + 100, HEIGHT-22)
        self.draw_text("SCORE: " + str(self.score), 20, WHITE, WIDTH * 2 / 4 + 100, HEIGHT - 22)
        
        # Health text color changes based on amount
        health_color = WHITE
        if self.player.hearts < 25:
            health_color = RED
        elif self.player.hearts < 50:
            health_color = YELLOW
        self.draw_text("HEALTH: " + str(int(self.player.hearts)), 20, health_color, WIDTH * 1 / 4 + 100, HEIGHT - 22)
        
        # Draw kill streak if active
        if self.kill_streak > 1:
            streak_color = YELLOW if self.kill_streak < 5 else (255, 165, 0)  # Orange for high streaks
            self.draw_text("STREAK: " + str(self.kill_streak) + "x", 22, streak_color, WIDTH/2, 40)
        
        # Draw combo indicator if player is attacking with combo
        if self.player.attack_combo > 1 and self.player.attacking:
            combo_text = str(self.player.attack_combo) + "x COMBO!"
            self.draw_text(combo_text, 28, (255, 200, 0), WIDTH/2, 70)
        
        # Draw pause screen overlay
        if self.paused:
            # Semi-transparent overlay
            overlay = pg.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Pause text
            self.draw_text("PAUSED", 64, WHITE, WIDTH / 2, HEIGHT / 2 - 40)
            self.draw_text("Press ESC to Resume", 24, WHITE, WIDTH / 2, HEIGHT / 2 + 20)
        
        # Draw mana bar
        mana_bar_width = 150
        mana_bar_height = 15
        mana_bar_x = 10
        mana_bar_y = 10
        # Background
        pg.draw.rect(self.screen, (50, 50, 50), (mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height))
        # Mana (blue)
        mana_width = int((self.player.mana / self.player.max_mana) * mana_bar_width)
        pg.draw.rect(self.screen, (0, 100, 255), (mana_bar_x, mana_bar_y, mana_width, mana_bar_height))
        # Border
        pg.draw.rect(self.screen, (255, 255, 255), (mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height), 2)
        # Mana text
        self.draw_text("MANA: " + str(int(self.player.mana)), 16, WHITE, mana_bar_x + mana_bar_width + 50, mana_bar_y + 5)
        
        # Draw monster health bar on boss levels
        if self.level % 5 == 0 and len(monster_arr) > 0:
            monster_arr[0].draw_health_bar(self.screen)
        
        # self.draw_lives(self.screen, 5, HEIGHT - 5, self.player.lives, pright)
        # *after* drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        # Start/menu screen - present New / Load / Quit options (text-based)
        options = ["New Game", "Load Game", "Quit"]
        selected = 0
        # Play background music for menu
        try:
            play_song('sounds/uzi_music.mp3')
        except Exception:
            pass

        # Refresh loaded save each time we enter the menu so displayed info is current
        try:
            self.loaded_save = self.load_game()
        except Exception:
            self.loaded_save = None

        while True:
            self.clock.tick(FPS)
            # Poll events once per frame and reuse for both keyboard and mouse handling
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    self.running = False
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
                            if getattr(self, 'loaded_save', None):
                                try:
                                    confirmed = self.show_confirm_dialog("Start New Game", "A saved game exists. Start New Game and overwrite the save?", yes_text='Start New', no_text='Cancel')
                                except Exception:
                                    confirmed = False
                                if confirmed:
                                    try:
                                        save_path = path.join(getattr(self, 'dir', '.'), 'savegame.json')
                                        if os.path.exists(save_path):
                                            os.remove(save_path)
                                    except Exception:
                                        pass
                                    return 'new'
                            else:
                                return 'new'
                        if choice == 'Load Game':
                            # attempt to load save; if present, mark to apply and start
                            loaded = self.load_game()
                            if loaded:
                                self.loaded_save = loaded
                                # applied_saved_game will be set in start_level when applying
                                self.applied_saved_game = False
                                return 'load'
                            else:
                                # flash a "No Save" message for a short time
                                self.screen.fill(BLACK)
                                self.draw_text("No savegame found.", 28, WHITE, WIDTH/2, HEIGHT/2)
                                pg.display.flip()
                                pg.time.wait(1000)
                            if choice == 'quit':
                                try:
                                    self.exit_now()
                                except SystemExit:
                                    raise
                                except Exception:
                                    self.playing = False
                                    self.running = False
                                    waiting = False
            # draw start menu background (alternate between selected start backgrounds)
            self.draw_start_background()
            self.draw_text(TITLE, 48, GREEN, WIDTH/2, HEIGHT/6)

            # We'll support mouse hover/click: compute centers for each option
            option_x = WIDTH/2
            option_w = 400
            option_h = 32
            for i, opt in enumerate(options):
                oy = HEIGHT/2 + i * 40
                color = YELLOW if i == selected else WHITE
                self.draw_text(opt, 30, color, option_x, oy)

            # show save summary inline (under Load Game option) if present
            if getattr(self, 'loaded_save', None):
                try:
                    sd = self.loaded_save
                    lvl = sd.get('level', '?')
                    sc = sd.get('score', '?')
                    # place summary right under the Load Game option (index 1)
                    self.draw_text(f"Saved: Level {lvl}  Score {sc}", 18, WHITE, option_x, HEIGHT/2 + 40 + 20)
                except Exception:
                    pass

            # show hint
            self.draw_text("Use UP/DOWN, MOUSE or ENTER to choose", 18, WHITE, WIDTH/2, HEIGHT - 60)
            pg.display.flip()

            # handle simple mouse hover and click using the previously-polled events
            for ev in [e for e in events if e.type in (pg.MOUSEMOTION, pg.MOUSEBUTTONDOWN)]:
                if ev.type == pg.MOUSEMOTION:
                    mx, my = ev.pos
                    for i in range(len(options)):
                        oy = HEIGHT/2 + i * 40
                        if abs(mx - option_x) < option_w/2 and abs(my - oy) < option_h/2:
                            selected = i
                            break
                if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                    # treat left click as selecting the current hovered option
                    choice = options[selected]
                    # jump to selection handling by simulating Enter
                    if choice == 'New Game':
                        if getattr(self, 'loaded_save', None):
                            try:
                                confirmed = self.show_confirm_dialog("Start New Game", "A saved game exists. Start New Game and overwrite the save?", yes_text='Start New', no_text='Cancel')
                            except Exception:
                                confirmed = False
                            if confirmed:
                                try:
                                    save_path = path.join(getattr(self, 'dir', '.'), 'savegame.json')
                                    if os.path.exists(save_path):
                                        os.remove(save_path)
                                except Exception:
                                    pass
                                return 'new'
                        else:
                            return 'new'
                    if choice == 'Load Game':
                        loaded = self.load_game()
                        if loaded:
                            self.loaded_save = loaded
                            self.applied_saved_game = False
                            return 'load'
                        else:
                            self.screen.fill(BLACK)
                            self.draw_text("No savegame found.", 28, WHITE, WIDTH/2, HEIGHT/2)
                            pg.display.flip()
                            pg.time.wait(1000)
                    if choice == 'Quit':
                        try:
                            confirmed = self.show_confirm_dialog("Quit Game", "Are you sure you want to quit?")
                        except Exception:
                            confirmed = False
                        if confirmed:
                            self.running = False
                            return 'quit'

    def show_pause_screen(self):
        # game pause screen - modal loop until resume or quit
        # If a graceful exit was requested (user chose Quit/Save&Quit), skip
        # showing the game over screen. Otherwise always show Game Over so the
        # player sees their final score on death even if `self.running` was
        # toggled by other handlers.
        if getattr(self, 'should_exit', False):
            return
        # Draw pause overlay with clickable buttons
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            # Precompute button rects so they're available during event handling
            resume_rect = pg.Rect(WIDTH/2 - 150, HEIGHT/2 - 20, 140, 48)
            savequit_rect = pg.Rect(WIDTH/2 + 10, HEIGHT/2 - 20, 160, 48)
            quit_rect = pg.Rect(WIDTH/2 - 70, HEIGHT/2 + 50, 140, 48)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                    self.playing = False
                    self.paused = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        # Resume
                        self.paused = False
                        waiting = False
                    elif event.key == pg.K_s:
                        # Press 'S' to Save & Quit from pause
                        try:
                            choice = 'save'
                            try:
                                self.save_game()
                            except Exception:
                                pass
                            try:
                                self.exit_now()
                                waiting = False
                            except SystemExit:
                                raise
                            except Exception:
                                self.paused = False
                                self.playing = False
                                self.running = False
                                waiting = False
                        except Exception:
                            # If anything goes wrong, fall back to normal pause
                            pass
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if resume_rect.collidepoint((mx, my)):
                        self.paused = False
                        waiting = False
                    if savequit_rect.collidepoint((mx, my)):
                        # Offer the 3-way Save/Quit/Cancel modal
                        try:
                            choice = self.show_save_quit_dialog("Exit Game", "Do you want to save before quitting?")
                        except Exception:
                            choice = 'cancel'
                        if choice == 'save':
                            try:
                                self.save_game()
                            except Exception:
                                pass
                            # Ensure game exits after saving
                            try:
                                self.exit_now()
                                waiting = False
                            except SystemExit:
                                raise
                            except Exception:
                                # Fallback: set flags so outer loops stop
                                self.paused = False
                                self.playing = False
                                self.running = False
                                waiting = False
                        elif choice == 'quit':
                            try:
                                self.exit_now()
                            except SystemExit:
                                raise
                            except Exception:
                                self.paused = False
                                self.playing = False
                                self.running = False
                                waiting = False
                        else:
                            # cancel -> remain paused
                            pass
                    if quit_rect.collidepoint((mx, my)):
                        try:
                            choice = self.show_save_quit_dialog("Exit Game", "Do you want to save before quitting?")
                        except Exception:
                            choice = 'cancel'
                        if choice == 'save':
                            try:
                                self.save_game()
                            except Exception:
                                pass
                            try:
                                self.exit_now()
                                waiting = False
                            except SystemExit:
                                raise
                            except Exception:
                                self.paused = False
                                self.playing = False
                                self.running = False
                                waiting = False
                        elif choice == 'quit':
                            try:
                                self.exit_now()
                            except SystemExit:
                                raise
                            except Exception:
                                self.paused = False
                                self.playing = False
                                self.running = False
                                waiting = False

            # Draw overlay and pause text while waiting
            overlay = pg.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            self.draw_text("PAUSED", 64, WHITE, WIDTH / 2, HEIGHT / 2 - 120)
            # buttons
            self.draw_button("Resume", resume_rect, (80, 120, 200), (120, 160, 240), text_size=22)
            self.draw_button("Save & Quit", savequit_rect, (80, 160, 80), (120, 220, 120), text_size=20)
            self.draw_button("Quit", quit_rect, (160, 80, 80), (220, 120, 120), text_size=20)
            pg.display.flip()
    
    def show_level_complete(self):
            # Handle mouse clicks for buttons
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                    self.playing = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        waiting = False
                    if event.key == pg.K_s:
                        try:
                            self.save_game()
                        except Exception:
                            pass
                        try:
                            self.exit_now()
                            waiting = False
                        except SystemExit:
                            raise
                        except Exception:
                            self.playing = False
                            self.running = False
                            waiting = False
                    if event.key == pg.K_q:
                        try:
                            choice = self.show_save_quit_dialog("Exit Game", "Do you want to save before quitting?")
                        except Exception:
                            choice = 'cancel'
                        if choice == 'save':
                            try:
                                self.save_game()
                            except Exception:
                                pass
                            try:
                                self.exit_now()
                                waiting = False
                            except SystemExit:
                                raise
                            except Exception:
                                self.playing = False
                                self.running = False
                                waiting = False
                        if choice == 'quit':
                            try:
                                self.exit_now()
                                waiting = False
                            except SystemExit:
                                raise
                            except Exception:
                                self.playing = False
                                self.running = False
                                waiting = False
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if getattr(self, 'should_exit', False):
                        return
                    waiting = True
                    while waiting:
                        # create buttons: Continue, Save & Quit, Quit (define every frame)
                        cont_rect = pg.Rect(WIDTH/2 - 260, HEIGHT/2 + 120, 180, 48)
                        save_rect = pg.Rect(WIDTH/2 - 10, HEIGHT/2 + 120, 200, 48)
                        quit_rect = pg.Rect(WIDTH/2 + 220, HEIGHT/2 + 120, 160, 48)
                        self.clock.tick(FPS)
                        # Draw menu background and stats/buttons every frame
                        self.screen.fill(BLACK)
                        completed_level = max(1, self.level - 1)
                        self.draw_text("LEVEL " + str(completed_level) + " COMPLETE!", 56, GREEN, WIDTH/2, HEIGHT/2 - 120)
                        if self.damage_taken_this_level == 0:
                            self.draw_text("PERFECT CLEAR! +1000", 32, (255, 215, 0), WIDTH/2, HEIGHT/2 - 80)
                        self.draw_text("Level: " + str(completed_level), 26, WHITE, WIDTH/2, HEIGHT/2 - 50)
                        if self.max_streak > 0:
                            self.draw_text("Best Streak: " + str(self.max_streak) + "x", 24, YELLOW, WIDTH/2, HEIGHT/2 - 20)
                        if self.accuracy_attempts > 0:
                            accuracy = int((self.accuracy_hits / self.accuracy_attempts) * 100)
                            acc_color = GREEN if accuracy >= 70 else YELLOW if accuracy >= 50 else WHITE
                            self.draw_text("Accuracy: " + str(accuracy) + "%", 24, acc_color, WIDTH/2, HEIGHT/2 + 10)
                        self.draw_text("Enemies Defeated: " + str(self.total_kills), 24, WHITE, WIDTH/2, HEIGHT/2 + 40)
                        self.draw_text("Press ENTER for Level " + str(self.level), 26, WHITE, WIDTH/2, HEIGHT/2 + 40)
                        self.draw_button("Continue", cont_rect, (80, 120, 200), (120, 160, 240), text_size=18)
                        self.draw_button("Save & Quit", save_rect, (80, 160, 80), (120, 220, 120), text_size=16)
                        self.draw_button("Quit", quit_rect, (160, 80, 80), (220, 120, 120), text_size=16)
                        pg.display.flip()
                        for event in pg.event.get():
                            if event.type == pg.QUIT:
                                waiting = False
                                self.running = False
                                self.playing = False
                            if event.type == pg.KEYDOWN:
                                if event.key == pg.K_RETURN:
                                    waiting = False
                                if event.key == pg.K_s:
                                    try:
                                        self.save_game()
                                    except Exception:
                                        pass
                                    try:
                                        self.exit_now()
                                        waiting = False
                                    except SystemExit:
                                        raise
                                    except Exception:
                                        self.playing = False
                                        self.running = False
                                        waiting = False
                                if event.key == pg.K_q:
                                    try:
                                        choice = self.show_save_quit_dialog("Exit Game", "Do you want to save before quitting?")
                                    except Exception:
                                        choice = 'cancel'
                                    if choice == 'save':
                                        try:
                                            self.save_game()
                                        except Exception:
                                            pass
                                        try:
                                            self.exit_now()
                                            waiting = False
                                        except SystemExit:
                                            raise
                                        except Exception:
                                            self.playing = False
                                            self.running = False
                                            waiting = False
                                    if choice == 'quit':
                                        try:
                                            self.exit_now()
                                            waiting = False
                                        except SystemExit:
                                            raise
                                        except Exception:
                                            self.playing = False
                                            self.running = False
                                            waiting = False
                            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                                mx, my = event.pos
                                if cont_rect.collidepoint((mx, my)):
                                    waiting = False
                                elif save_rect.collidepoint((mx, my)):
                                    try:
                                        self.save_game()
                                    except Exception:
                                        pass
                                    try:
                                        self.exit_now()
                                        waiting = False
                                    except SystemExit:
                                        raise
                                    except Exception:
                                        self.playing = False
                                        self.running = False
                                        waiting = False
                                elif quit_rect.collidepoint((mx, my)):
                                    try:
                                        choice = self.show_save_quit_dialog("Exit Game", "Do you want to save before quitting?")
                                    except Exception:
                                        choice = 'cancel'
                                    if choice == 'save':
                                        try:
                                            self.save_game()
                                        except Exception:
                                            pass
                                        try:
                                            self.exit_now()
                                            waiting = False
                                        except SystemExit:
                                            raise
                                        except Exception:
                                            self.playing = False
                                            self.running = False
                                            waiting = False
                                    if choice == 'quit':
                                        try:
                                            self.exit_now()
                                            waiting = False
                                        except SystemExit:
                                            raise
                                        except Exception:
                                            self.playing = False
                                            self.running = False
                                            waiting = False
                                self.running = False
                                waiting = False
    
    def show_boss_warning(self):
        # Boss warning screen before boss levels
        if not self.running:
            return
        self.draw_menu_background()
        self.draw_text("BOSS FIGHT!", 70, RED, WIDTH/2, HEIGHT/2 - 80)
        self.draw_text("Level " + str(self.level), 40, YELLOW, WIDTH/2, HEIGHT/2 - 10)
        self.draw_text("Prepare yourself...", 30, WHITE, WIDTH/2, HEIGHT/2 + 50)
        self.draw_text("Press ENTER to begin", 25, WHITE, WIDTH/2, HEIGHT/2 + 100)
        pg.display.flip()
        pg.time.wait(1500)  # Show for 1.5 seconds
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                    self.playing = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        waiting = False

    def show_go_screen(self):
        # game over screen
        # Clear all arrays to prevent crashes on replay
        goblins_arr.clear()
        coin_arr.clear()
        player_arr.clear()
        monster_arr.clear()
        skel_arr.clear()
        reset_plat_list()
        if not self.running:
            return
        # Text-only Game Over screen (plain background)
        self.screen.fill(BLACK)
        # Space the game over text higher so buttons below do not overlap
        title_y = HEIGHT/2 - 80
        score_y = HEIGHT/2 - 20
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE!!!!!!", 40, GREEN, WIDTH/2, title_y)
            try:
                with open(path.join(self.dir, hs_file), 'w') as f:
                    f.write(str(self.score))
            except Exception:
                pass
        else:
            self.draw_text("HIGH SCORE:: " + str(self.highscore), 40, GREEN, WIDTH/2, title_y)
        self.draw_text("FINAL SCORE:: " + str(self.score), 40, GREEN, WIDTH/2, score_y)
        pg.display.flip()
        game_over_sound.stop()
        play_song('sounds/death_song.mp3')
        pg.mixer.music.unpause()
        # clickable options on Game Over screen
        # Precompute button rects so they exist when handling events
        # Move buttons further down and widen for readability
        # For Game Over there is nothing to save (player is dead) so present
        # Return to Menu and Quit options instead of Save & Quit.
        menu_rect = pg.Rect(WIDTH/2 - 120, HEIGHT/2 + 100, 240, 48)
        quit_rect = pg.Rect(WIDTH/2 + 160, HEIGHT/2 + 100, 160, 48)

        waiting = True
        while waiting:
            self.clock.tick(FPS)

            # draw background and buttons first (plain background)
            self.screen.fill(BLACK)
            if self.score > self.highscore:
                self.draw_text("NEW HIGH SCORE!!!!!!", 40, GREEN, WIDTH/2, title_y)
            else:
                self.draw_text("HIGH SCORE:: " + str(self.highscore), 40, GREEN, WIDTH/2, title_y)
            self.draw_text("FINAL SCORE:: " + str(self.score), 40, GREEN, WIDTH/2, score_y)

            # Buttons with hover colors
            mx, my = pg.mouse.get_pos()
            hovered_menu = menu_rect.collidepoint((mx, my))
            hovered_quit = quit_rect.collidepoint((mx, my))

            self.draw_button("Return to Menu", menu_rect, (80, 120, 200), (120, 160, 240), text_size=20)
            self.draw_button("Quit", quit_rect, (160, 80, 80), (220, 120, 120), text_size=18)

            # helpful hint
            self.draw_text("Press ENTER to return to menu, or Q/ESC to Quit", 18, WHITE, WIDTH/2, HEIGHT - 60)

            pg.display.flip()

            for ev in pg.event.get():
                if ev.type == pg.QUIT:
                    waiting = False
                    self.running = False
                    self.playing = False
                if ev.type == pg.KEYDOWN:
                    if ev.key == pg.K_RETURN:
                        # Return to menu
                        waiting = False
                    if ev.key == pg.K_q or ev.key == pg.K_ESCAPE:
                        try:
                            self.exit_now()
                            waiting = False
                        except SystemExit:
                            raise
                        except Exception:
                            self.playing = False
                            self.running = False
                            waiting = False
                if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                    mx, my = ev.pos
                    if menu_rect.collidepoint((mx, my)):
                        # Return to main menu
                        waiting = False
                    elif quit_rect.collidepoint((mx, my)):
                        try:
                            self.exit_now()
                            waiting = False
                        except SystemExit:
                            raise
                        except Exception:
                            self.playing = False
                            self.running = False
                            waiting = False

    def save_game(self):
        # Save minimal player/game state to a JSON file
        try:
            save = {
                'level': self.level,
                'score': self.score,
                'player': {
                    'max_hearts': getattr(self.player, 'max_hearts', 100),
                    'hearts': getattr(self.player, 'hearts', 100),
                    'max_mana': getattr(self.player, 'max_mana', 100),
                    'mana': getattr(self.player, 'mana', 100),
                    'attack_power': getattr(self.player, 'attack_power', 1),
                    'speed_mult': getattr(self.player, 'speed_mult', 1.0),
                    'max_combo': getattr(self.player, 'max_combo', 5)
                }
            }
            save_path = path.join(getattr(self, 'dir', '.'), 'savegame.json')
            with open(save_path, 'w') as f:
                json.dump(save, f, indent=2)
        except Exception as e:
            # If saving fails, print error but don't crash
            print('Failed to save game:', e)

    def exit_now(self):
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
            self.playing = False
            self.running = False
            self.should_exit = True
        except Exception:
            # If we can't set attributes for some reason, fallback to raising
            raise SystemExit(0)

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        play_song('sounds/uzi_music.mp3')
                        waiting = False
                    if event.key == pg.K_ESCAPE:
                        if self.playing:
                            self.playing = False
                        self.running = False
                        waiting = False

    def draw_text(self, text, size, colors, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, colors)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (int(x), int(y))
        self.screen.blit(text_surface, text_rect)

    def draw_button(self, text, rect, inactive_color, active_color, text_size=20):
        """Draw a rectangular button with centered text. Returns True if mouse is over it."""
        mx, my = pg.mouse.get_pos()
        hovered = rect.collidepoint((mx, my))
        color = active_color if hovered else inactive_color
        pg.draw.rect(self.screen, color, rect)
        # border
        pg.draw.rect(self.screen, WHITE, rect, 2)
        # draw label
        self.draw_text(text, text_size, WHITE, rect.centerx, rect.centery - (text_size // 2))
        return hovered

    def draw_menu_background(self):
        """Draw a rotating medieval menu background if available, otherwise fill black."""
        try:
            if getattr(self, 'menu_backgrounds', None) and len(self.menu_backgrounds) > 0:
                idx = (pg.time.get_ticks() // 3000) % len(self.menu_backgrounds)
                self.screen.blit(self.menu_backgrounds[idx], (0, 0))
                return
        except Exception:
            pass
        # fallback
        self.screen.fill(BLACK)

    def draw_start_background(self):
        """Draw the start screen background alternating between selected images."""
        try:
            if getattr(self, 'start_backgrounds', None) and len(self.start_backgrounds) > 0:
                # Strict: always use the first loaded start background (start_background4)
                try:
                    self.screen.blit(self.start_backgrounds[0], (0, 0))
                    return
                except Exception:
                    pass
        except Exception:
            pass
        # fallback: fill or procedurally generate (handled by caller if desired)
        self.screen.fill(BLACK)

    def show_confirm_dialog(self, title, message, yes_text='Yes', no_text='No'):
        """Show a modal confirmation dialog. Returns True if user confirms (Yes).

        This blocks until the user selects Yes or No, or closes the window.
        """
        if not getattr(self, 'running', True):
            return False

        # dialog layout
        w = 600
        h = 220
        rect = pg.Rect((WIDTH - w) // 2, (HEIGHT - h) // 2, w, h)
        yes_rect = pg.Rect(rect.left + 60, rect.bottom - 80, 140, 48)
        no_rect = pg.Rect(rect.right - 200, rect.bottom - 80, 140, 48)

        waiting = True
        confirmed = False
        while waiting and getattr(self, 'running', True):
            self.clock.tick(FPS)
            for ev in pg.event.get():
                if ev.type == pg.QUIT:
                    # treat window close as cancel but mark running False so outer loops exit
                    self.running = False
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

            # draw modal overlay
            overlay = pg.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            # dialog box
            pg.draw.rect(self.screen, (30, 30, 30), rect)
            pg.draw.rect(self.screen, WHITE, rect, 2)
            self.draw_text(title, 28, WHITE, rect.centerx, rect.top + 18)
            self.draw_text(message, 20, WHITE, rect.centerx, rect.top + 70)

            # buttons
            self.draw_button(yes_text, yes_rect, (80, 160, 80), (120, 220, 120), text_size=20)
            self.draw_button(no_text, no_rect, (160, 80, 80), (220, 120, 120), text_size=20)

            pg.display.flip()

        return bool(confirmed)
    
    def show_save_quit_dialog(self, title="Exit Game", message="Do you want to save before quitting?"):
        """Show a 3-way modal: Save & Quit, Quit without saving, Cancel.

        Returns one of: 'save', 'quit', 'cancel'.
        """
        if not getattr(self, 'running', True):
            return 'cancel'

        # layout
        w = 700
        h = 260
        rect = pg.Rect((WIDTH - w) // 2, (HEIGHT - h) // 2, w, h)
        save_rect = pg.Rect(rect.left + 40, rect.bottom - 86, 180, 56)
        quit_rect = pg.Rect(rect.centerx - 90, rect.bottom - 86, 180, 56)
        cancel_rect = pg.Rect(rect.right - 220, rect.bottom - 86, 180, 56)

        waiting = True
        result = 'cancel'
        while waiting and getattr(self, 'running', True):
            self.clock.tick(FPS)
            for ev in pg.event.get():
                if ev.type == pg.QUIT:
                    # Window close -> cancel but stop running
                    self.running = False
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

            # draw modal overlay
            overlay = pg.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            # dialog box
            pg.draw.rect(self.screen, (30, 30, 30), rect)
            pg.draw.rect(self.screen, WHITE, rect, 2)
            self.draw_text(title, 28, WHITE, rect.centerx, rect.top + 18)
            self.draw_text(message, 20, WHITE, rect.centerx, rect.top + 70)

            # buttons: Save, Quit, Cancel
            self.draw_button("Save & Quit", save_rect, (80, 160, 80), (120, 220, 120), text_size=20)
            self.draw_button("Quit", quit_rect, (200, 80, 80), (240, 120, 120), text_size=20)
            self.draw_button("Cancel", cancel_rect, (100, 100, 100), (160, 160, 160), text_size=20)

            # helpful hint
            self.draw_text("Press S to Save & Quit, Q to Quit without saving, or ESC to Cancel", 16, WHITE, rect.centerx, rect.bottom - 120)

            pg.display.flip()

        return result


g = Game()
while g.running:
    choice = g.show_start_screen()
    if not g.running:
        break
    if choice == 'load':
        # start using saved game
        if getattr(g, 'loaded_save', None):
            g.start_level()
        else:
            # fallback to new game if no save
            g.new()
    elif choice == 'new':
        g.new()
    else:
        break
    g.show_go_screen()

pg.quit()



