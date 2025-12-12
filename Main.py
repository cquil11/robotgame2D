import pygame as pg
import random
import settings
from settings import WIDTH, HEIGHT, WINDOW_HEIGHT, FPS, FONT_NAME, hs_file, BLACK, WHITE, RED, GREEN, BLUE, YELLOW
from settings import goblins_arr, coin_arr, skel_arr, player_arr, monster_arr, reset_plat_list, get_level_platforms
from settings import PLAYER_ACC, PLAYER_FRICTION, PLAYER_GRAV, PLAYER_JUMP
from sprites import *
from os import path
import os
from datetime import datetime
import json
from upgrades import show_upgrade_screen
from ui_dialogs import show_boss_warning, show_go_screen, show_confirm_dialog, show_save_quit_dialog
from screens import show_start_screen, show_pause_screen, show_level_complete, draw_text, draw_button, draw_start_background
from game_utils import save_game, exit_now, wait_for_key


class Game:

    def __init__(self):
        # Windows-specific: Set taskbar icon FIRST (before pygame init)
        try:
            import ctypes
            myappid = 'robotgame.2d.adventure.1'  # Arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass  # Not Windows or ctypes unavailable
        
        # initialize game windows
        pg.init()
        pg.mixer.init()
        
        # Set custom window icon BEFORE creating the display
        try:
            # Use PNG for pygame (pygame doesn't support .ico files)
            icon = pg.image.load('images/sprites/player/player_right.png')
            pg.display.set_icon(icon)
        except Exception as e:
            print(f"Failed to load icon: {e}")
            pass  # If icon loading fails, use default
        
        # Open windowed mode with extra height for UI panel at the bottom
        # Use WINDOW_HEIGHT which includes the 80px UI panel
        self.screen = pg.display.set_mode((WIDTH, WINDOW_HEIGHT))
        
        # Finalize images (convert surfaces) now that a display exists
        try:
            finalize_images()
        except Exception:
            # If finalize_images isn't present or fails, continue without converting
            pass
        pg.display.set_caption("Crimson Knight")
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
            p = path.join(getattr(self, 'dir', '.'), 'images', 'backgrounds', 'start_background4.png')
            if os.path.exists(p):
                try:
                    img = pg.image.load(p).convert()
                    img = pg.transform.scale(img, (WIDTH, WINDOW_HEIGHT))
                    self.start_backgrounds.append(img)
                except Exception:
                    # If loading fails, fall back to generated start background below
                    pass

            # Procedurally generate a small set of medieval-themed menu backgrounds
            # (these are created in memory and do not rely on image files in the
            # repository). They provide visual variety for pause/level-complete/game-over.
            for i in range(3):
                surf = pg.Surface((WIDTH, WINDOW_HEIGHT)).convert()
                # Base color varies per index for subtle variety
                base = (40 + i * 20, 36 + i * 10, 48 + i * 15)
                surf.fill(base)

                # Draw a few simple castle/tower silhouettes
                tower_color = (30, 30, 30)
                tower_w = 80 + (i * 10)
                for t in range(4):
                    tx = 40 + t * (tower_w + 40) + (i * 8)
                    th = 180 + (t % 3) * 40 + (i * 10)
                    pg.draw.rect(surf, tower_color, (tx, WINDOW_HEIGHT - th - 40, tower_w, th))
                    # battlements
                    for b in range(4):
                        bx = tx + b * (tower_w // 4) + 6
                        pg.draw.rect(surf, (20, 20, 20), (bx, WINDOW_HEIGHT - th - 56, 12, 12))

                # Add small warm window dots for depth
                for wx in range(6):
                    wx_x = 60 + wx * 140 + (i * 6)
                    for wy in range(3):
                        wy_y = WINDOW_HEIGHT - 120 - wy * 50 - (i * 6)
                        pg.draw.rect(surf, (200, 170, 80), (wx_x, wy_y, 8, 16))

                # Dark vignette overlay to make menu text readable
                vign = pg.Surface((WIDTH, WINDOW_HEIGHT)).convert_alpha()
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
        # Delay after level complete before showing next screen (in ticks)
        self.level_complete_delay = 0
        self.level_complete_delay_max = 0
        # Screen shake effect for dramatic moments
        self.screen_shake_intensity = 0
        self.screen_shake_timer = 0
        self.screen_shake_max = 0
        self.load_data()

    def load_data(self):
        # load high score
        self.dir = path.dirname(path.abspath(__file__))
        if not self.dir or self.dir == '':
            self.dir = '.'
        try:
            with open(path.join(self.dir, hs_file), 'r') as f:
                self.highscore = int(f.read())
        except Exception:
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
        self.start_game()
    
    def start_game(self):
        """Initialize a fresh game with a new player at full health."""
        # Clear all enemy arrays
        goblins_arr.clear()
        coin_arr.clear()
        monster_arr.clear()
        skel_arr.clear()
        powerup_arr.clear()
        
        # Reset level timer and damage tracking
        self.level_start_time = pg.time.get_ticks()
        self.time_bonus_active = True
        self.damage_taken_this_level = 0
        
        # Generate platforms for current level
        get_level_platforms(self.level)
        
        # Create fresh player with default stats (no preservation)
        self.all_sprites = pg.sprite.Group()
        self.player = Player(self)
        
        # Initialize player array
        if len(player_arr) == 0:
            player_arr.append(self.player)
        else:
            player_arr[0] = self.player
        self.all_sprites.add(self.player)
        
        # If loading a saved game, restore saved stats
        if getattr(self, 'loaded_save', None) and not getattr(self, 'applied_saved_game', False):
            try:
                self.level = int(self.loaded_save.get('level', self.level))
                self.score = int(self.loaded_save.get('score', getattr(self, 'score', 0)))
            except Exception:
                pass
            self.applied_saved_game = True
            
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
        
        # Initialize sprite groups
        self.platforms = pg.sprite.Group()
        self.lava = pg.sprite.Group()
        self.goblins = pg.sprite.Group()
        self.skeletons = pg.sprite.Group()
        self.monster = pg.sprite.Group()
        self.coins = pg.sprite.Group()
        self.fireballs = pg.sprite.Group()
        self.skeleton_arrows = pg.sprite.Group()
        self.hearts = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.particles = pg.sprite.Group()
        
        # Spawn enemies and platforms for the level
        self._spawn_level_content()
    
    def start_level(self):
        """Start next level, preserving player stats and upgrades."""
        # Clear arrays from previous level
        goblins_arr.clear()
        coin_arr.clear()
        monster_arr.clear()
        skel_arr.clear()
        powerup_arr.clear()
        
        # Reset level timer and damage tracking
        self.level_start_time = pg.time.get_ticks()
        self.time_bonus_active = True
        self.damage_taken_this_level = 0
        
        # Generate platforms for new level
        get_level_platforms(self.level)
        
        # Preserve current player stats before recreating player
        prev_stats = None
        if hasattr(self, 'player') and getattr(self, 'player', None):
            try:
                prev_stats = {
                    'max_hearts': getattr(self.player, 'max_hearts', 100),
                    'hearts': getattr(self.player, 'hearts', 100),
                    'max_mana': getattr(self.player, 'max_mana', 100),
                    'mana': getattr(self.player, 'mana', 100),
                    'attack_power': getattr(self.player, 'attack_power', 1),
                    'speed_mult': getattr(self.player, 'speed_mult', 1.0),
                    'max_combo': getattr(self.player, 'max_combo', 5),
                }
            except Exception:
                prev_stats = None
        
        # Recreate player (resets position, state, etc.)
        self.all_sprites = pg.sprite.Group()
        self.player = Player(self)
        
        # Update player array
        if len(player_arr) == 0:
            player_arr.append(self.player)
        else:
            player_arr[0] = self.player
        self.all_sprites.add(self.player)

        # Restore preserved stats (upgrades persist across levels)
        if prev_stats:
            try:
                for attr, val in prev_stats.items():
                    setattr(self.player, attr, val)
                # Clamp hearts/mana to their maxima
                self.player.hearts = min(self.player.hearts, getattr(self.player, 'max_hearts', self.player.hearts))
                self.player.mana = min(self.player.mana, getattr(self.player, 'max_mana', self.player.mana))
            except Exception:
                pass
        
        # Reinitialize sprite groups
        self.platforms = pg.sprite.Group()
        self.lava = pg.sprite.Group()
        self.goblins = pg.sprite.Group()
        self.skeletons = pg.sprite.Group()
        self.monster = pg.sprite.Group()
        self.coins = pg.sprite.Group()
        self.fireballs = pg.sprite.Group()
        self.skeleton_arrows = pg.sprite.Group()
        self.hearts = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.particles = pg.sprite.Group()
        
        # Spawn enemies and platforms for the level
        self._spawn_level_content()
    
    def _spawn_level_content(self):
        """Spawn platforms, enemies, and items for the current level."""
        # Add monster only on every 5th level
        if self.level % 5 == 0:
            mon = Monster(self, WIDTH / 2, 30)
            self.monster.add(mon)
            self.all_sprites.add(mon)
            monster_arr.append(mon)
        else:
            # Mixed enemy spawns for variety - both goblins and skeletons from level 1
            # Enhanced dynamic difficulty scaling with easier early levels
            if self.level <= 2:
                total_enemies = 3 + random.randint(0, 1)  # Levels 1-2: 3-4 enemies (EASY)
            elif self.level <= 4:
                total_enemies = 5 + random.randint(0, 1)  # Levels 3-4: 5-6 enemies (NORMAL)
            elif self.level <= 6:
                total_enemies = 7 + random.randint(0, 1)  # Levels 5-6: 7-8 enemies (HARD)
            else:
                total_enemies = min(9 + (self.level - 6) * 1.5, 20)  # Level 7+: progressively harder
            
            # Progressive difficulty - enemies get faster every 3 levels
            difficulty_tier = (self.level - 1) // 3
            speed_boost = 1.0 + (difficulty_tier * 0.15)  # 15% faster per tier
            
            # Additional boost based on level parity (alternating harder/medium)
            if self.level % 2 == 0:
                speed_boost *= 1.1  # Even levels are 10% harder
                total_enemies = int(total_enemies * 1.05)  # 5% more enemies
            
            # Random mix ratio - more varied each level
            # Later levels have more skeletons (harder ranged enemies)
            skeleton_bias = min(0.7, 0.3 + (self.level * 0.05))  # Start 30%, up to 70%
            goblin_ratio = 1.0 - skeleton_bias
            num_goblins = int(total_enemies * goblin_ratio)
            num_skeletons = total_enemies - num_goblins
            
            # Spawn goblins
            for i in range(num_goblins):
                # Elite chance increases with level
                elite_chance = min(0.3, 0.05 + (self.level * 0.025))  # 5% at level 1, up to 30%
                is_elite = random.random() < elite_chance
                goblin = Goblin(self, is_elite=is_elite, speed_mult=speed_boost)
                self.all_sprites.add(goblin)
                self.goblins.add(goblin)
                goblins_arr.append(goblin)
            
            # Spawn skeletons (from level 1 now)
            for i in range(num_skeletons):
                # Elite chance increases with level
                elite_chance = min(0.3, 0.05 + (self.level * 0.025))  # 5% at level 1, up to 30%
                is_elite = random.random() < elite_chance
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
        
        for plat in settings.platform_arr:
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
        
        # Update screen shake effect
        if self.screen_shake_intensity > 0:
            self.screen_shake_timer -= 1
            if self.screen_shake_timer <= 0:
                self.screen_shake_intensity = max(0, self.screen_shake_intensity - 1)
                self.screen_shake_timer = self.screen_shake_max
        
        # Only spawn monster bullets if monster exists (every 5th level)
        if self.level % 5 == 0 and len(monster_arr) > 0:
            # Boss shoots more frequently as the level progresses
            if self.score <= 1000:
                if self.score % 80 == 0:  # More frequent (was 150)
                    # Sometimes aim at player, sometimes random spread
                    if random.random() < 0.6:
                        for _ in range(2):  # Shoot 2 bullets at once
                            bullet = MonsterBullet(target_pos=self.player.rect.center)
                            self.all_sprites.add(bullet)
                            self.monsterbullet.add(bullet)
                    else:
                        for _ in range(3):  # Or 3 bullets in random pattern
                            bullet = MonsterBullet()
                            self.all_sprites.add(bullet)
                            self.monsterbullet.add(bullet)
            elif self.score <= 1500:
                if self.score % 50 == 0:  # More frequent (was 100)
                    for _ in range(2):
                        bullet = MonsterBullet(target_pos=self.player.rect.center)
                        self.all_sprites.add(bullet)
                        self.monsterbullet.add(bullet)
            elif self.score <= 2000:
                if self.score % 40 == 0:  # More frequent (was 100)
                    for _ in range(2):
                        bullet = MonsterBullet(target_pos=self.player.rect.center)
                        self.all_sprites.add(bullet)
                        self.monsterbullet.add(bullet)
            else:
                # Late game: very frequent and aggressive
                if self.score % 15 == 0:  # Much more frequent (was 25)
                    for _ in range(3):  # 3 bullets at once
                        bullet = MonsterBullet(target_pos=self.player.rect.center)
                        self.all_sprites.add(bullet)
                        self.monsterbullet.add(bullet)
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
                    # Only hit each enemy once per attack
                    if attack_rect.colliderect(goblin.rect) and goblin not in getattr(self.player, 'hit_enemies_this_attack', set()):
                        if not hasattr(self.player, 'hit_enemies_this_attack'):
                            self.player.hit_enemies_this_attack = set()
                        self.player.hit_enemies_this_attack.add(goblin)
                        old_health = goblin.health
                        goblin.take_damage(damage)
                        hit_something = True
                        
                        # Screen shake on hit (more for heavy/critical)
                        shake_intensity = 2
                        if self.player.attack_type == 'heavy':
                            shake_intensity = 4
                        elif self.player.attack_type == 'critical':
                            shake_intensity = 5
                        self.trigger_screen_shake(shake_intensity, 3)
                        
                        # Knockback enemy based on hit direction
                        knockback_mult = 1.5 if self.player.attack_type == 'heavy' else 1.0
                        if self.player.attack_type == 'critical':
                            knockback_mult = 2.0
                        goblin.vx += (4 if self.player.facing_right else -4) * knockback_mult
                        
                        # Spawn particles on hit
                        for _ in range(5):
                            vx = random.uniform(-3, 3)
                            vy = random.uniform(-4, 2)
                            particle = Particle(self, goblin.rect.centerx, goblin.rect.centery, vx, vy, (255, 100, 0), lifetime=20, size=6)
                            self.all_sprites.add(particle)
                            self.particles.add(particle)
                        # Increment combo only on successful hit
                        self.player.increment_combo()
                        # Check if killed
                        if goblin.health <= 0 and old_health > 0:
                            self.total_kills += 1
                            self.kill_streak += 1
                            self.max_streak = max(self.max_streak, self.kill_streak)
                        # Scoring with elite bonus, attack type, and high streak multiplier
                        base_score = 50
                        elite_mult = 3.0 if getattr(goblin, 'is_elite', False) else 1.0
                        combo_mult = 1.0 + (self.player.attack_combo * 0.2)  # +20% per combo
                        # Attack type bonus
                        attack_type_mult = 1.0
                        if self.player.attack_type == 'heavy':
                            attack_type_mult = 1.5  # Heavy attacks give 1.5x score
                        elif self.player.attack_type == 'critical':
                            attack_type_mult = 2.0  # Critical attacks give 2x score
                        streak_bonus = 1 + (self.kill_streak * 0.1)  # 10% bonus per streak
                        # Streak 10+ doubles all score
                        if self.kill_streak >= 10:
                            streak_bonus *= 2
                        self.score += int(base_score * elite_mult * combo_mult * attack_type_mult * streak_bonus)
                        
                for skeleton in self.skeletons:
                    # Only hit each enemy once per attack
                    if attack_rect.colliderect(skeleton.rect) and skeleton not in getattr(self.player, 'hit_enemies_this_attack', set()):
                        if not hasattr(self.player, 'hit_enemies_this_attack'):
                            self.player.hit_enemies_this_attack = set()
                        self.player.hit_enemies_this_attack.add(skeleton)
                        old_health = skeleton.health
                        skeleton.take_damage(damage)
                        hit_something = True
                        
                        # Screen shake on hit (more for heavy/critical)
                        shake_intensity = 2
                        if self.player.attack_type == 'heavy':
                            shake_intensity = 4
                        elif self.player.attack_type == 'critical':
                            shake_intensity = 5
                        self.trigger_screen_shake(shake_intensity, 3)
                        
                        # Knockback enemy based on hit direction
                        knockback_mult = 1.5 if self.player.attack_type == 'heavy' else 1.0
                        if self.player.attack_type == 'critical':
                            knockback_mult = 2.0
                        skeleton.vx += (4 if self.player.facing_right else -4) * knockback_mult
                        
                        # Spawn particles on hit
                        for _ in range(5):
                            vx = random.uniform(-3, 3)
                            vy = random.uniform(-4, 2)
                            particle = Particle(self, skeleton.rect.centerx, skeleton.rect.centery, vx, vy, (200, 200, 200), lifetime=20, size=6)
                            self.all_sprites.add(particle)
                            self.particles.add(particle)
                        # Increment combo only on successful hit
                        self.player.increment_combo()
                        # Check if killed
                        if skeleton.health <= 0 and old_health > 0:
                            self.total_kills += 1
                            self.kill_streak += 1
                            self.max_streak = max(self.max_streak, self.kill_streak)
                        # Skeletons worth more with elite bonus and attack type bonus
                        base_score = 75
                        elite_mult = 3.0 if getattr(skeleton, 'is_elite', False) else 1.0
                        combo_mult = 1.0 + (self.player.attack_combo * 0.2)  # +20% per combo
                        # Attack type bonus
                        attack_type_mult = 1.0
                        if self.player.attack_type == 'heavy':
                            attack_type_mult = 1.5
                        elif self.player.attack_type == 'critical':
                            attack_type_mult = 2.0
                        streak_bonus = 1 + (self.kill_streak * 0.1)
                        # Streak 10+ doubles all score
                        if self.kill_streak >= 10:
                            streak_bonus *= 2
                        self.score += int(base_score * elite_mult * combo_mult * attack_type_mult * streak_bonus)
                        
                # Check for monster boss damage
                for monster in self.monster:
                    # Only hit each enemy once per attack
                    if attack_rect.colliderect(monster.rect) and monster not in getattr(self.player, 'hit_enemies_this_attack', set()):
                        if not hasattr(self.player, 'hit_enemies_this_attack'):
                            self.player.hit_enemies_this_attack = set()
                        self.player.hit_enemies_this_attack.add(monster)
                        old_health = monster.health
                        monster.take_damage(damage)
                        hit_something = True
                        # Spawn particles on hit (more for boss)
                        for _ in range(8):
                            vx = random.uniform(-5, 5)
                            vy = random.uniform(-5, 2)
                            particle = Particle(self, monster.rect.centerx, monster.rect.centery, vx, vy, (255, 0, 0), lifetime=20, size=8)
                            self.all_sprites.add(particle)
                            self.particles.add(particle)
                        # Increment combo only on successful hit
                        self.player.increment_combo()
                        # Check if killed
                        if monster.health <= 0 and old_health > 0:
                            self.total_kills += 1
                            self.kill_streak += 1
                            self.max_streak = max(self.max_streak, self.kill_streak)
                        # Boss worth most points with attack type bonus
                        base_score = 100
                        combo_mult = 1.0 + (self.player.attack_combo * 0.2)
                        # Attack type bonus (boss fights benefit heavily from critical hits)
                        attack_type_mult = 1.0
                        if self.player.attack_type == 'heavy':
                            attack_type_mult = 1.5
                        elif self.player.attack_type == 'critical':
                            attack_type_mult = 2.5  # Extra bonus for critical on boss
                        streak_bonus = 1 + (self.kill_streak * 0.1)
                        self.score += int(base_score * combo_mult * attack_type_mult * streak_bonus)
                
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
                    # Set delay to show particles before level complete (60 frames = ~1 second at 60 FPS)
                    if self.level_complete_delay_max == 0:
                        self.level_complete_delay_max = 60
                        self.level_complete_delay = 60
                    
                    self.level_complete_delay -= 1
                    if self.level_complete_delay <= 0:
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
                        self.level_complete_delay_max = 0
                        self.show_level_complete()
                        if getattr(self, 'should_exit', False):
                            return
                        show_upgrade_screen(self)
                        if getattr(self, 'should_exit', False):
                            return
                        self.start_level()
            else:
                # Normal level - check if goblins and skeletons are dead
                if len(self.goblins) == 0 and len(goblins_arr) == 0 and len(self.skeletons) == 0 and len(skel_arr) == 0:
                    # Set delay to show particles before level complete (60 frames = ~1 second at 60 FPS)
                    if self.level_complete_delay_max == 0:
                        self.level_complete_delay_max = 60
                        self.level_complete_delay = 60
                    
                    self.level_complete_delay -= 1
                    if self.level_complete_delay <= 0:
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
                        self.level_complete_delay_max = 0
                        self.show_level_complete()
                        if getattr(self, 'should_exit', False):
                            return
                        show_upgrade_screen(self)
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
        
        # Check for powerup pickups
        hits_powerups = pg.sprite.spritecollide(self.player, self.powerups, False)
        for powerup in hits_powerups:
            powerup.apply(self.player)
        
        # Check boss collision - boss can do damage
        hits_monster = False
        for monster in self.monster:
            if self.player.rect.colliderect(monster.rect):
                hits_monster = True
                break
        
        # Smooth collision prevention - realistic push between player and enemies
        for goblin in self.goblins:
            if self.player.rect.colliderect(goblin.rect):
                overlap = min(self.player.rect.right - goblin.rect.left, goblin.rect.right - self.player.rect.left)
                if overlap > 0:
                    half = overlap / 2.0
                    if self.player.rect.centerx <= goblin.rect.centerx:
                        # player on left: push left, goblin right
                        self.player.rect.right -= half
                        goblin.rect.left += half
                        # oppose motion for stability
                        if self.player.vel.x > 0:
                            self.player.vel.x *= 0.7
                        goblin.vx = max(getattr(goblin, 'vx', 0) * 0.7, 0)
                    else:
                        # player on right: push right, goblin left
                        self.player.rect.left += half
                        goblin.rect.right -= half
                        if self.player.vel.x < 0:
                            self.player.vel.x *= 0.7
                        goblin.vx = min(getattr(goblin, 'vx', 0) * 0.7, 0)
        
        for skeleton in self.skeletons:
            if self.player.rect.colliderect(skeleton.rect):
                overlap = min(self.player.rect.right - skeleton.rect.left, skeleton.rect.right - self.player.rect.left)
                if overlap > 0:
                    half = overlap / 2.0
                    if self.player.rect.centerx <= skeleton.rect.centerx:
                        self.player.rect.right -= half
                        skeleton.rect.left += half
                        if self.player.vel.x > 0:
                            self.player.vel.x *= 0.7
                        skeleton.vx = max(getattr(skeleton, 'vx', 0) * 0.7, 0)
                    else:
                        self.player.rect.left += half
                        skeleton.rect.right -= half
                        if self.player.vel.x < 0:
                            self.player.vel.x *= 0.7
                        skeleton.vx = min(getattr(skeleton, 'vx', 0) * 0.7, 0)
        
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
            # Remove bullets from game
            for bullet in hits_bullet:
                bullet.kill()
            # Shield blocks monster fireballs completely (no damage)
            if self.player.shield_active:
                # Shield successfully blocked the fireball
                pass
            else:
                # No shield - take reduced damage
                self.player.hearts -= 3  # Reduced from 5
                self.damage_taken_this_level += 3
                self.kill_streak = 0  # Reset streak on damage
                death_sound_HIT.play()
            if self.player.hearts < 0:
                pg.mixer.music.stop()
                play_song('sounds/death_song.mp3')
                pg.time.wait(500)
                self.playing = False
        elif hits_arrows:
            # Arrows from skeletons hit the player
            # hits_arrows is a list of Arrow instances (removed on hit)
            # Shield blocks arrows completely (no damage)
            if self.player.shield_active:
                # Shield successfully blocked all arrows
                pass
            else:
                # No shield - take damage
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
        elif hits_monster:
            # Monster boss does heavy damage on collision
            if not self.player.shield_active:
                self.player.hearts -= 8
                self.damage_taken_this_level += 8
                self.kill_streak = 0
                death_sound_HIT.play()
            else:
                self.player.shield_active = False
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
                # Fireball hotkeys (R or E keys)
                if not self.paused:
                    if event.key in (pg.K_r, pg.K_e):
                        mouse_pos = pg.mouse.get_pos()
                        fireball = self.player.cast_fireball(mouse_pos)
                        if fireball:
                            self.fireballs.add(fireball)
                            self.all_sprites.add(fireball)
            # Mouse buttons: left = sword attack, right = shield
            if event.type == pg.MOUSEBUTTONDOWN and not self.paused:
                if event.button == 1:  # Left mouse button -> melee hit
                    try:
                        self.player.hit()
                    except Exception:
                        pass
                elif event.button == 3:  # Right mouse button -> activate shield
                    try:
                        self.player.activate_shield()
                    except Exception:
                        pass

    def draw(self):
        # game loop draw
        # self.screen.blit(game_background, (0, 0))
        self.screen.fill(BLACK)
        
        # Calculate screen shake offset
        shake_offset_x = 0
        shake_offset_y = 0
        if self.screen_shake_intensity > 0:
            shake_offset_x = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            shake_offset_y = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
        
        # Low health warning - red tint overlay
        if self.player.hearts < 25:
            overlay = pg.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(30)  # Semi-transparent
            overlay.fill((255, 0, 0))
            self.screen.blit(overlay, (shake_offset_x, shake_offset_y))
        
        # Draw all sprites with shake offset
        for sprite in self.all_sprites:
            if hasattr(sprite, 'image') and hasattr(sprite, 'rect'):
                self.screen.blit(sprite.image, (sprite.rect.x + shake_offset_x, sprite.rect.y + shake_offset_y))
        
        # Draw enemy health bars
        for goblin in self.goblins:
            try:
                goblin.draw_health_bar(self.screen, shake_offset_x, shake_offset_y)
            except Exception:
                pass
        for skeleton in self.skeletons:
            try:
                skeleton.draw_health_bar(self.screen, shake_offset_x, shake_offset_y)
            except Exception:
                pass
        for monster in self.monster:
            try:
                monster.draw_health_bar(self.screen, shake_offset_x, shake_offset_y)
            except Exception:
                pass
        
        # Draw shield visual effect if active
        if self.player.shield_active:
            shield_radius = 45
            shield_alpha = int(80 + 60 * abs(pg.math.Vector2(0.5, 0).rotate(pg.time.get_ticks() * 0.5).x))
            shield_surface = pg.Surface((shield_radius * 2, shield_radius * 2), pg.SRCALPHA)
            pg.draw.circle(shield_surface, (100, 200, 255, shield_alpha), (shield_radius, shield_radius), shield_radius, 3)
            pg.draw.circle(shield_surface, (150, 220, 255, shield_alpha // 2), (shield_radius, shield_radius), shield_radius - 5, 2)
            self.screen.blit(shield_surface, (self.player.rect.centerx - shield_radius, self.player.rect.centery - shield_radius))
        
        # Draw bottom UI panel background (below the game area)
        ui_panel_height = 80
        ui_panel_y = HEIGHT  # Start at the game area boundary
        pg.draw.rect(self.screen, (0, 0, 0), (0, ui_panel_y, WIDTH, ui_panel_height))
        # Optional: draw a subtle border on top of the panel
        pg.draw.line(self.screen, (50, 50, 50), (0, ui_panel_y), (WIDTH, ui_panel_y), 2)
        
        # UI text positioned within the UI panel area - better spacing
        panel_y_base = HEIGHT + 25
        self.draw_text("SCORE: " + str(self.score), 20, WHITE, WIDTH / 2 - 80, panel_y_base)
        self.draw_text("LEVEL: " + str(self.level), 20, WHITE, WIDTH / 2 + 80, panel_y_base)
        
        # Draw difficulty indicator with better positioning
        difficulty_tier = (self.level - 1) // 3
        difficulty_names = ["EASY", "NORMAL", "HARD", "HARDER", "EXTREME", "NIGHTMARE"]
        difficulty_name = difficulty_names[min(difficulty_tier, len(difficulty_names) - 1)]
        difficulty_colors = [(100, 200, 100), (100, 100, 200), (200, 100, 100), (200, 50, 50), (200, 0, 200), (255, 0, 0)]
        difficulty_color = difficulty_colors[min(difficulty_tier, len(difficulty_colors) - 1)]
        self.draw_text("DIFFICULTY: " + difficulty_name, 18, difficulty_color, WIDTH / 2 - 80, panel_y_base + 30)
        
        # Draw health bar (bottom left, within UI panel)
        health_bar_width = 220
        health_bar_height = 24
        health_bar_x = 20
        health_bar_y = HEIGHT + 28
        # Background with rounded corners
        pg.draw.rect(self.screen, (30, 30, 35), (health_bar_x - 2, health_bar_y - 2, health_bar_width + 4, health_bar_height + 4), border_radius=3)
        pg.draw.rect(self.screen, (40, 40, 45), (health_bar_x, health_bar_y, health_bar_width, health_bar_height), border_radius=2)
        # Health fill (color based on health level with smooth gradient)
        health_percent = self.player.hearts / self.player.max_hearts
        if health_percent > 0.5:
            health_color = (50, 255, 50)  # Bright green
        elif health_percent > 0.25:
            health_color = (255, 220, 0)  # Bright yellow
        else:
            health_color = (255, 50, 50)  # Bright red
        health_width = int((health_percent) * health_bar_width)
        if health_width > 0:
            pg.draw.rect(self.screen, health_color, (health_bar_x + 1, health_bar_y + 1, health_width - 2, health_bar_height - 2), border_radius=1)
        # Ornate border matching health color
        pg.draw.rect(self.screen, health_color, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 3, border_radius=2)
        pg.draw.rect(self.screen, tuple(int(c * 0.6) for c in health_color), (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 1, border_radius=2)
        # Label and health text - positioned above bar to match mana/attack style
        self.draw_text("HP", 14, WHITE, health_bar_x + 30, health_bar_y - 18)
        health_text = f"{int(self.player.hearts)}/{int(self.player.max_hearts)}"
        self.draw_text(health_text, 14, health_color, health_bar_x + health_bar_width - 80, health_bar_y - 18)
        
        # Draw kill streak if active
        if self.kill_streak > 1:
            streak_color = YELLOW if self.kill_streak < 5 else (255, 165, 0)  # Orange for high streaks
            self.draw_text("STREAK: " + str(self.kill_streak) + "x", 24, streak_color, WIDTH/2, 40)
        
        # Draw powerup indicators below mana bar (left side, stacked)
        powerup_y = 60  # Below mana bar
        powerup_x = 25
        
        # Draw shield indicator if active or on cooldown
        if self.player.shield_active:
            shield_text = f"SHIELD ACTIVE: {self.player.shield_time // 30}s"
            self.draw_text(shield_text, 20, (100, 200, 255), WIDTH/2, 10)
        elif self.player.shield_cooldown > 0:
            cooldown_text = f"Shield CD: {self.player.shield_cooldown // 30}s"
            self.draw_text(cooldown_text, 16, (150, 150, 150), WIDTH - 100, 10)
        
        # Draw damage boost indicator if active
        if self.player.damage_boost_active:
            damage_text = f"DAMAGE x{self.player.damage_boost_mult}: {self.player.damage_boost_time // 10}s"
            self.draw_text(damage_text, 18, (255, 50, 50), powerup_x, powerup_y)
            powerup_y += 25
        
        # Draw speed boost indicator if active
        if self.player.speed_boost_active:
            speed_text = f"SPEED x{self.player.speed_mult_boost}: {self.player.speed_boost_time // 10}s"
            self.draw_text(speed_text, 18, (255, 200, 0), powerup_x, powerup_y)
            powerup_y += 25
        
        # Draw combo indicator if player is attacking with combo
        if self.player.attack_combo > 1 and self.player.attacking:
            combo_text = str(self.player.attack_combo) + "x COMBO!"
            self.draw_text(combo_text, 28, (255, 200, 0), WIDTH/2, 70)
        
        # Draw attack type indicator
        if self.player.attacking:
            attack_color = (255, 255, 255)  # White for normal
            if self.player.attack_type == 'heavy':
                attack_color = (255, 100, 100)  # Red for heavy
            elif self.player.attack_type == 'critical':
                attack_color = (255, 215, 0)  # Gold for critical
            attack_text = self.player.attack_type.upper() + " ATTACK!"
            self.draw_text(attack_text, 24, attack_color, WIDTH/2, 100)
        
        # Draw attack energy bar (top right)
        bar_width = 200
        bar_height = 24
        bar_x = WIDTH - bar_width - 20
        bar_y = 20
        # Background gradient effect with dark rounded corners
        pg.draw.rect(self.screen, (30, 30, 35), (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), border_radius=3)
        pg.draw.rect(self.screen, (40, 40, 45), (bar_x, bar_y, bar_width, bar_height), border_radius=2)
        # Energy fill with gradient color based on level
        energy_width = int((self.player.attack_energy / self.player.max_attack_energy) * bar_width)
        if energy_width > 0:
            # Use gradient colors: orange when low, yellow when high
            energy_percent = self.player.attack_energy / self.player.max_attack_energy
            if energy_percent < 0.33:
                fill_color = (200, 100, 0)
            elif energy_percent < 0.66:
                fill_color = (255, 140, 0)
            else:
                fill_color = (255, 180, 0)
            pg.draw.rect(self.screen, fill_color, (bar_x + 1, bar_y + 1, energy_width - 2, bar_height - 2), border_radius=1)
        # Ornate border
        pg.draw.rect(self.screen, (255, 200, 0), (bar_x, bar_y, bar_width, bar_height), 3, border_radius=2)
        pg.draw.rect(self.screen, (200, 150, 0), (bar_x, bar_y, bar_width, bar_height), 1, border_radius=2)
        # Label and stats - positioned above bar with better spacing
        self.draw_text("ATTACK", 14, (255, 180, 0), bar_x + 30, bar_y - 18)
        energy_text = f"{int(self.player.attack_energy)}/{int(self.player.max_attack_energy)}"
        self.draw_text(energy_text, 14, (255, 180, 0), bar_x + bar_width - 80, bar_y - 18)
        
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
        mana_bar_width = 180
        mana_bar_height = 24
        mana_bar_x = 20
        mana_bar_y = 20
        # Background gradient effect with dark rounded corners
        pg.draw.rect(self.screen, (30, 30, 40), (mana_bar_x - 2, mana_bar_y - 2, mana_bar_width + 4, mana_bar_height + 4), border_radius=3)
        pg.draw.rect(self.screen, (40, 40, 50), (mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height), border_radius=2)
        # Mana fill with gradient color based on level
        mana_width = int((self.player.mana / self.player.max_mana) * mana_bar_width)
        if mana_width > 0:
            # Use gradient colors: dark blue when low, bright cyan when high
            mana_percent = self.player.mana / self.player.max_mana
            if mana_percent < 0.33:
                mana_color = (0, 80, 200)
            elif mana_percent < 0.66:
                mana_color = (0, 150, 255)
            else:
                mana_color = (0, 200, 255)
            pg.draw.rect(self.screen, mana_color, (mana_bar_x + 1, mana_bar_y + 1, mana_width - 2, mana_bar_height - 2), border_radius=1)
        # Ornate border
        pg.draw.rect(self.screen, (0, 180, 255), (mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height), 3, border_radius=2)
        pg.draw.rect(self.screen, (0, 120, 200), (mana_bar_x, mana_bar_y, mana_bar_width, mana_bar_height), 1, border_radius=2)
        # Label and stats - positioned above bar like attack bar
        self.draw_text("MANA", 14, (100, 180, 255), mana_bar_x + 30, mana_bar_y - 18)
        mana_text = f"{int(self.player.mana)}/{int(self.player.max_mana)}"
        self.draw_text(mana_text, 14, (0, 200, 255), mana_bar_x + mana_bar_width - 80, mana_bar_y - 18)
        
        # Draw monster health bar on boss levels
        if self.level % 5 == 0 and len(monster_arr) > 0:
            monster_arr[0].draw_health_bar(self.screen)
        
        # self.draw_lives(self.screen, 5, HEIGHT - 5, self.player.lives, pright)
        # *after* drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        return show_start_screen(self)

    def show_pause_screen(self):
        return show_pause_screen(self)
    
    def show_level_complete(self):
        return show_level_complete(self)
    
    def show_boss_warning(self):
        return show_boss_warning(self)

    def show_go_screen(self):
        return show_go_screen(self)

    def save_game(self):
        return save_game(self)

    def exit_now(self):
        return exit_now(self)

    def wait_for_key(self):
        return wait_for_key(self)

    def draw_text(self, text, size, colors, x, y):
        return draw_text(self, text, size, colors, x, y)

    def draw_button(self, text, rect, inactive_color, active_color, text_size=20):
        return draw_button(self, text, rect, inactive_color, active_color, text_size=text_size)

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

    def trigger_screen_shake(self, intensity, duration_frames):
        """Trigger a screen shake effect with given intensity and duration"""
        self.screen_shake_intensity = intensity
        self.screen_shake_timer = duration_frames
        self.screen_shake_max = duration_frames

    def draw_start_background(self):
        return draw_start_background(self)

    def show_confirm_dialog(self, title, message, yes_text='Yes', no_text='No'):
        return show_confirm_dialog(self, title, message, yes_text=yes_text, no_text=no_text)
    
    def show_save_quit_dialog(self, title="Exit Game", message="Do you want to save before quitting?"):
        return show_save_quit_dialog(self, title=title, message=message)


# Start the game
g = Game()
while g.running:
    choice = g.show_start_screen()
    if not g.running:
        break
    if choice == 'load':
        # start using saved game
        if getattr(g, 'loaded_save', None):
            g.start_game()  # Use start_game which handles loading
        else:
            # fallback to new game if no save
            g.new()
    elif choice == 'new':
        g.new()
    else:
        break
    g.show_go_screen()

pg.quit()