# player and enemy classes for game
from settings import *
import pygame as pg

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
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
            self.image = pleft
        if keys[pg.K_RIGHT]:
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


class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((w, h))
        self.rect = self.image.get_rect()
        self.image = platform_skin
        self.rect.x = x
        self.rect.y = y
        #why this not working


class Monster(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = hamel
        self.rect = self.image.get_rect()
        self.pos = vec(WIDTH /2, HEIGHT / 2)

    def move_towards_player(self, player):
        dx, dy = player.rect.x - self.rect.x, player.rect.y - self.rect.y
        dist = math.hypot(dx, dy)
        dx, dy = dx / dist, dy / dist

        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed





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

