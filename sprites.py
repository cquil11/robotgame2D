# player and enemy classes for game
import settings
from settings import WIDTH, HEIGHT, LEVEL_WIDTH, FPS, FONT_NAME, hs_file, BLACK, WHITE, RED, GREEN, BLUE, YELLOW
from settings import goblins_arr, coin_arr, skel_arr, player_arr, monster_arr
from settings import PLAYER_ACC, PLAYER_FRICTION, PLAYER_GRAV, PLAYER_JUMP
from settings import platform_layer, lava_layer, player_layer, mob_layer, coin_layer, projectile_layer, monster_layer, particle_layer, powerup_layer
from settings import pleft, pright, pleftj, prightj, plefth, prighth
from settings import attack_normal_right, attack_normal_left, attack_critical_right, attack_critical_left
from settings import attack_heavy_right, attack_heavy_left
from settings import gleft, gright, sleft, sright
from settings import monster_scary, arrow_skeleton, platform_image, lava, coin, heart_image
from settings import game_over_sound, death_sound, jump_sound, death_sound_HIT, lava_burning_sound, sword_swing
from settings import scream_sound, coin_sound, explosion_sound, goblin_death_sound, skeleton_death_sound
from settings import play_song, songs
import pygame as pg
import random
import math
from os import path

vec = pg.math.Vector2


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self._layer = player_layer
        self.image = pleft
        self.rect = self.image.get_rect()
        # Player stats (make several values configurable/upgradable)
        self.max_hearts = 100
        self.hearts = float(self.max_hearts)
        self.max_mana = 100
        self.mana = 100  # Mana system
        self.max_combo = 5
        self.attack_power = 1
        self.speed_mult = 1.0
        # Start player on the left side for scrolling levels
        self.pos = vec(200, HEIGHT / 2)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.lives = 3
        self.attacking = False
        self.attack_timer = 0
        self.facing_right = False
        self.attack_frame = 0  # Current animation frame
        self.attack_frame_timer = 0  # Timer for frame advancement
        self.attack_combo = 0  # Track combo hits
        self.last_attack_time = 0  # Track time for combo window
        # Attack energy system for charge attacks
        self.attack_energy = 0  # Builds up over time during attack stance
        self.max_attack_energy = 100
        self.attack_energy_regen = 3.0  # Builds up during charging
        self.attack_type = 'normal'  # 'normal', 'heavy', 'critical'
        self.charge_timer = 0  # Tracks charge time for heavy attacks
        self.consecutive_hits = 0  # Tracks hits in current combo
        # Mana settings
        self.mana_regen_rate = 0.2  # Mana per frame
        self.fireball_cost = 15  # Cost to cast fireball (reduced for balance)
        self.fireball_cooldown = 0  # Cooldown timer
        # Powerup effects
        self.shield_active = False
        self.shield_time = 0
        self.damage_boost_active = False
        self.damage_boost_time = 0
        self.damage_boost_mult = 1.0
        self.speed_boost_active = False
        self.speed_boost_time = 0
        self.speed_mult_boost = 1.0
        # Manual shield activation
        self.shield_max_duration = 90  # 3 seconds at 30 FPS
        self.shield_cooldown = 0
        self.shield_cooldown_max = 180  # 6 seconds cooldown
        # New advanced mechanics (unlocked at level 5)
        self.double_jump_available = False  # Starts at level 5
        self.air_dash_available = False    # Starts at level 8
        self.ground_pound_available = False  # Starts at level 10
        self.double_jump_count = 0  # Track double jumps (0 = ground, 1 = used)
        self.air_dash_cooldown = 0  # Cooldown between dashes
        self.ground_pound_charging = False
        self.ground_pound_timer = 0

    def jump(self):
        # only jump if on platform
        self.rect.y += 1
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 1
        if hits:
            jump_sound.play()
            self.vel.y = PLAYER_JUMP
            self.image = pright
            self.double_jump_count = 0  # Reset double jump when landing

    def double_jump(self):
        """Double jump - jump again while in air (unlocked at level 5)"""
        if self.double_jump_available and self.double_jump_count == 0:
            jump_sound.play()
            self.vel.y = PLAYER_JUMP * 0.85  # Slightly less powerful than ground jump
            self.double_jump_count = 1
            self.image = pright

    def air_dash(self, direction):
        """Air dash - dash horizontally while in air (unlocked at level 8)"""
        if self.air_dash_available and self.air_dash_cooldown <= 0:
            # Dash speed
            dash_speed = 12
            self.vel.x = dash_speed * direction
            self.air_dash_cooldown = 20  # Cooldown between dashes (20 frames = 0.67s)
            # Visual feedback - play jump sound
            jump_sound.play()

    def ground_pound(self):
        """Ground pound - jump and slam down for damage (unlocked at level 10)"""
        if self.ground_pound_available and not self.ground_pound_charging:
            self.ground_pound_charging = True
            self.ground_pound_timer = 15  # Charge time
            # Jump upward for pound
            self.vel.y = PLAYER_JUMP * 1.2

    def do_ground_pound_slam(self):
        """Execute the ground pound slam"""
        # Damage all enemies in range
        slam_radius = 80
        slam_damage = 3
        
        # Check collision with enemies
        for goblin in self.game.goblins:
            dist = math.sqrt((goblin.rect.centerx - self.rect.centerx)**2 + 
                           (goblin.rect.centery - self.rect.centery)**2)
            if dist < slam_radius:
                goblin.take_damage(slam_damage)
                # Knockback effect
                goblin.vel.y = -10
                goblin.vel.x = (goblin.rect.centerx - self.rect.centerx) / 10
        
        for skeleton in self.game.skeletons:
            dist = math.sqrt((skeleton.rect.centerx - self.rect.centerx)**2 + 
                           (skeleton.rect.centery - self.rect.centery)**2)
            if dist < slam_radius:
                skeleton.take_damage(slam_damage)
                # Knockback effect
                skeleton.vel.y = -10
                skeleton.vel.x = (skeleton.rect.centerx - self.rect.centerx) / 10
        
        # Knockback player slightly upward
        self.vel.y = -8
        explosion_sound.play()

    def hit(self):
        sword_swing.play()
        current_time = pg.time.get_ticks()
        
        # Don't increment combo here - only on successful hit
        # Store last attack time for combo window tracking
        self.last_attack_time = current_time
        self.attacking = True
        
        # Reset animation
        self.attack_frame = 0
        self.attack_frame_timer = 0
        
        # Determine attack type based on charge level
        if self.charge_timer >= 20:  # Charged heavy attack
            self.attack_type = 'heavy'
            self.attack_timer = 10  # Reduced from 16
        elif self.consecutive_hits >= 4:  # Critical after 4+ hits
            self.attack_type = 'critical'
            self.attack_timer = 8  # Reduced from 14
        else:
            self.attack_type = 'normal'
            self.attack_timer = 6  # Reduced from 10
        
        self.charge_timer = 0  # Reset charge after attacking
        
        if self.image == pright or self.facing_right:
            self.image = prighth
            self.facing_right = True
        else:
            self.image = plefth
            self.facing_right = False
    
    def increment_combo(self):
        """Called when an attack successfully hits an enemy"""
        current_time = pg.time.get_ticks()
        # Check for combo (hit within 1 second of last attack)
        if current_time - self.last_attack_time < 1000:
            self.attack_combo = min(self.attack_combo + 1, self.max_combo)
            self.consecutive_hits = min(self.consecutive_hits + 1, 10)
        else:
            self.attack_combo = 1  # Reset combo
            self.consecutive_hits = 1
        
        # Regenerate some attack energy on successful hits
        self.attack_energy = min(self.attack_energy + 20, self.max_attack_energy)

    def update(self):
        # Handle attack timer
        if self.attacking:
            # Update attack animation frames
            self.attack_frame_timer += 1
            
            # Determine frame count and speed based on attack type
            if self.attack_type == 'heavy':
                total_frames = 4
                frames_per_frame = 3  # Slower, more impactful
            else:  # normal or critical
                total_frames = 3
                frames_per_frame = 2  # Faster attacks
            
            # Advance to next frame
            if self.attack_frame_timer >= frames_per_frame:
                self.attack_frame_timer = 0
                self.attack_frame += 1
                if self.attack_frame >= total_frames:
                    self.attack_frame = total_frames - 1  # Stay on last frame
            
            # Set the appropriate animation frame
            if self.attack_type == 'heavy':
                frames = attack_heavy_right if self.facing_right else attack_heavy_left
            elif self.attack_type == 'critical':
                frames = attack_critical_right if self.facing_right else attack_critical_left
            else:  # normal
                frames = attack_normal_right if self.facing_right else attack_normal_left
            
            if self.attack_frame < len(frames):
                self.image = frames[self.attack_frame]
            
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attacking = False        # Update powerup timers
        if self.shield_active:
            self.shield_time -= 1
            if self.shield_time <= 0:
                self.shield_active = False
        
        if self.damage_boost_active:
            self.damage_boost_time -= 1
            if self.damage_boost_time <= 0:
                self.damage_boost_active = False
        
        if self.speed_boost_active:
            self.speed_boost_time -= 1
            if self.speed_boost_time <= 0:
                self.speed_boost_active = False
        
        # Regenerate attack energy when not attacking
        if not self.attacking and self.attack_energy < self.max_attack_energy:
            self.attack_energy = min(self.attack_energy + self.attack_energy_regen, self.max_attack_energy)
        
        # Regenerate mana
        if self.mana < self.max_mana:
            self.mana = min(self.mana + self.mana_regen_rate, self.max_mana)
        
        # Fireball cooldown
        if self.fireball_cooldown > 0:
            self.fireball_cooldown -= 1
        
        # Shield cooldown
        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1
        
        # Reset consecutive hits if not attacking for more than 1.5 seconds
        if pg.time.get_ticks() - self.last_attack_time > 1500:
            self.consecutive_hits = 0
        
        # ATTACK ANIMATION TAKES PRECEDENCE - only update movement if not attacking
        if not self.attacking:
            self.acc = vec(0, PLAYER_GRAV)
            keys = pg.key.get_pressed()
            if keys[pg.K_LEFT] | keys[pg.K_a]:
                # Apply player's speed multiplier and speed boost
                speed_multiplier = self.speed_mult * self.speed_mult_boost if self.speed_boost_active else self.speed_mult
                self.acc.x = -PLAYER_ACC * speed_multiplier
                self.facing_right = False
                if self.vel.y >= 0:
                    self.image = pleft
                if self.vel.y < 0:
                    self.image = pleftj
            if keys[pg.K_RIGHT] | keys[pg.K_d]:
                # Apply player's speed multiplier and speed boost
                speed_multiplier = self.speed_mult * self.speed_mult_boost if self.speed_boost_active else self.speed_mult
                self.acc.x = PLAYER_ACC * speed_multiplier
                self.facing_right = True
                if self.vel.y >= 0:
                    self.image = pright
                if self.vel.y < 0:
                    self.image = prightj

            # slows player down over time
            self.acc.x += self.vel.x * PLAYER_FRICTION
        else:
            # While attacking, reduce horizontal acceleration to maintain momentum but not add new movement
            self.acc = vec(0, PLAYER_GRAV)
            self.acc.x = self.vel.x * PLAYER_FRICTION
        
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # Clamp to level boundaries instead of wrapping
        from settings import LEVEL_WIDTH
        if self.pos.x > LEVEL_WIDTH:
            self.pos.x = LEVEL_WIDTH
        if self.pos.x < 0:
            self.pos.x = 0

        self.rect.midbottom = self.pos
    
    def cast_fireball(self, target_pos):
        """Cast a fireball toward the target position (mouse cursor)"""
        if self.mana >= self.fireball_cost and self.fireball_cooldown == 0:
            self.mana -= self.fireball_cost
            self.fireball_cooldown = 30  # 1 second cooldown at 30 FPS
            return Fireball(self.game, self.rect.center, target_pos)
        return None
    
    def activate_shield(self):
        """Activate shield to block projectiles and reduce damage"""
        if self.shield_cooldown == 0 and not self.shield_active:
            self.shield_active = True
            self.shield_time = self.shield_max_duration
            self.shield_cooldown = self.shield_cooldown_max
            return True
        return False
    
    def get_attack_rect(self):
        """Returns the hitbox for sword attack - width matches player model"""
        if not self.attacking:
            return None
        
        # Attack width matches player width
        attack_width = self.rect.width
        attack_height = 25 + (self.attack_combo - 1) * 3
        
        # Heavy attacks have larger hitbox
        if self.attack_type == 'heavy':
            attack_height += 8
        # Critical attacks have taller hitbox
        elif self.attack_type == 'critical':
            attack_height += 10
        
        if self.facing_right:
            # Attack to the right
            attack_rect = pg.Rect(self.rect.right, self.rect.centery - attack_height // 2, 
                                 attack_width, attack_height)
        else:
            # Attack to the left
            attack_rect = pg.Rect(self.rect.left - attack_width, self.rect.centery - attack_height // 2, 
                                 attack_width, attack_height)
        
        return attack_rect
    
    def get_attack_damage(self):
        """Returns damage based on attack type, combo level, energy, and powerups"""
        base = getattr(self, 'attack_power', 1)
        combo_bonus = max(0, self.attack_combo - 1) * 0.5  # +0.5 per combo level
        
        # Attack type modifiers
        type_multiplier = 1.0
        if self.attack_type == 'heavy':
            type_multiplier = 2.0  # Double damage for heavy attacks
        elif self.attack_type == 'critical':
            type_multiplier = 1.5  # 1.5x damage for critical hits
        
        # Energy bonus (up to 100% bonus at full energy)
        energy_bonus = (self.attack_energy / self.max_attack_energy) * 0.5  # Up to +50% from energy
        self.attack_energy = 0  # Drain energy on attack
        
        # Apply damage boost powerup
        damage_mult = self.damage_boost_mult if self.damage_boost_active else 1.0
        
        return int((base + combo_bonus) * type_multiplier * (1.0 + energy_bonus) * damage_mult)

    def get_pos_x(self):
        return self.rect.x

    def get_pos_y(self):
        return self.rect.y


class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, num_goblins):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self._layer = platform_layer
        self.num_goblins = num_goblins
        
        # Tile platform.png to create the desired width
        original_image = platform_image
        tile_width = original_image.get_width()
        original_height = original_image.get_height()
        
        # Create a surface to hold the tiled platform
        self.image = pg.Surface((int(w), original_height), pg.SRCALPHA)
        
        # Tile the platform image horizontally
        num_tiles = int(w // tile_width) + 1  # Number of tiles needed to cover width
        for i in range(num_tiles):
            x_offset = i * tile_width
            # If this is the last tile and it extends beyond width, crop it
            if x_offset + tile_width > w:
                crop_width = int(w - x_offset)
                cropped_tile = original_image.subsurface(0, 0, crop_width, original_height)
                self.image.blit(cropped_tile, (x_offset, 0))
            else:
                self.image.blit(original_image, (x_offset, 0))
        
        # Get rect from tiled image
        self.rect = self.image.get_rect()
        # Position the platform
        self.rect.x = x
        self.rect.y = y
        # Adjust collision to only the top 20 pixels for gameplay
        self.collision_rect = pg.Rect(x, y + self.rect.height - 20, w, 20)


class Monster(pg.sprite.Sprite):
    def __init__(self, game, x, y, level=1):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        # Use the generated scary monster sprite
        self.image = monster_scary
        self._layer = monster_layer
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # Boss flies around the entire map - both horizontal and vertical
        self.vx = random.choice([-6, -4, 4, 6])  # Faster horizontal movement
        self.vy = random.choice([-3, -2, 2, 3])  # Add vertical movement
        # Scale health by level: base 60 + level scaling
        base_health = 60
        self.health = int(base_health * (1.0 + (level - 1) * 0.25))  # 25% more health per level
        self.max_health = self.health
        # Create a smaller hitbox for player damage (just the moving box part)
        # The monster image is 128x128, the actual moving box is roughly in the middle
        self.damage_hitbox = pg.Rect(0, 0, 60, 60)  # Smaller hitbox for the box
        self.update_hitbox()
        # Frozen state from freeze powerup
        self.frozen = False
        self.frozen_time = 0
        # Shooting behavior
        self.shoot_timer = 0
        self.shoot_pattern = 0  # Cycle through different shooting patterns
    
    def update_hitbox(self):
        """Update the damage hitbox position to follow the monster"""
        # Center the damage hitbox on the monster's center
        self.damage_hitbox.centerx = self.rect.centerx
        self.damage_hitbox.centery = self.rect.centery

    def update(self):
        # Update frozen timer
        if self.frozen:
            self.frozen_time -= 1
            if self.frozen_time <= 0:
                self.frozen = False
        
        # Skip movement if frozen
        if self.frozen:
            return
        
        # Boss flies around the entire map
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        # Bounce off walls (horizontal)
        if self.rect.x >= WIDTH - 128:
            self.vx = -abs(self.vx)
        elif self.rect.x <= 0:
            self.vx = abs(self.vx)
        
        # Bounce off ceiling and floor (vertical)
        if self.rect.y <= 50:  # Don't go too far up (below UI panel)
            self.vy = abs(self.vy)
        elif self.rect.y >= HEIGHT - 128:
            self.vy = -abs(self.vy)
        
        # Occasionally change direction for unpredictable movement
        if random.random() < 0.02:
            self.vx = random.choice([-6, -4, 4, 6])
        if random.random() < 0.02:
            self.vy = random.choice([-3, -2, 2, 3])
        
        self.update_hitbox()  # Keep hitbox in sync
    
    def take_damage(self, damage=1):
        """Damage the monster boss"""
        self.health -= damage
        if self.health <= 0:
            # Boss always drops powerup on death (2x drops)
            for _ in range(2):
                powerup_type = random.choice(Powerup.TYPES)
                powerup = Powerup(self.game, self.rect.centerx + random.randint(-30, 30), 
                                self.rect.centery, powerup_type)
                self.game.all_sprites.add(powerup)
                self.game.powerups.add(powerup)
                powerup_arr.append(powerup)
            
            death_sound_HIT.play()
            self.kill()
            if self in monster_arr:
                monster_arr.remove(self)
    
    def draw_health_bar(self, screen):
        """Draw health bar above monster"""
        bar_width = 120
        bar_height = 10
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 20
        
        # Background (red)
        pg.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # Health (green)
        health_width = int((self.health / self.max_health) * bar_width)
        pg.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, health_width, bar_height))
        # Border
        pg.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)


class FastGoblin(pg.sprite.Sprite):
    """Faster, more aggressive goblin variant. Bounces higher and attacks more frequently."""
    def __init__(self, game, level=1):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self._layer = mob_layer
        self.image_left = gleft
        self.image_right = gright
        self.image = gleft
        self.is_elite = False
        self.rect = self.image.get_rect()
        # Fast goblins are significantly faster
        self.vx = random.choice([-6, 6]) * (1.0 + (level - 1) * 0.1)
        self.vy = 0
        self.on_ground = False
        # Less health but faster attacks
        self.health = int(3 * (1.0 + (level - 1) * 0.1))
        self.max_health = self.health
        self.jump_cooldown = 0
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 20  # More frequent attacks (was ~60 normally)
        self.attack_range = 25
        self.attack_type = 'none'
        self.walk_frame = 0
        self.walk_timer = 0
        self.stuck_counter = 0
        self.last_x = 0
        self.frozen = False
        self.frozen_time = 0
        
        # Place on platform
        available_platforms = []
        player_spawn_x = WIDTH / 2
        player_spawn_y = HEIGHT / 2
        
        for idx, plat in enumerate(settings.platform_arr):
            plat_x = plat[0]
            plat_y = plat[1]
            plat_w = plat[2]
            if abs((plat_x + plat_w/2) - player_spawn_x) < 150 and abs(plat_y - player_spawn_y) < 100:
                continue
            available_platforms.append(idx)
        
        if len(available_platforms) > 0:
            i = random.choice(available_platforms)
        else:
            i = 0
        
        y_pos = int(settings.platform_arr[i][1] - 30)
        x_start = int(settings.platform_arr[i][0])
        x_end = int(min(settings.platform_arr[i][0] + settings.platform_arr[i][2] - 20, WIDTH - 20))
        if x_end <= x_start:
            x_pos = x_start
        else:
            x_pos = random.randrange(x_start, x_end)
        self.rect.x = x_pos
        self.rect.y = y_pos
        self.spawn_platform = settings.platform_arr[i]
    
    def update(self):
        """Update fast goblin - faster movement and attacks"""
        if self.frozen:
            self.frozen_time -= 1
            if self.frozen_time <= 0:
                self.frozen = False
            return
        
        # Apply gravity
        self.vy += PLAYER_GRAV
        self.rect.y += self.vy
        self.rect.x += self.vx
        
        # Platform collisions
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        if self.vy > 0:
            self.vy = 0
            self.on_ground = True
            self.rect.bottom = hits[0].rect.top
        if self.vy < 0:
            self.vy = 0
            self.rect.top = hits[0].rect.bottom if hits else self.rect.top
        
        if not hits:
            self.on_ground = False
        
        # Jump more frequently
        if self.on_ground and random.random() < 0.04:
            self.vy = -15
        
        self.attack_cooldown -= 1
    
    def take_damage(self, damage=1):
        self.health -= damage
        if self.health <= 0:
            goblin_death_sound.play()
            self.kill()


class ArcherSkeleton(pg.sprite.Sprite):
    """Skeleton archer variant. Shoots faster and from farther away."""
    def __init__(self, game, level=1):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self._layer = mob_layer
        self.image = sleft
        self.rect = self.image.get_rect()
        self.is_elite = False
        # Slightly slower movement than normal skeleton
        self.vx = 2.5 * (1.0 + (level - 1) * 0.1)
        self.vy = 0
        self.on_ground = False
        self.jump_cooldown = 0
        self.x_upper_bound = 0
        # Same health scaling as normal skeleton
        self.health = int(4 * (1.0 + (level - 1) * 0.15))
        self.max_health = self.health
        # Fast shooting - increased rate
        self.shoot_timer = random.randint(20, 50)
        self.shoot_range = 300  # Can shoot from farther away
        self.walk_frame = 0
        self.walk_timer = 0
        self.shooting = False
        self.shoot_frame = 0
        
        available_platforms = []
        player_spawn_x = WIDTH / 2
        player_spawn_y = HEIGHT / 2
        
        for idx, plat in enumerate(settings.platform_arr):
            plat_x = plat[0]
            plat_y = plat[1]
            plat_w = plat[2]
            if abs((plat_x + plat_w/2) - player_spawn_x) < 150 and abs(plat_y - player_spawn_y) < 100:
                continue
            if plat[4] > 0:
                available_platforms.append(idx)
        
        if len(available_platforms) == 0:
            for idx, plat in enumerate(settings.platform_arr):
                plat_x = plat[0]
                plat_y = plat[1]
                plat_w = plat[2]
                if abs((plat_x + plat_w/2) - player_spawn_x) < 150 and abs(plat_y - player_spawn_y) < 100:
                    continue
                available_platforms.append(idx)
            i = random.choice(available_platforms) if len(available_platforms) > 0 else 0
        else:
            i = random.choice(available_platforms)
            settings.platform_arr[i][4] = settings.platform_arr[i][4] - 1

        y_pos = settings.platform_arr[i][1] - 30
        x_pos = random.randrange(settings.platform_arr[i][0], settings.platform_arr[i][0] + settings.platform_arr[i][2] - 20)

        self.x_lower_bound = settings.platform_arr[i][0]
        self.x_upper_bound = settings.platform_arr[i][0] + settings.platform_arr[i][2] - 20
        self.spawn_platform = settings.platform_arr[i]
        self.rect.y = y_pos
        self.rect.x = x_pos
    
    def update(self):
        """Update archer skeleton - faster shooting"""
        if self.frozen:
            self.frozen_time -= 1
            if self.frozen_time <= 0:
                self.frozen = False
            return
        
        # Apply gravity
        self.vy += PLAYER_GRAV
        self.rect.y += self.vy
        
        # Platform collisions
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        if hits:
            if self.vy >= 0:
                self.vy = 0
                self.on_ground = True
                self.rect.bottom = hits[0].rect.top
        else:
            self.on_ground = False
        
        # Jump occasionally
        if self.on_ground and random.random() < 0.02:
            self.vy = -12
        
        # Move and keep on platform
        if self.rect.x < self.x_lower_bound:
            self.vx = 2.5
        elif self.rect.x > self.x_upper_bound:
            self.vx = -2.5
        else:
            if random.random() < 0.02:
                self.vx *= -1
        
        self.rect.x += self.vx
        
        # Shooting behavior - more aggressive
        self.shoot_timer -= 1
        if self.shoot_timer <= 0 and self.on_ground:
            player_pos = self.game.player.rect.centerx
            distance = abs(player_pos - self.rect.centerx)
            if distance < self.shoot_range:
                arrow = Arrow(self.game, self.rect.centerx, self.rect.centery, player_pos)
                self.game.all_sprites.add(arrow)
                self.game.skeleton_arrows.add(arrow)
                self.shoot_timer = random.randint(20, 50)
    
    def take_damage(self, damage=1):
        self.health -= damage
        if self.health <= 0:
            skeleton_death_sound.play()
            self.kill()


class Fireball(pg.sprite.Sprite):
    def __init__(self, game, start_pos, target_pos):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self._layer = projectile_layer
        
        # Create fireball visual (orange/red circle)
        self.image = pg.Surface((16, 16), pg.SRCALPHA)
        pg.draw.circle(self.image, (255, 100, 0), (8, 8), 8)  # Orange outer
        pg.draw.circle(self.image, (255, 200, 0), (8, 8), 5)  # Yellow inner
        
        self.rect = self.image.get_rect(center=start_pos)
        
        # Calculate direction to target
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        # Normalize and set speed
        speed = 8
        if distance > 0:
            self.vx = (dx / distance) * speed
            self.vy = (dy / distance) * speed
        else:
            self.vx = 0
            self.vy = -speed  # Default upward if no target
        
        self.lifetime = 120  # 4 seconds at 30 FPS
    
    def update(self):
        # Move fireball
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        # Check platform collision - fireball stops
        for platform in self.game.platforms:
            collision_check = platform.collision_rect if hasattr(platform, 'collision_rect') else platform.rect
            if self.rect.colliderect(collision_check):
                self.kill()
                return
        
        # Check lava collision
        for lava in self.game.lava:
            if self.rect.colliderect(lava.rect):
                self.kill()
                return
        
        # Decrease lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        
        # Remove if off screen
        if self.rect.right < 0 or self.rect.left > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


class Explosion(pg.sprite.Sprite):
    """Simple explosion animation that also applies area damage on creation.

    Parameters:
      game: reference to Game
      pos: (x,y) center of explosion
      radius: pixel radius for splash damage
      damage: integer damage to apply to nearby enemies
      exclude_sprite: a sprite to exclude from splash (e.g. the directly hit target)
    """
    def __init__(self, game, pos, radius=48, damage=2, exclude_sprite=None):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self._layer = projectile_layer
        self.pos = pos
        self.radius = radius
        self.damage = damage
        self.exclude = exclude_sprite

        # Pre-generate simple expanding-circle frames for animation
        self.frames = []
        sizes = [int(radius * t) for t in (0.25, 0.5, 0.75, 1.0)]
        for s in sizes:
            surf = pg.Surface((s*2, s*2), pg.SRCALPHA)
            # Outer glow
            pg.draw.circle(surf, (255, 140, 0, 160), (s, s), s)
            # Inner bright
            pg.draw.circle(surf, (255, 220, 0, 220), (s, s), max(1, int(s*0.5)))
            self.frames.append(surf)

        self.frame_index = 0
        self.frame_timer = 0
        self.frame_delay = 4
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=pos)

        # Apply immediate splash damage to nearby enemies (excluding provided sprite)
        try:
            # Goblins
            for g in list(self.game.goblins):
                if g is self.exclude:
                    continue
                dx = g.rect.centerx - pos[0]
                dy = g.rect.centery - pos[1]
                if dx*dx + dy*dy <= radius*radius:
                    try:
                        g.take_damage(damage)
                    except Exception:
                        pass
            # Skeletons
            for s in list(self.game.skeletons):
                if s is self.exclude:
                    continue
                dx = s.rect.centerx - pos[0]
                dy = s.rect.centery - pos[1]
                if dx*dx + dy*dy <= radius*radius:
                    try:
                        s.take_damage(damage)
                    except Exception:
                        pass
            # Monster (boss)
            for m in list(self.game.monster):
                if m is self.exclude:
                    continue
                dx = m.rect.centerx - pos[0]
                dy = m.rect.centery - pos[1]
                if dx*dx + dy*dy <= radius*radius:
                    try:
                        m.take_damage(damage)
                    except Exception:
                        pass
        except Exception:
            pass

        # play explosion sound if available (use globals to avoid static name errors)
        try:
            snd = globals().get('explosion_sound', None)
            if snd:
                try:
                    snd.play()
                except Exception:
                    pass
        except Exception:
            pass

    def update(self):
        # Advance animation and kill when done
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.kill()
                return
            self.image = self.frames[self.frame_index]
            # update rect to keep center
            center = self.rect.center
            self.rect = self.image.get_rect(center=center)


class Arrow(pg.sprite.Sprite):
    """Arrow projectile shot by skeletons toward the player"""
    def __init__(self, game, start_pos, target_pos):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self._layer = projectile_layer

        # Choose animation frames if available, otherwise use a single image
        try:
            frames = arrow_skeleton_frames
        except NameError:
            frames = []

        if frames and len(frames) > 0:
            # Scale frames to 50% size for smaller arrows
            scaled_frames = []
            for f in frames:
                w, h = f.get_size()
                scaled_frames.append(pg.transform.scale(f, (w // 2, h // 2)))
            self.frames = scaled_frames
            self.frame_index = 0
            self.image = self.frames[0]
        else:
            # Fallback to the static arrow (scaled to 50%)
            try:
                orig = arrow_skeleton
                w, h = orig.get_size()
                self.image = pg.transform.scale(orig, (w // 2, h // 2))
            except NameError:
                # create tiny surface (smaller)
                self.image = pg.Surface((24, 6), pg.SRCALPHA)
                self.image.fill((120, 80, 40))
            self.frames = None

        self.rect = self.image.get_rect(center=start_pos)

        # Calculate direction to target
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        # Balance: slightly faster arrows
        speed = 12
        if distance > 0:
            self.vx = (dx / distance) * speed
            self.vy = (dy / distance) * speed
        else:
            self.vx = speed
            self.vy = 0

        # Damage and lifetime for balance
        self.damage = 4
        self.lifetime = 180
        self.animation_timer = 0
        
        # Rotate the image(s) to face the flight direction
        # Compute angle in degrees (pygame rotates counter-clockwise)
        angle = -math.degrees(math.atan2(self.vy, self.vx))
        # If we have animated frames, rotate each and store
        if self.frames:
            rotated = []
            for f in self.frames:
                rotated.append(pg.transform.rotate(f, angle))
            self.frames = rotated
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=start_pos)
        else:
            try:
                orig = self.image
                self.image = pg.transform.rotate(orig, angle)
                self.rect = self.image.get_rect(center=start_pos)
            except Exception:
                pass

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Animate if frames exist
        if self.frames:
            self.animation_timer += 1
            if self.animation_timer >= 6:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]

        # Check platform collision - arrows should be blocked
        for platform in self.game.platforms:
            collision_check = platform.collision_rect if hasattr(platform, 'collision_rect') else platform.rect
            if self.rect.colliderect(collision_check):
                self.kill()
                return

        # Check lava collision
        for lava in self.game.lava:
            if self.rect.colliderect(lava.rect):
                self.kill()
                return

        # Lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return

        # Remove if off screen
        if self.rect.right < 0 or self.rect.left > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


class Lava(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
        self._layer = lava_layer
        # Create a surface with the specified width and height
        self.image = pg.Surface((w, h))
        self.image.blit(lava, (0, 0))  # Blit the lava texture to fill the surface
        # Tile the lava texture if needed to fill the width
        tiles_needed = (w // lava.get_width()) + 1
        for i in range(1, tiles_needed):
            tile_x = i * lava.get_width()
            if tile_x < w:
                self.image.blit(lava, (tile_x, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self._layer = coin_layer
        self.image = coin
        self.rect = self.image.get_rect()
        self.x_upper_bound = 0
        # Coin is 10px wide and 10px tall
        j = 2
        while j == 2:
            j = random.randrange(5)

        y_pos = settings.platform_arr[j][1] - 15
        x_pos = random.randrange(settings.platform_arr[j][0], settings.platform_arr[j][0] + settings.platform_arr[j][2] - 10)
        self.rect.y = y_pos
        self.rect.x = x_pos

    def update(self):
        """hits_coin = pg.sprite.spritecollide(self.game.player, self.game.coins, False)
        if hits_coin:
            self.game.score += 100
            coin_sound.play()
            self.game.coin_count -= 1
            self.kill()"""
        """if self.rect.x == self.game.player.get_pos_x() or self.rect.x == self.game.player.get_pos_x() + 5 \
                or self.rect.x == self.game.player.get_pos_x() - 5:
            if self.rect.y - 15 == self.game.player.get_pos_y() or self.rect.y == self.game.player.get_pos_y() - 24 \
                    or self.rect.y == self.game.player.get_pos_y() + 24:
                self.game.score += 100
                coin_sound.play()
                self.game.coin_count -= 1
                self.kill()"""
        # Safety check to avoid crashes when arrays are empty
        if len(player_arr) == 0 or len(coin_arr) == 0:
            return
            
        for coi in coin_arr[:]:  # Create a copy of the list to iterate safely
            if abs(coi.rect.x - player_arr[0].rect.x) < 10 and abs(coi.rect.y - player_arr[0].rect.y) < 20:
                self.game.score += 500
                coin_sound.play()
                self.game.coin_count -= 1
                coi.kill()
                coin_arr.remove(coi)


class Heart(pg.sprite.Sprite):
    """Health pickup that restores player health"""
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self._layer = coin_layer
        # Use heart image
        self.image = heart_image
        self.rect = self.image.get_rect()
        self.heal_amount = 15  # How much health to restore
        
        # Place on a random platform
        if len(settings.platform_arr) > 0:
            plat_index = random.randrange(len(settings.platform_arr))
            y_pos = settings.platform_arr[plat_index][1] - 25
            x_pos = random.randrange(settings.platform_arr[plat_index][0], 
                                     settings.platform_arr[plat_index][0] + settings.platform_arr[plat_index][2] - 20)
            self.rect.y = y_pos
            self.rect.x = x_pos

    def update(self):
        # Check for player collision
        if len(player_arr) > 0:
            if abs(self.rect.x - player_arr[0].rect.x) < 15 and abs(self.rect.y - player_arr[0].rect.y) < 25:
                # Heal player (cap at player's max_hearts, which may be upgraded)
                player_max = getattr(player_arr[0], 'max_hearts', 100)
                player_arr[0].hearts = min(player_arr[0].hearts + self.heal_amount, player_max)
                coin_sound.play()  # Reuse coin sound for pickup
                self.kill()


class MonsterBullet(pg.sprite.Sprite):
    def __init__(self, target_pos=None):
        pg.sprite.Sprite.__init__(self)
        self._layer = projectile_layer
        self.image = lava_ball
        self.rect = self.image.get_rect()
        self.pos = vec(WIDTH / 2, HEIGHT / 2)
        
        # Get bullet starting position from boss
        y_pos = 125
        if len(monster_arr) > 0:
            x_pos = monster_arr[0].rect.centerx
            y_pos = monster_arr[0].rect.centery
        else:
            x_pos = WIDTH / 2
        
        self.rect.y = y_pos
        self.rect.x = x_pos
        
        # If target position provided, aim at it; otherwise use random pattern
        if target_pos:
            dx = target_pos[0] - x_pos
            dy = target_pos[1] - y_pos
            distance = (dx**2 + dy**2)**0.5
            if distance > 0:
                # Normalize and scale to speed
                speed = 8  # Faster bullets
                self.speedx = (dx / distance) * speed
                self.speedy = (dy / distance) * speed
            else:
                self.speedx = random.randrange(-10, 10)
                self.speedy = random.randrange(5, 15)
        else:
            # Random spread pattern
            self.speedx = random.randrange(-12, 12)  # Faster
            self.speedy = random.randrange(6, 16)  # Faster

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx  # Fixed: was subtracting, now adding
        
        # Kill bullets that go off screen
        if self.rect.y > HEIGHT or self.rect.y < 0:
            self.kill()
        if self.rect.x < 0 or self.rect.x > WIDTH:
            self.kill()


class Goblin(pg.sprite.Sprite):
    def __init__(self, game, is_elite=False, speed_mult=1.0, level=1):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self._layer = mob_layer
        self.image_left = gleft
        self.image_right = gright
        self.image = gleft
        self.is_elite = is_elite
        self.rect = self.image.get_rect()
        # Don't shrink the hitbox - use full rect for proper collision
        # Elite enemies are faster and have more health
        # Progressive difficulty also increases speed
        elite_mult = 1.3 if is_elite else 1.0
        self.vx = random.choice([-4, 4]) * elite_mult * speed_mult
        self.vy = 0
        self.on_ground = False
        # Scale health by level: base 2 (or 5 for elite) + level bonus
        base_health = 5 if is_elite else 2
        self.health = int(base_health * (1.0 + (level - 1) * 0.15))
        self.max_health = self.health
        self.jump_cooldown = 0
        # Goblin attack system
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_range = 25  # How close goblin needs to be to stab
        self.attack_type = 'none'  # 'none', 'stab'
        # Walking animation
        self.walk_frame = 0
        self.walk_timer = 0
        
        # Stuck detection - if goblin bounces back and forth in same spot
        self.stuck_counter = 0
        self.last_x = 0
        # Frozen state from freeze powerup
        self.frozen = False
        self.frozen_time = 0
        
        # Goblin is 20px wide and 30px tall
        # Spread goblins across platforms, but avoid player spawn platform (center of screen)
        available_platforms = []
        player_spawn_x = WIDTH / 2
        player_spawn_y = HEIGHT / 2
        
        for idx, plat in enumerate(settings.platform_arr):
            plat_x = plat[0]
            plat_y = plat[1]
            plat_w = plat[2]
            # Skip platforms near player spawn (within 150px horizontally and 100px vertically)
            if abs((plat_x + plat_w/2) - player_spawn_x) < 150 and abs(plat_y - player_spawn_y) < 100:
                continue
            available_platforms.append(idx)
        
        # Choose random platform (or fallback to first if all filtered out)
        if len(available_platforms) > 0:
            i = random.choice(available_platforms)
        else:
            i = 0  # Fallback

        # platform_arr may contain floats (from divisions in settings). Cast to int for pixel positions.
        y_pos = int(settings.platform_arr[i][1] - 30)
        x_start = int(settings.platform_arr[i][0])
        x_end = int(min(settings.platform_arr[i][0] + settings.platform_arr[i][2] - 20, WIDTH - 20))
        # Ensure range is valid for randrange
        if x_end <= x_start:
            x_pos = x_start
        else:
            x_pos = random.randrange(x_start, x_end)

        self.current_platform = i
        self.rect.y = y_pos
        self.rect.x = x_pos
        self.last_x = x_pos

    def update(self):
        # Update frozen timer
        if self.frozen:
            self.frozen_time -= 1
            if self.frozen_time <= 0:
                self.frozen = False
        
        # Skip movement if frozen
        if self.frozen:
            return
        
        # Apply gravity
        self.vy += 0.8
        self.rect.y += self.vy
        
        # Check platform collisions
        self.on_ground = False
        for platform in self.game.platforms:
            # Use collision_rect for gameplay collision
            collision_check = platform.collision_rect if hasattr(platform, 'collision_rect') else platform.rect
            if self.rect.colliderect(collision_check):
                if self.vy > 0:  # Falling down
                    # Use collision_rect.top to align properly with tiled platform top
                    plat_top = collision_check.top if hasattr(platform, 'collision_rect') else platform.rect.top
                    self.rect.bottom = plat_top
                    self.vy = 0
                    self.on_ground = True
        
        # Check lava collision - take damage if touching lava
        for lava in self.game.lava:
            if self.rect.colliderect(lava.rect):
                # Goblin touched lava - instant death
                lava_burning_sound.play()
                self.kill()
                if self in goblins_arr:
                    goblins_arr.remove(self)
                return  # Exit update to prevent further processing
        
        # Look ahead before moving to avoid falling into lava
        # Check what's directly below and to the sides for lava
        will_fall_into_lava = False
        will_fall_off_platform = True
        lava_on_left = False
        lava_on_right = False
        
        # Check directly below for lava
        below_check = self.rect.copy()
        below_check.y += 35  # Check just below current position
        for lava in self.game.lava:
            if below_check.colliderect(lava.rect):
                will_fall_into_lava = True
        
        # Check ahead in movement direction for lava
        if self.vx != 0:
            ahead_check = self.rect.copy()
            ahead_check.x += self.vx * 8  # Look 8 pixels in direction of movement
            ahead_check.y += 35  # Check below as well
            for lava in self.game.lava:
                if ahead_check.colliderect(lava.rect):
                    will_fall_into_lava = True
        
        # Check sides for lava nearby
        left_check = self.rect.copy()
        left_check.x -= 50
        left_check.y += 10
        for lava in self.game.lava:
            if left_check.colliderect(lava.rect):
                lava_on_left = True
        
        right_check = self.rect.copy()
        right_check.x += 50
        right_check.y += 10
        for lava in self.game.lava:
            if right_check.colliderect(lava.rect):
                lava_on_right = True
        
        # Check if there's a platform ahead in movement direction
        test_rect = self.rect.copy()
        if self.vx != 0:
            test_rect.x += self.vx * 8
        test_rect.y += 50  # Check further below
        for platform in self.game.platforms:
            if test_rect.colliderect(platform.rect):
                will_fall_off_platform = False
                break
        
        # Detect stuck situation - if goblin hasn't moved much in last 30 frames
        if abs(self.rect.x - self.last_x) < 2:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
        self.last_x = self.rect.x
        
        # GOBLIN AI: Intelligent chase and platform navigation
        if len(player_arr) > 0:
            player = player_arr[0]
            player_x = player.rect.centerx
            player_y = player.rect.centery
            goblin_x = self.rect.centerx
            goblin_y = self.rect.centery
            
            horizontal_dist = abs(player_x - goblin_x)
            vertical_dist = abs(player_y - goblin_y)
            
            # Determine direction toward player
            if player_x < goblin_x - 5:
                desired_direction = -1  # Move left
            elif player_x > goblin_x + 5:
                desired_direction = 1  # Move right
            else:
                desired_direction = 0  # Same horizontal position
            
            # LAVA AVOIDANCE - Override desired direction if lava is detected ahead
            # But don't freeze - always try to move in some direction
            if will_fall_into_lava:
                # Lava is ahead in current direction - reverse it only if we were moving
                if desired_direction != 0:
                    desired_direction = -desired_direction
                else:
                    # If we weren't moving toward them, pick a safe direction
                    desired_direction = 1 if not lava_on_right else -1
            elif desired_direction == -1 and lava_on_left:
                # Want to go left but lava is on left side - go right instead
                desired_direction = 1
            elif desired_direction == 1 and lava_on_right:
                # Want to go right but lava is on right side - go left instead
                desired_direction = -1
            
            # Apply movement with speed
            speed_mult = 1.3 if self.is_elite else 1.0
            if desired_direction == -1:
                self.vx = -4 * speed_mult
            elif desired_direction == 1:
                self.vx = 4 * speed_mult
            else:
                self.vx = 0
            
            # Smart jumping: Jump more aggressively if player is above or unreachable
            # BUT avoid jumping into lava
            if self.on_ground and self.jump_cooldown == 0 and not will_fall_into_lava:
                # Jump if player is significantly above
                if player_y < goblin_y - 40 and horizontal_dist < 150:
                    if random.random() < 0.5:  # 50% chance to jump up
                        self.vy = random.randrange(-15, -11)
                        self.jump_cooldown = 30
                # Jump if there's a platform below to reach player on lower level (not into lava)
                elif player_y > goblin_y + 80 and horizontal_dist < 200:
                    if random.random() < 0.3:  # 30% chance to jump down
                        self.vy = random.randrange(-12, -8)
                        self.jump_cooldown = 30
                # Jump to avoid falling off edges while chasing (but not into lava)
                elif will_fall_off_platform and self.stuck_counter > 15:
                    self.vy = random.randrange(-13, -10)
                    self.jump_cooldown = 35
        else:
            # No player - slow wandering
            if random.random() < 0.005:
                self.vx = -self.vx
        
        # FINAL SAFETY CHECK: Don't move if we would land in lava
        # Test the position we would move to
        test_move_rect = self.rect.copy()
        test_move_rect.x += self.vx
        test_move_rect.y += 10  # Check at slightly lower position to catch lava
        
        landing_in_lava = False
        for lava in self.game.lava:
            if test_move_rect.colliderect(lava.rect):
                landing_in_lava = True
                break
        
        # If this movement would land us in lava, reverse direction
        if landing_in_lava:
            self.vx = -self.vx
        
        # Movement
        self.rect.x += self.vx
        
        # Prevent goblin-goblin collisions - check for other goblins after moving
        for goblin in goblins_arr:
            if goblin is not self and self.rect.colliderect(goblin.rect):
                # Reverse both goblins' directions to separate them
                self.vx = -self.vx
                goblin.vx = -goblin.vx
                # Move both goblins back slightly to prevent overlap
                self.rect.x -= self.vx * 2
                goblin.rect.x -= goblin.vx * 2
                break  # Only handle one collision per frame
        
        # Attack system - goblins must attack to damage player
        if self.attack_timer > 0:
            self.attack_timer -= 1
            if self.attack_timer == 0:
                self.attacking = False
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Check if player is in attack range
        if len(player_arr) > 0 and self.attack_cooldown == 0 and not self.attacking:
            player = player_arr[0]
            dist_to_player = abs(self.rect.centerx - player.rect.centerx)
            vertical_dist = abs(self.rect.centery - player.rect.centery)
            
            # Attack if player is close and roughly on same height
            if dist_to_player < self.attack_range and vertical_dist < 50:
                self.attacking = True
                self.attack_timer = 15  # Attack lasts 15 frames
                self.attack_cooldown = 60  # 2 second cooldown between attacks
        
        # Jump cooldown
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
        
        # Only jump if not near lava
        near_lava = False
        for lava in self.game.lava:
            if abs(self.rect.bottom - lava.rect.top) < 100:  # Within 100 pixels of lava
                near_lava = True
                break
        
        # Intelligent jumping toward player
        if self.on_ground and not near_lava and self.jump_cooldown == 0 and len(player_arr) > 0:
            player = player_arr[0]
            vertical_dist = abs(self.rect.centery - player.rect.centery)
            horizontal_dist = abs(self.rect.centerx - player.rect.centerx)
            
            # Jump if player is above or on different platform
            if vertical_dist > 50 and horizontal_dist < 250:
                # Higher chance to jump when player is nearby on different level
                if random.random() < 0.12:  # 12% chance per frame when conditions met
                    self.vy = random.randrange(-13, -9)  # Stronger jump
                    self.jump_cooldown = 45  # Shorter cooldown
            elif random.random() < 0.03:  # 3% chance for random exploration jumps
                self.vy = random.randrange(-12, -8)
                self.jump_cooldown = 50
        
        # More aggressive movement - goblins should be constantly moving
        # Only turn if stuck or detected fall/lava - not randomly turning
        # Random turns now reduced to 0.002 (very rare)
        if random.random() < 0.002:  # Very rare random turn
            self.vx = -self.vx
        
        # Wrap around screen edges
        if self.rect.x < 0:
            self.rect.x = WIDTH
        if self.rect.x > WIDTH:
            self.rect.x = 0
        
        # Display attack animation if attacking
        if self.attacking:
            # Show stab animation during attack
            attack_progress = (self.attack_timer - 1) // 8  # 15 frames / 2 frames = ~7-8 frames per pose
            if attack_progress >= 1:
                attack_progress = 1
            if self.vx < 0:
                try:
                    self.image = pg.image.load(f'images/enemies/goblin_stab_{attack_progress}.png')
                except:
                    self.image = gleft
            else:
                try:
                    self.image = pg.image.load(f'images/enemies/goblin_stab_{attack_progress}.png')
                except:
                    self.image = gright
        # Update sprite direction with walking animation
        elif self.vx < 0:
            # Walking left - animate
            self.walk_timer += 1
            if self.walk_timer >= 10:  # Change frame every 10 ticks
                self.walk_timer = 0
                self.walk_frame = 1 - self.walk_frame
            # Use walk animation if moving, else use idle
            if self.walk_frame == 1:
                try:
                    self.image = pg.image.load('images/enemies/goblin_walk_1.png')
                except:
                    self.image = gleft
            else:
                self.image = gleft
        elif self.vx > 0:
            # Walking right - animate
            self.walk_timer += 1
            if self.walk_timer >= 10:
                self.walk_timer = 0
                self.walk_frame = 1 - self.walk_frame
            if self.walk_frame == 1:
                try:
                    self.image = pg.image.load('images/enemies/goblin_walk_1.png')
                except:
                    self.image = gright
            else:
                self.image = gright
        
        # Apply golden tint for elite enemies
        if self.is_elite and not hasattr(self, '_tinted'):
            self.image = self.image.copy()
            gold_overlay = pg.Surface(self.image.get_size(), pg.SRCALPHA)
            gold_overlay.fill((255, 215, 0, 120))  # More intense golden tint
            self.image.blit(gold_overlay, (0, 0), special_flags=pg.BLEND_ADD)
            self._tinted = True
        
        # Kill if fell off screen
        if self.rect.y > HEIGHT:
            self.kill()
            if self in goblins_arr:
                goblins_arr.remove(self)
    
    def take_damage(self, damage=1):
        """Damage the goblin"""
        self.health -= damage
        if self.health <= 0:
            # Chance to drop powerup on death (higher for elite)
            drop_chance = 0.15 if self.is_elite else 0.08
            if random.random() < drop_chance:
                powerup_type = random.choice(Powerup.TYPES)
                powerup = Powerup(self.game, self.rect.centerx, self.rect.centery, powerup_type)
                self.game.all_sprites.add(powerup)
                self.game.powerups.add(powerup)
                powerup_arr.append(powerup)
            
            # Play goblin-specific death sound if available
            try:
                snd = globals().get('goblin_death_sound', None)
                if snd:
                    snd.play()
            except Exception:
                pass
            self.kill()
            if self in goblins_arr:
                goblins_arr.remove(self)
    
    def get_attack_rect(self):
        """Return attack hitbox when goblin is attacking"""
        if not self.attacking or self.attack_timer <= 0:
            return None
        # Attack rect extends in front of goblin
        attack_width = 35
        attack_height = 30
        if self.vx > 0:  # Facing right
            return pg.Rect(self.rect.right - 10, self.rect.centery - attack_height//2, attack_width, attack_height)
        else:  # Facing left
            return pg.Rect(self.rect.left - attack_width + 10, self.rect.centery - attack_height//2, attack_width, attack_height)


class Skeleton(pg.sprite.Sprite):
    def __init__(self, game, is_elite=False, speed_mult=1.0, level=1):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self._layer = mob_layer
        self.image = sleft
        self.rect = self.image.get_rect()
        self.is_elite = is_elite
        # Elite enemies are faster and have more health
        # Progressive difficulty also increases speed
        elite_mult = 1.3 if is_elite else 1.0
        self.vx = 3 * elite_mult * speed_mult
        self.vy = 0  # Vertical velocity for gravity
        self.on_ground = False  # Track if on platform
        self.jump_cooldown = 0  # Cooldown between jumps
        self.x_upper_bound = 0
        # Scale health by level: base 3 (or 6 for elite) + level bonus
        base_health = 6 if is_elite else 3
        self.health = int(base_health * (1.0 + (level - 1) * 0.15))
        self.max_health = self.health
        # Increase base cooldown to reduce firing frequency
        self.shoot_timer = random.randint(40, 90)  # frames until next possible shot - increased fire rate
        # Walking and shooting animation
        self.walk_frame = 0
        self.walk_timer = 0
        self.shooting = False
        self.shoot_frame = 0
        # Skeleton is 20px wide and 30px tall
        # Find a platform, but avoid player spawn platform (center of screen)
        available_platforms = []
        player_spawn_x = WIDTH / 2
        player_spawn_y = HEIGHT / 2
        
        for idx, plat in enumerate(settings.platform_arr):
            plat_x = plat[0]
            plat_y = plat[1]
            plat_w = plat[2]
            # Skip platforms near player spawn (within 150px horizontally and 100px vertically)
            if abs((plat_x + plat_w/2) - player_spawn_x) < 150 and abs(plat_y - player_spawn_y) < 100:
                continue
            # Skip if platform has no spawn slots
            if plat[4] > 0:
                available_platforms.append(idx)
        
        # If no platforms available, use any platform except player spawn area
        if len(available_platforms) == 0:
            # Fallback to any platform
            for idx, plat in enumerate(settings.platform_arr):
                plat_x = plat[0]
                plat_y = plat[1]
                plat_w = plat[2]
                if abs((plat_x + plat_w/2) - player_spawn_x) < 150 and abs(plat_y - player_spawn_y) < 100:
                    continue
                available_platforms.append(idx)
            i = random.choice(available_platforms) if len(available_platforms) > 0 else 0
        else:
            i = random.choice(available_platforms)
            settings.platform_arr[i][4] = settings.platform_arr[i][4] - 1

        y_pos = settings.platform_arr[i][1] - 30
        x_pos = random.randrange(settings.platform_arr[i][0], settings.platform_arr[i][0] + settings.platform_arr[i][2] - 20)

        self.x_lower_bound = settings.platform_arr[i][0]
        self.x_upper_bound = settings.platform_arr[i][0] + settings.platform_arr[i][2] - 20

        self.spawn_platform = settings.platform_arr[i]
        self.rect.y = y_pos
        self.rect.x = x_pos
        # Frozen state from freeze powerup
        self.frozen = False
        self.frozen_time = 0

    def get_attack_rect(self):
        """Return attack hitbox only when actively shooting. Otherwise return None."""
        if self.shooting:
            return self.rect
        return None

    def update(self):
        # Update frozen timer
        if self.frozen:
            self.frozen_time -= 1
            if self.frozen_time <= 0:
                self.frozen = False
        
        # Skip movement if frozen
        if self.frozen:
            return
        
        # Apply gravity
        self.vy += 0.8
        self.rect.y += self.vy
        
        # Check platform collisions
        self.on_ground = False
        for platform in self.game.platforms:
            # Use collision_rect for gameplay collision
            collision_check = platform.collision_rect if hasattr(platform, 'collision_rect') else platform.rect
            if self.rect.colliderect(collision_check):
                if self.vy > 0:  # Falling down
                    self.rect.bottom = collision_check.top
                    self.vy = 0
                    self.on_ground = True
        
        # Check lava collision - take damage if touching lava
        for lava in self.game.lava:
            if self.rect.colliderect(lava.rect):
                # Skeleton touched lava - instant death
                lava_burning_sound.play()
                self.kill()
                if self in skel_arr:
                    skel_arr.remove(self)
                return  # Exit update to prevent further processing
        
        # Smart AI: SKELETON RANGED BEHAVIOR - Position for clear shots
        if len(player_arr) > 0:
            player = player_arr[0]
            player_x = player.rect.centerx
            player_y = player.rect.centery
            skeleton_x = self.rect.centerx
            skeleton_y = self.rect.centery
            horizontal_dist = abs(player_x - skeleton_x)
            vertical_dist = abs(player_y - skeleton_y)
            
            # Check if skeleton has line of sight to player (no platforms blocking)
            has_clear_shot = True
            for platform in self.game.platforms:
                platform_check = platform.collision_rect if hasattr(platform, 'collision_rect') else platform.rect
                # Simple line of sight check - if platform is between skeleton and player
                if skeleton_x < player_x:
                    if platform_check.left < player_x and platform_check.right > skeleton_x:
                        if skeleton_y < platform_check.top < player_y or player_y < platform_check.top < skeleton_y:
                            has_clear_shot = False
                            break
                else:
                    if platform_check.right > player_x and platform_check.left < skeleton_x:
                        if skeleton_y < platform_check.top < player_y or player_y < platform_check.top < skeleton_y:
                            has_clear_shot = False
                            break
            
            # Check if player is below skeleton (might want to drop down)
            player_is_below = player_y > skeleton_y + 100
            
            # Positioning strategy based on shot availability and distance
            if not has_clear_shot:
                # No clear shot - move to get better position
                if vertical_dist > 100:
                    # Player is on different level - try to get closer vertically by moving
                    if player_is_below and horizontal_dist < 250:
                        # Player is below - move toward edge to drop down
                        # Find current platform to determine edge direction
                        on_platform = None
                        for platform in self.game.platforms:
                            platform_check = platform.collision_rect if hasattr(platform, 'collision_rect') else platform.rect
                            if abs(self.rect.bottom - platform_check.top) < 5 and self.rect.centerx > platform_check.left and self.rect.centerx < platform_check.right:
                                on_platform = platform_check
                                break
                        
                        if on_platform:
                            # Move toward the edge closest to player
                            if player_x > skeleton_x:
                                # Player is to the right - move right toward right edge
                                if self.rect.right < on_platform.right - 10:
                                    self.vx = abs(self.vx)  # Move right to edge
                                else:
                                    self.vx = abs(self.vx) * 0.3  # At edge, keep moving slowly to fall off
                            else:
                                # Player is to the left - move left toward left edge
                                if self.rect.left > on_platform.left + 10:
                                    self.vx = -abs(self.vx)  # Move left to edge
                                else:
                                    self.vx = -abs(self.vx) * 0.3  # At edge, keep moving slowly to fall off
                        else:
                            # No platform detected, move toward player
                            if player_x > skeleton_x:
                                self.vx = abs(self.vx)
                            else:
                                self.vx = -abs(self.vx)
                    elif horizontal_dist > 200:
                        # Move toward player to get on same platform or closer
                        if player_x > skeleton_x:
                            self.vx = abs(self.vx)  # Move right toward player
                        else:
                            self.vx = -abs(self.vx)  # Move left toward player
                    else:
                        # Close enough horizontally - prepare to jump or hold position
                        self.vx = 0
                else:
                    # Similar height but blocked - move to get angle
                    if player_x > skeleton_x:
                        self.vx = abs(self.vx)  # Move right
                    else:
                        self.vx = -abs(self.vx)  # Move left
            elif horizontal_dist < 120:
                # Has shot but too close - back away for safety
                if player_x > skeleton_x:
                    self.vx = -abs(self.vx)  # Move left away from player
                else:
                    self.vx = abs(self.vx)  # Move right away from player
            elif horizontal_dist > 400:
                # Too far even with clear shot - move closer for better accuracy
                if player_x > skeleton_x:
                    self.vx = abs(self.vx)  # Move right toward player
                else:
                    self.vx = -abs(self.vx)  # Move left toward player
            elif vertical_dist > 120 and not player_is_below:
                # Player is higher - move to edge to prepare for jump
                if player_x > skeleton_x:
                    self.vx = abs(self.vx) * 0.5  # Move slowly toward player
                else:
                    self.vx = -abs(self.vx) * 0.5
            elif vertical_dist > 120 and player_is_below:
                # Player is lower - similar to no clear shot, move to edge
                on_platform = None
                for platform in self.game.platforms:
                    platform_check = platform.collision_rect if hasattr(platform, 'collision_rect') else platform.rect
                    if abs(self.rect.bottom - platform_check.top) < 5 and self.rect.centerx > platform_check.left and self.rect.centerx < platform_check.right:
                        on_platform = platform_check
                        break
                
                if on_platform:
                    if player_x > skeleton_x and self.rect.right < on_platform.right - 10:
                        self.vx = abs(self.vx) * 0.7  # Move toward right edge
                    elif player_x < skeleton_x and self.rect.left > on_platform.left + 10:
                        self.vx = -abs(self.vx) * 0.7  # Move toward left edge
                    else:
                        self.vx = 0  # At edge
                else:
                    self.vx = 0
            else:
                # Perfect position - clear shot, good range, similar height
                self.vx = 0
        
        # Move horizontally
        self.rect.x += self.vx
        
        # Look ahead to detect edges/lava and prepare to jump
        test_rect = self.rect.copy()
        test_rect.x += self.vx * 3  # Look 3 pixels ahead
        test_rect.y += 40  # Check below
        
        will_fall_into_lava = False
        will_fall_off_platform = True
        
        # Check if there's lava ahead
        for lava in self.game.lava:
            if test_rect.colliderect(lava.rect):
                will_fall_into_lava = True
        
        # Check if there's a platform ahead
        for platform in self.game.platforms:
            platform_check = platform.collision_rect if hasattr(platform, 'collision_rect') else platform.rect
            if test_rect.colliderect(platform_check):
                will_fall_off_platform = False
        
        # Jump if about to fall or if player is on different platform
        if (will_fall_into_lava or will_fall_off_platform) and self.on_ground and self.jump_cooldown == 0:
            if len(player_arr) > 0:
                player = player_arr[0]
                # Jump toward player's platform
                if abs(player.rect.centery - self.rect.centery) > 50:
                    self.vy = random.randrange(-14, -10)
                    self.jump_cooldown = 35
        
        # Jump cooldown
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
        
        # Only jump if not near lava
        near_lava = False
        for lava in self.game.lava:
            if abs(self.rect.bottom - lava.rect.top) < 100:  # Within 100 pixels of lava
                near_lava = True
                break
        
        # Intelligent jumping to reach player on different platforms or get clear shots
        if self.on_ground and not near_lava and self.jump_cooldown == 0 and len(player_arr) > 0:
            player = player_arr[0]
            vertical_dist = abs(self.rect.centery - player.rect.centery)
            horizontal_dist = abs(self.rect.centerx - player.rect.centerx)
            
            # Check if skeleton has clear shot (from earlier calculation)
            has_clear_shot = True
            blocking_platform = None
            for platform in self.game.platforms:
                platform_check = platform.collision_rect if hasattr(platform, 'collision_rect') else platform.rect
                if self.rect.centerx < player.rect.centerx:
                    if platform_check.left < player.rect.centerx and platform_check.right > self.rect.centerx:
                        if self.rect.centery < platform_check.top < player.rect.centery or player.rect.centery < platform_check.top < self.rect.centery:
                            has_clear_shot = False
                            blocking_platform = platform_check
                            break
                else:
                    if platform_check.right > player.rect.centerx and platform_check.left < self.rect.centerx:
                        if self.rect.centery < platform_check.top < player.rect.centery or player.rect.centery < platform_check.top < self.rect.centery:
                            has_clear_shot = False
                            blocking_platform = platform_check
                            break
            
            # Find platforms above and below current position for strategic movement
            platforms_above = []
            platforms_below = []
            current_platform_y = self.rect.bottom
            
            for platform in self.game.platforms:
                platform_check = platform.collision_rect if hasattr(platform, 'collision_rect') else platform.rect
                # Check if platform is horizontally reachable
                if abs(platform_check.centerx - self.rect.centerx) < 200:
                    if platform_check.top < current_platform_y - 50:  # Platform above
                        jump_distance = current_platform_y - platform_check.top
                        if jump_distance < 200:  # Reachable with jump
                            platforms_above.append((platform_check, jump_distance))
                    elif platform_check.top > current_platform_y + 50:  # Platform below
                        platforms_below.append((platform_check, platform_check.top - current_platform_y))
            
            # Decide whether to jump to a different platform for better positioning
            should_change_platform = False
            target_is_above = player.rect.centery < self.rect.centery
            
            if not has_clear_shot and blocking_platform:
                # Shot is blocked - try to get above or below the blocking platform
                if player.rect.centery < blocking_platform.top and self.rect.centery > blocking_platform.top:
                    # Player is above blocking platform, skeleton is below - need to jump up
                    if platforms_above and random.random() < 0.25:
                        should_change_platform = True
                        # Jump to reach higher platform
                        closest_above = min(platforms_above, key=lambda x: x[1])
                        jump_strength = min(-12, -10 - closest_above[1] // 30)
                        self.vy = jump_strength
                        self.jump_cooldown = 25
                elif player.rect.centery > blocking_platform.bottom and self.rect.centery < blocking_platform.bottom:
                    # Player is below blocking platform, skeleton is above - walk off edge to drop down
                    if platforms_below and random.random() < 0.2:
                        should_change_platform = True
                        # Move toward edge to drop down (handled by movement logic)
            
            if not should_change_platform:
                # Standard jumping logic
                # Jump if no clear shot and player is on different level
                if not has_clear_shot and vertical_dist > 80 and horizontal_dist < 350:
                    # Jump to get better position
                    if random.random() < 0.2:  # 20% chance per frame when blocked
                        self.vy = random.randrange(-15, -11)
                        self.jump_cooldown = 30
                # Jump UP to higher platform if player is significantly higher
                elif target_is_above and vertical_dist > 100 and horizontal_dist < 300:
                    if platforms_above and random.random() < 0.22:
                        # Calculate jump needed to reach platform above
                        closest_above = min(platforms_above, key=lambda x: x[1])
                        jump_strength = min(-12, -10 - closest_above[1] // 30)
                        self.vy = jump_strength
                        self.jump_cooldown = 30
                # Move to edge to DROP DOWN to lower platform if player is lower
                elif not target_is_above and vertical_dist > 100 and horizontal_dist < 300:
                    if platforms_below and random.random() < 0.18:
                        # Just walk off the edge (gravity will handle the drop)
                        # Movement logic will push skeleton toward edge
                        pass
                # Jump if player is significantly higher and within shooting range
                elif player.rect.centery < self.rect.centery - 80 and horizontal_dist < 300:
                    if random.random() < 0.18:  # 18% chance to jump up toward player
                        self.vy = random.randrange(-16, -12)  # Strong jump upward
                        self.jump_cooldown = 35
                # Jump if too close to player (escape)
                elif horizontal_dist < 100 and random.random() < 0.12:
                    self.vy = random.randrange(-13, -10)
                    self.jump_cooldown = 40
        
        # Update sprite direction with walking animation (unless shooting)
        if not self.shooting:
            if self.vx < 0:
                # Walking left - animate
                self.walk_timer += 1
                if self.walk_timer >= 10:
                    self.walk_timer = 0
                    self.walk_frame = 1 - self.walk_frame
                if self.walk_frame == 1:
                    try:
                        self.image = pg.image.load('images/enemies/skeleton_walk_0.png')
                    except:
                        self.image = sleft
                else:
                    self.image = sleft
            elif self.vx > 0:
                # Walking right - animate
                self.walk_timer += 1
                if self.walk_timer >= 10:
                    self.walk_timer = 0
                    self.walk_frame = 1 - self.walk_frame
                if self.walk_frame == 1:
                    try:
                        self.image = pg.image.load('images/enemies/skeleton_walk_1.png')
                    except:
                        self.image = sright
                else:
                    self.image = sright
        
        # Shooting: fire arrows toward the player when in range
        if len(player_arr) > 0:
            player = player_arr[0]
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            horiz_dist = abs(dx)
            vert_dist = abs(dy)
            # Only shoot if player is within a reasonable range and cooldown elapsed
            if self.shoot_timer <= 0 and horiz_dist < 450 and vert_dist < 200:
                # Show shooting animation
                self.shooting = True
                self.shoot_frame = 0
                
                arrow = Arrow(self.game, (self.rect.centerx, self.rect.centery), (player.rect.centerx, player.rect.centery))
                self.game.all_sprites.add(arrow)
                # Ensure skeleton_arrows group exists on game
                if hasattr(self.game, 'skeleton_arrows'):
                    self.game.skeleton_arrows.add(arrow)
                else:
                    self.game.skeleton_arrows = pg.sprite.Group()
                    self.game.skeleton_arrows.add(arrow)
                # Small random delay until next shot (balanced)
                self.shoot_timer = random.randint(40, 90)  # Increased fire rate
            
            # Update shooting animation
            if self.shooting:
                self.shoot_frame += 1
                if self.shoot_frame >= 5:  # 5 frame shooting animation
                    self.shooting = False
                else:
                    # Show different shoot frames during animation (0-4)
                    # Cycle through available frames for smooth animation
                    frame_index = min(self.shoot_frame, 1)  # Use frames 0 and 1
                    try:
                        if self.vx < 0:
                            self.image = pg.image.load(f'images/enemies/skeleton_shoot_0.png')
                        else:
                            self.image = pg.image.load(f'images/enemies/skeleton_shoot_1.png')
                    except:
                        pass  # Fall back to walk/idle animation

        # Decrease shoot timer
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
    
    def take_damage(self, damage=1):
        """Damage the skeleton"""
        self.health -= damage
        if self.health <= 0:
            # Chance to drop powerup on death (higher for elite)
            drop_chance = 0.15 if self.is_elite else 0.08
            if random.random() < drop_chance:
                powerup_type = random.choice(Powerup.TYPES)
                powerup = Powerup(self.game, self.rect.centerx, self.rect.centery, powerup_type)
                self.game.all_sprites.add(powerup)
                self.game.powerups.add(powerup)
                powerup_arr.append(powerup)
            
            # Play skeleton-specific death sound if available
            try:
                snd = globals().get('skeleton_death_sound', None)
                if snd:
                    snd.play()
            except Exception:
                pass
            self.kill()
            if self in skel_arr:
                skel_arr.remove(self)


class Particle(pg.sprite.Sprite):
    """Visual particle effect for damage hits and attacks"""
    def __init__(self, game, x, y, vx, vy, color, lifetime=30, size=8):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self._layer = particle_layer
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.image = pg.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
    def update(self):
        """Update particle position and lifetime"""
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Gravity effect
        self.lifetime -= 1
        
        # Fade out
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        self.image = pg.Surface((self.size, self.size), pg.SRCALPHA)
        color_with_alpha = (*self.color, alpha)
        pg.draw.circle(self.image, color_with_alpha, (self.size // 2, self.size // 2), self.size // 2)
        
        self.rect.center = (int(self.x), int(self.y))
        
        if self.lifetime <= 0:
            self.kill()


class Powerup(pg.sprite.Sprite):
    """Powerup item that floats down and gives temporary bonuses"""
    TYPES = ['shield', 'damage', 'speed', 'freeze']
    COLORS = {
        'shield': (100, 150, 255),   # Blue
        'damage': (255, 50, 50),      # Red
        'speed': (255, 200, 0),       # Orange
        'freeze': (150, 255, 255)     # Cyan
    }
    
    def __init__(self, game, x, y, powerup_type='shield'):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self._layer = powerup_layer
        
        if powerup_type not in self.TYPES:
            powerup_type = random.choice(self.TYPES)
        
        self.type = powerup_type
        self.size = 40
        self.color = self.COLORS[powerup_type]
        
        # Load powerup image or create fallback
        try:
            image_path = f'images/powerup_{powerup_type}.png'
            if path.exists(image_path):
                self.image = pg.image.load(image_path)
            else:
                # Fallback: create colored circle
                self.image = pg.Surface((self.size, self.size), pg.SRCALPHA)
                pg.draw.circle(self.image, self.color, (self.size // 2, self.size // 2), self.size // 2)
                pg.draw.circle(self.image, WHITE, (self.size // 2, self.size // 2), self.size // 3)
        except Exception:
            # Fallback if loading fails
            self.image = pg.Surface((self.size, self.size), pg.SRCALPHA)
            pg.draw.circle(self.image, self.color, (self.size // 2, self.size // 2), self.size // 2)
            pg.draw.circle(self.image, WHITE, (self.size // 2, self.size // 2), self.size // 3)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vy = 2  # Fall speed
        self.rotation = 0
        self.lifetime = 600  # 20 seconds at 30 FPS
    
    def update(self):
        """Update powerup position and animation"""
        self.rect.y += self.vy
        self.rotation += 5
        
        # Remove if fallen off screen or expired
        if self.rect.y > HEIGHT or self.lifetime <= 0:
            self.kill()
            if self in powerup_arr:
                powerup_arr.remove(self)
        
        self.lifetime -= 1
    
    def apply(self, player):
        """Apply powerup effect to player"""
        if self.type == 'shield':
            player.shield_active = True
            player.shield_time = 300  # 10 seconds
        elif self.type == 'damage':
            player.damage_boost_active = True
            player.damage_boost_time = 300
            player.damage_boost_mult = 1.5
        elif self.type == 'speed':
            player.speed_boost_active = True
            player.speed_boost_time = 300
            player.speed_mult_boost = 1.5
        elif self.type == 'freeze':
            # Freeze all enemies for 5 seconds
            for enemy_group in [self.game.goblins, self.game.skeletons, self.game.monster]:
                for enemy in enemy_group:
                    enemy.frozen = True
                    enemy.frozen_time = 150  # 5 seconds
        
        self.kill()
        if self in powerup_arr:
            powerup_arr.remove(self)


# Global powerup array
powerup_arr = []






