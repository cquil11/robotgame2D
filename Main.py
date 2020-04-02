import pygame as pg
import random
from settings import *
from sprites import *
import os

class Game:
    def __init__(self):
        # initialize game windows
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("My Game")
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)

    def new(self):
        # start new game
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        self.monster = Monster(self)
        self.all_sprites.add(self.monster)
        for plat in PLATFORM_LIST:
            p = Platform(*plat)
            self.all_sprites.add(p)
            self.platforms.add(p)
        self.run()

    def run(self):
        # game loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        # game loop update
        self.all_sprites.update()
        # check if player hits platform
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                self.player.pos.y = hits[0].rect.top
                self.player.vel.y = 0
        # DEATH
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= (int)(max(self.player.vel.y, 10))
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

    def events(self):
        # game loop events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()

    def draw(self):
        # game loop draw
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self.draw_text("LEVEL: ", 22, WHITE, WIDTH/2, 15)
        # *after* drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        # game start screen
        self.screen.blit(start_background1, (0, 0))
        self.draw_text(TITLE, 48, RED, WIDTH / 2, 48)
        self.draw_text("Use left and right arrow keys to move and space to jump", 20, RED, WIDTH / 2, HEIGHT - 50)
        self.draw_text("PRESS ANY KEY TO PLAY", 20, RED, WIDTH / 2, HEIGHT / 2)
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        # game over screen
        pg.mixer.music.play(go_music, 0)
        if not self.running:
            return
        self.screen.blit(end_background, (0, 0))
        self.draw_text("GAME OVER", 60, RED, WIDTH / 2, 48)
        self.draw_text("PRESS ANY KEY TO PLAY AGAIN", 35, WHITE, WIDTH / 2, HEIGHT - 100)
        self.draw_text("FINAL LEVEL: ", 35, WHITE, WIDTH / 2, HEIGHT / 2)
        pg.display.flip()
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
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.QUIT




