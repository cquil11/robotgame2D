# File I/O

#"python.analysis.extraPaths": ["C:\Users\harri\RobotGame"],
#"python.pythonPath": "/path/to/your/venv/bin/python",
import pygame as pg
from pygame.locals import *
import random
from settings import *
from sprites import *
from os import path
import time


class Game:

    def __init__(self):
        # initialize game windows
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("My Game")
        self.clock = pg.time.Clock()
        play_song('sounds/computer_startup.mp3')
        self.running = True
        self.paused = False
        self.font_name = pg.font.match_font(FONT_NAME)
        self.level = 1
        self.load_data()

    def load_data(self):
        # load high score
        self.dir = path.dirname(__file__)
        try:
            with open(path.join(self.dir, hs_file), 'r') as f:
                self.highscore = int(f.read())
        except:
            self.highscore = 0

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
        get_level_platforms(self.level)
        
        self.all_sprites = pg.sprite.Group()
        self.player = Player(self)
        # Only add player to array if it's empty
        if len(player_arr) == 0:
            player_arr.append(self.player)
        else:
            player_arr[0] = self.player  # Update reference
        self.all_sprites.add(self.player)
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
                    # Regenerate 10 health between levels
                    self.player.hearts = min(self.player.hearts + 10, 100)
                    self.level += 1
                    self.show_level_complete()
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
                    # Regenerate 10 health between levels
                    self.player.hearts = min(self.player.hearts + 10, 100)
                    self.level += 1
                    self.show_level_complete()
                    # Show boss warning if next level is a boss level
                    if self.level % 5 == 0:
                        self.show_boss_warning()
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
        for event in pg.event.get():

            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.paused = not self.paused
                if not self.paused:
                    if event.key == pg.K_UP:
                        self.player.jump()
                    if event.key == pg.K_w:
                        self.player.jump()
                    if event.key == pg.K_SPACE:
                        self.player.hit()
            if event.type == pg.MOUSEBUTTONDOWN and not self.paused:
                # Left click to cast fireball
                if event.button == 1:  # Left mouse button
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
        # game start screen
        start_screen_timer = pg.time.get_ticks()
        self.playing = True
        self.screen.blit(start_background2, (0, 0))
        """for bg in backgrounds:
            self.screen.blit(bg, (0, 0))
            pg.time.wait(1000)
            print(pg.time.get_ticks())
            # test"""
        play_song('sounds/uzi_music.mp3')
        pg.display.flip()
        self.wait_for_key()

    def show_pause_screen(self):
        # game pause screen
        pass
    
    def show_level_complete(self):
        # level complete screen
        if not self.running:
            return
        # Show themed level-complete background if available
        try:
            bg = pg.transform.scale(level_background, (WIDTH, HEIGHT))
            self.screen.blit(bg, (0, 0))
        except Exception:
            self.screen.fill(BLACK)

        completed_level = max(1, self.level - 1)
        # Main title
        self.draw_text("LEVEL " + str(completed_level) + " COMPLETE!", 56, GREEN, WIDTH/2, HEIGHT/2 - 120)
        
        # Perfect clear bonus indicator
        if self.damage_taken_this_level == 0:
            self.draw_text("PERFECT CLEAR! +1000", 32, (255, 215, 0), WIDTH/2, HEIGHT/2 - 80)
        
        # Level stats
        self.draw_text("Level: " + str(completed_level), 26, WHITE, WIDTH/2, HEIGHT/2 - 50)
        
        # Show max streak achieved
        if self.max_streak > 0:
            self.draw_text("Best Streak: " + str(self.max_streak) + "x", 24, YELLOW, WIDTH/2, HEIGHT/2 - 20)
        
        # Show accuracy if any attacks were made
        if self.accuracy_attempts > 0:
            accuracy = int((self.accuracy_hits / self.accuracy_attempts) * 100)
            acc_color = GREEN if accuracy >= 70 else YELLOW if accuracy >= 50 else WHITE
            self.draw_text("Accuracy: " + str(accuracy) + "%", 24, acc_color, WIDTH/2, HEIGHT/2 + 10)
        
        # Show total kills
        self.draw_text("Enemies Defeated: " + str(self.total_kills), 24, WHITE, WIDTH/2, HEIGHT/2 + 40)
        
        self.draw_text("Press ENTER for Level " + str(self.level), 26, WHITE, WIDTH/2, HEIGHT/2 + 80)
        pg.display.flip()
        pg.time.wait(2000)  # Show for 2 seconds
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                    self.playing = False
                if event.type == pg.KEYUP:
                    if event.key == pg.K_RETURN:
                        waiting = False
    
    def show_boss_warning(self):
        # Boss warning screen before boss levels
        if not self.running:
            return
        self.screen.fill(BLACK)
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
                if event.type == pg.KEYUP:
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
        self.screen.blit(end_background, (0, 0))
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE!!!!!!", 40, GREEN, WIDTH/2, HEIGHT/2 + 40)
            with open(path.join(self.dir, hs_file), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("HIGH SCORE:: " + str(self.highscore), 40, GREEN, WIDTH/2, HEIGHT/2 + 60)
        self.draw_text("FINAL SCORE:: " + str(self.score), 40, GREEN, WIDTH/2, HEIGHT/2)
        pg.display.flip()
        game_over_sound.stop()
        play_song('sounds/death_song.mp3')
        pg.mixer.music.unpause()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
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


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()



