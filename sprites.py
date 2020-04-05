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
        self.pos = vec(WIDTH /2, HEIGHT / 2)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.lives = 3
        self.hearts = float(100)

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
        if self.image == pright:
            self.image = prighth
        if self.image == pleft:
            self.image = plefth

    def update(self):
        self.acc = vec(0, PLAYER_GRAV)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] | keys[pg.K_a]:
            self.acc.x = -PLAYER_ACC
            if self.vel.y >= 0:
                self.image = pleft
            if self.vel.y < 0:
                self.image = pleftj
        if keys[pg.K_RIGHT] | keys[pg.K_d]:
            self.acc.x = PLAYER_ACC
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

    def get_pos_x(self):
        return self.rect.x

    def get_pos_y(self):
        return self.rect.y


class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self._layer = platform_layer
        self.image = pg.Surface((w, h))
        self.rect = self.image.get_rect()
        if w == 320:
            self.image = platform_320
        if w == 100:
            self.image = platform_100
        if w == 150:
            self.image = platform_150
        self.rect.x = x
        self.rect.y = y


class Monster(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = hamel_monster
        self._layer = monster_layer
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vx = 5

    def update(self):
        self.rect.x += self.vx
        if self.rect.x >= WIDTH - 128:
            self.vx = -self.vx
        if self.rect.x == 0:
            self.vx = -self.vx



"""class Monster(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = hamel_monster
        self.rect = self.image.get_rect()
        self.pos = vec(WIDTH / 2, HEIGHT / 2)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.speedx = 10

    def move_towards_player(self, player):
        # Find direction vector (dx, dy) between enemy and player.
        dx, dy = player.rect.x - self.rect.x, player.rect.y - self.rect.y
        dist = math.hypot(dx, dy)
        dx, dy = dx / dist, dy / dist 
        # Normalize.
        # Move along this normalized vector towards the player at current speed.
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

    def update(self):
        self.acc = vec(0, 0)
        if self.pos.x > WIDTH:
            self.speedx = -10
        if self.pos.x < 0:
            self.speedx = 10

    def shoot(self, game):
        self.game = game
        self.image = hamel_open"""


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

        y_pos = PLATFORM_LIST[j][1] - 15
        x_pos = random.randrange(PLATFORM_LIST[j][0], PLATFORM_LIST[j][0] + PLATFORM_LIST[j][2] - 10)
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
        for coi in coin_arr:
            if abs(coi.rect.x - player_arr[0].rect.x) < 10 and abs(coi.rect.y - player_arr[0].rect.y) < 20:
                self.game.score += 100
                coin_sound.play()
                self.game.coin_count -= 1
                coi.kill()
                coin_arr.remove(coi)


class MonsterBullet(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self._layer = projectile_layer
        self.image = lava_ball
        self.rect = self.image.get_rect()
        self.pos = vec(WIDTH / 2, HEIGHT / 2)
        y_pos = 125
        x_pos = monster_arr[0].rect.x
        self.rect.y = y_pos
        self.rect.x = x_pos
        self.speedx = random.randrange(-10, 10)
        self.speedy = random.randrange(5, 15)
        hamel_sound.play()

    def update(self):
        self.rect.y += self.speedy
        self.rect.x -= self.speedx
        if self.rect.y > HEIGHT - 60:
            self.kill()
        if self.rect.x < 0 | self.rect.x > WIDTH:
            self.kill()


class Goblin(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self._layer = mob_layer
        self.image_left = gleft
        self.image_right = gright
        self.image = gleft
        self.rect = self.image.get_rect()
        self.vx = MOB_SPEED
        self.x_upper_bound = 0
        # Goblin is 20px wide and 30px tall
        i = 2
        while i == 2:
            i = random.randrange(5)

        y_pos = PLATFORM_LIST[i][1] - 30
        x_pos = random.randrange(PLATFORM_LIST[i][0], PLATFORM_LIST[i][0] + PLATFORM_LIST[i][2] - 20)

        self.x_lower_bound = PLATFORM_LIST[i][0]
        self.x_upper_bound = PLATFORM_LIST[i][0] + PLATFORM_LIST[i][2]-20

        self.spawn_platform = PLATFORM_LIST[i]
        self.rect.y = y_pos
        self.rect.x = x_pos

    def update(self):
        for gob in goblins_arr:
            for i in range(0, len(goblins_arr)):
                diff_sign = False
                if gob is not goblins_arr[i] and gob.vx < 0 and goblins_arr[i].vx > 0 or gob.vx > 0 and goblins_arr[i].vx < 0:
                    diff_sign = True
                if gob is not goblins_arr[i] and abs(gob.rect.x - goblins_arr[i].rect.x) < 20 \
                        and abs(gob.rect.y - goblins_arr[i].rect.y) < 20:
                    self.vx = -self.vx
                    goblins_arr[i].vx = -goblins_arr[i].vx
        if self.rect.x > self.x_upper_bound:
            self.vx = -self.vx
        if self.rect.x < self.x_lower_bound:
            self.vx = -self.vx
        self.rect.x += self.vx
        if self.vx < 0:
            self.image = gleft
        if self.vx > 0:
            self.image = gright


class Skeleton(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self._layer = mob_layer
        self.image = sleft
        self.rect = self.image.get_rect()
        self.vx = 4
        self.x_upper_bound = 0
        # Skeleton is 20px wide and 30px tall
        i = 2
        while i == 2:
            i = random.randrange(5)

        y_pos = PLATFORM_LIST[i][1] - 30
        x_pos = random.randrange(PLATFORM_LIST[i][0], PLATFORM_LIST[i][0] + PLATFORM_LIST[i][2]-20)

        self.x_lower_bound = PLATFORM_LIST[i][0]
        self.x_upper_bound = PLATFORM_LIST[i][0] + PLATFORM_LIST[i][2]-20

        self.spawn_platform = PLATFORM_LIST[i]
        self.rect.y = y_pos
        self.rect.x = x_pos








