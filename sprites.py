# player and enemy classes for game
from settings import *
import pygame as pg
import random
import math

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
        self.pos = vec(WIDTH /2, HEIGHT / 2)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.lives = 3
        self.attacking = False
        self.attack_timer = 0
        self.facing_right = False
        self.attack_combo = 0  # Track combo hits
        self.last_attack_time = 0  # Track time for combo window
        # Mana settings
        self.mana_regen_rate = 0.2  # Mana per frame
        self.fireball_cost = 15  # Cost to cast fireball (reduced for balance)
        self.fireball_cooldown = 0  # Cooldown timer

    def jump(self):
        # only jump if on platform
        self.rect.y += 1
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 1
        if hits:
            jump_sound.play()
            self.vel.y = PLAYER_JUMP
            self.image = pright

    def hit(self):
        sword_swing.play()
        current_time = pg.time.get_ticks()
        
        # Don't increment combo here - only on successful hit
        # Store last attack time for combo window tracking
        self.last_attack_time = current_time
        self.attacking = True
        self.attack_timer = 12 if self.attack_combo >= 2 else 10  # Longer attack for combos
        
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
        else:
            self.attack_combo = 1  # Reset combo

    def update(self):
        # Handle attack timer
        if self.attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attacking = False
        
        # Regenerate mana
        if self.mana < self.max_mana:
            self.mana = min(self.mana + self.mana_regen_rate, self.max_mana)
        
        # Fireball cooldown
        if self.fireball_cooldown > 0:
            self.fireball_cooldown -= 1
        
        self.acc = vec(0, PLAYER_GRAV)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] | keys[pg.K_a]:
            # Apply player's speed multiplier
            self.acc.x = -PLAYER_ACC * self.speed_mult
            self.facing_right = False
            if self.vel.y >= 0:
                self.image = pleft
            if self.vel.y < 0:
                self.image = pleftj
        if keys[pg.K_RIGHT] | keys[pg.K_d]:
            self.acc.x = PLAYER_ACC * self.speed_mult
            self.facing_right = True
            if self.vel.y >= 0:
                self.image = pright
            if self.vel.y < 0:
                self.image = prightj

        # slows player down over time
        self.acc.x += self.vel.x * PLAYER_FRICTION

        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # wrap around screen
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos
    
    def cast_fireball(self, target_pos):
        """Cast a fireball toward the target position (mouse cursor)"""
        if self.mana >= self.fireball_cost and self.fireball_cooldown == 0:
            self.mana -= self.fireball_cost
            self.fireball_cooldown = 30  # 1 second cooldown at 30 FPS
            return Fireball(self.game, self.rect.center, target_pos)
        return None
    
    def get_attack_rect(self):
        """Returns the hitbox for sword attack"""
        if not self.attacking:
            return None
        
        # Attack range increases with combo (reduced scaling)
        base_range = 30
        attack_range = base_range + (self.attack_combo - 1) * 5  # +5 pixels per combo level (was 10)
        attack_height = 25 + (self.attack_combo - 1) * 3  # Slightly taller hitbox for combos (was 5)
        
        if self.facing_right:
            # Attack to the right
            attack_rect = pg.Rect(self.rect.right, self.rect.centery - attack_height // 2, 
                                 attack_range, attack_height)
        else:
            # Attack to the left
            attack_rect = pg.Rect(self.rect.left - attack_range, self.rect.centery - attack_height // 2, 
                                 attack_range, attack_height)
        
        return attack_rect
    
    def get_attack_damage(self):
        """Returns damage based on combo level"""
        return self.attack_combo  # 1, 2, or 3 damage based on combo

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
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        # Use the generated medieval monster sprite if available
        try:
            self.image = monster_medieval
        except NameError:
            self.image = monster
        self._layer = monster_layer
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vx = 5
        self.health = 50  # Boss has 50 HP
        self.max_health = 50
        # Create a smaller hitbox for player damage (just the moving box part)
        # The monster image is 128x128, the actual moving box is roughly in the middle
        self.damage_hitbox = pg.Rect(0, 0, 60, 60)  # Smaller hitbox for the box
        self.update_hitbox()
    
    def update_hitbox(self):
        """Update the damage hitbox position to follow the monster"""
        # Center the damage hitbox on the monster's center
        self.damage_hitbox.centerx = self.rect.centerx
        self.damage_hitbox.centery = self.rect.centery

    def update(self):
        self.rect.x += self.vx
        if self.rect.x >= WIDTH - 128:
            self.vx = -self.vx
        if self.rect.x == 0:
            self.vx = -self.vx
        self.update_hitbox()  # Keep hitbox in sync
    
    def take_damage(self, damage=1):
        """Damage the monster boss"""
        self.health -= damage
        if self.health <= 0:
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
        self.image = pg.Surface((w, h))
        self.rect = self.image.get_rect()
        self.image = lava
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

        y_pos = platform_arr[j][1] - 15
        x_pos = random.randrange(platform_arr[j][0], platform_arr[j][0] + platform_arr[j][2] - 10)
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
        if len(platform_arr) > 0:
            plat_index = random.randrange(len(platform_arr))
            y_pos = platform_arr[plat_index][1] - 25
            x_pos = random.randrange(platform_arr[plat_index][0], 
                                     platform_arr[plat_index][0] + platform_arr[plat_index][2] - 20)
            self.rect.y = y_pos
            self.rect.x = x_pos

    def update(self):
        # Check for player collision
        if len(player_arr) > 0:
            if abs(self.rect.x - player_arr[0].rect.x) < 15 and abs(self.rect.y - player_arr[0].rect.y) < 25:
                # Heal player (cap at 100)
                player_arr[0].hearts = min(player_arr[0].hearts + self.heal_amount, 100)
                coin_sound.play()  # Reuse coin sound for pickup
                self.kill()


class MonsterBullet(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self._layer = projectile_layer
        self.image = lava_ball
        self.rect = self.image.get_rect()
        self.pos = vec(WIDTH / 2, HEIGHT / 2)
        y_pos = 125
        # Safety check to avoid crashes when monster_arr is empty
        if len(monster_arr) > 0:
            x_pos = monster_arr[0].rect.x
        else:
            x_pos = WIDTH / 2  # Default position if no monster exists
        self.rect.y = y_pos
        self.rect.x = x_pos
        self.speedx = random.randrange(-10, 10)
        self.speedy = random.randrange(5, 15)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x -= self.speedx
        if self.rect.y > HEIGHT - 60:
            self.kill()
        if self.rect.x < 0 | self.rect.x > WIDTH:
            self.kill()


class Goblin(pg.sprite.Sprite):
    def __init__(self, game, is_elite=False, speed_mult=1.0):
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
        self.health = 5 if is_elite else 2  # Elite goblins take 5 hits
        self.max_health = self.health
        self.jump_cooldown = 0
        # Goblin attack system
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_range = 40  # How close goblin needs to be to attack
        
        # Goblin is 20px wide and 30px tall
        # Spread goblins across platforms, but avoid player spawn platform (center of screen)
        available_platforms = []
        player_spawn_x = WIDTH / 2
        player_spawn_y = HEIGHT / 2
        
        for idx, plat in enumerate(platform_arr):
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
        y_pos = int(platform_arr[i][1] - 30)
        x_start = int(platform_arr[i][0])
        x_end = int(min(platform_arr[i][0] + platform_arr[i][2] - 20, WIDTH - 20))
        # Ensure range is valid for randrange
        if x_end <= x_start:
            x_pos = x_start
        else:
            x_pos = random.randrange(x_start, x_end)

        self.current_platform = i
        self.rect.y = y_pos
        self.rect.x = x_pos

    def update(self):
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
        test_rect = self.rect.copy()
        test_rect.x += self.vx * 3  # Look 3 pixels ahead
        test_rect.y += 40  # Check below
        
        will_fall_into_lava = False
        will_fall_off_platform = True
        
        # Check if there's lava ahead and below
        for lava in self.game.lava:
            if test_rect.colliderect(lava.rect):
                will_fall_into_lava = True
        
        # Check if there's a platform ahead
        for platform in self.game.platforms:
            if test_rect.colliderect(platform.rect):
                will_fall_off_platform = False
        
        # Turn around if would fall into lava or off platform edge
        if self.on_ground and (will_fall_into_lava or will_fall_off_platform):
            self.vx = -self.vx
        
        # Movement
        self.rect.x += self.vx
        
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
        
        # Reverse direction at edges or randomly
        if random.random() < 0.01:  # 1% chance to randomly turn
            self.vx = -self.vx
        
        # Wrap around screen edges
        if self.rect.x < 0:
            self.rect.x = WIDTH
        if self.rect.x > WIDTH:
            self.rect.x = 0
        
        # Update sprite direction
        if self.vx < 0:
            self.image = gleft
        if self.vx > 0:
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
    def __init__(self, game, is_elite=False, speed_mult=1.0):
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
        self.health = 6 if is_elite else 3  # Elite skeletons take 6 hits
        self.max_health = self.health
        # Increase base cooldown to reduce firing frequency
        self.shoot_timer = random.randint(90, 180)  # frames until next possible shot
        # Skeleton is 20px wide and 30px tall
        # Find a platform, but avoid player spawn platform (center of screen)
        available_platforms = []
        player_spawn_x = WIDTH / 2
        player_spawn_y = HEIGHT / 2
        
        for idx, plat in enumerate(platform_arr):
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
            for idx, plat in enumerate(platform_arr):
                plat_x = plat[0]
                plat_y = plat[1]
                plat_w = plat[2]
                if abs((plat_x + plat_w/2) - player_spawn_x) < 150 and abs(plat_y - player_spawn_y) < 100:
                    continue
                available_platforms.append(idx)
            i = random.choice(available_platforms) if len(available_platforms) > 0 else 0
        else:
            i = random.choice(available_platforms)
            platform_arr[i][4] = platform_arr[i][4] - 1

        y_pos = platform_arr[i][1] - 30
        x_pos = random.randrange(platform_arr[i][0], platform_arr[i][0] + platform_arr[i][2] - 20)

        self.x_lower_bound = platform_arr[i][0]
        self.x_upper_bound = platform_arr[i][0] + platform_arr[i][2] - 20

        self.spawn_platform = platform_arr[i]
        self.rect.y = y_pos
        self.rect.x = x_pos

    def update(self):
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
        
        # Smart AI: Follow the player and move around
        if len(player_arr) > 0:
            player = player_arr[0]
            player_x = player.rect.centerx
            skeleton_x = self.rect.centerx
            
            # Determine desired direction toward player
            if player_x > skeleton_x + 10:  # Player is to the right
                self.vx = abs(self.vx)  # Move right
            elif player_x < skeleton_x - 10:  # Player is to the left
                self.vx = -abs(self.vx)  # Move left
        
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
        
        # Intelligent jumping to reach player on different platforms
        if self.on_ground and not near_lava and self.jump_cooldown == 0 and len(player_arr) > 0:
            player = player_arr[0]
            vertical_dist = abs(self.rect.centery - player.rect.centery)
            horizontal_dist = abs(self.rect.centerx - player.rect.centerx)
            
            # Jump if player is on different platform and within range
            if vertical_dist > 50 and horizontal_dist < 300:
                # Much higher chance to jump when player is on different platform
                if random.random() < 0.15:  # 15% chance per frame
                    self.vy = random.randrange(-15, -11)  # Stronger, more varied jump
                    self.jump_cooldown = 35  # Shorter cooldown for aggressive pursuit
            elif horizontal_dist < 150 and random.random() < 0.08:  # Jump toward nearby player
                self.vy = random.randrange(-13, -10)
                self.jump_cooldown = 40
        
        # Update sprite direction
        if self.vx < 0:
            self.image = sleft
        if self.vx > 0:
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
                arrow = Arrow(self.game, (self.rect.centerx, self.rect.centery), (player.rect.centerx, player.rect.centery))
                self.game.all_sprites.add(arrow)
                # Ensure skeleton_arrows group exists on game
                if hasattr(self.game, 'skeleton_arrows'):
                    self.game.skeleton_arrows.add(arrow)
                else:
                    self.game.skeleton_arrows = pg.sprite.Group()
                    self.game.skeleton_arrows.add(arrow)
                # Small random delay until next shot (balanced)
                self.shoot_timer = random.randint(90, 180)

        # Decrease shoot timer
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
    
    def take_damage(self, damage=1):
        """Damage the skeleton"""
        self.health -= damage
        if self.health <= 0:
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






