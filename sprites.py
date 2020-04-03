# player and enemy classes for game
from settings import *
import pygame as pg
import math

vec = pg.math.Vector2


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pleft
        self.rect = self.image.get_rect()
        self.pos = vec(WIDTH /2, HEIGHT / 2)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def jump(self):
        # only jump if on platform
        self.rect.y += 1
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 1
        if hits:
            self.vel.y = PLAYER_JUMP

    def update(self):
        self.acc = vec(0, PLAYER_GRAV)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] | keys[pg.K_a]:
            self.acc.x = -PLAYER_ACC
            self.image = pleft
        if keys[pg.K_RIGHT] | keys[pg.K_d]:
            self.acc.x = PLAYER_ACC
            self.image = pright

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


class PlayerImage(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((w, h))
        self.rect = self.image.get_rect()
        self.image = lava
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
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


# test
class Monster(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = hamel
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 20
        self.velX = 5

    def update(self):
        dx = self.rect.x
        if dx < 0:
            self.rect.x += self.velX
        else:
            self.rect.x -= self.velX
            #why

        if self.rect.x > WIDTH - 128:
            self.velX = -self.velX
        if self.rect.x < 0:
            self.velX = -self.velX

    def move_towards_player(self, player):
        dx = player.rect.x - self.rect.x

        print(dx)

        if dx < 0:
            self.acc = BOSS_ACC
        else:
            self.acc = -BOSS_ACC

        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc


class Lava(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((w, h))
        self.rect = self.image.get_rect()
        self.image = lava
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((w, h))
        self.rect = self.image.get_rect()
        self.image = lava
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class MonsterBullet(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = hamel_open
        self.rect = self.image.get_rect()
        self.pos = vec(WIDTH / 2, HEIGHT / 2)


class Goblin(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = gleft
        self.rect = self.image.get_rect()
        self.pos = vec(WIDTH /2, HEIGHT / 2)

