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
        play_song('sounds/uzi_music.mp3')
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)

    def new(self):
        # start new game
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.lava = pg.sprite.Group()
        self.coins = pg.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        self.monster = Monster(self)
        self.all_sprites.add(self.monster)
        for plat in PLATFORM_LIST:
            p = Platform(*plat)
            self.all_sprites.add(p)
            self.platforms.add(p)
        bottom_lava = Lava(0, HEIGHT - 40, 800, 20)
        self.all_sprites.add(bottom_lava)
        self.lava.add(bottom_lava)
        self.run()

    def run(self):
        # game loops
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
            hits_plat = pg.sprite.spritecollide(self.player, self.platforms, False)
            hits_lava = pg.sprite.spritecollide(self.player, self.lava, False)
            if hits_plat:
                self.player.pos.y = hits_plat[0].rect.top
                self.player.vel.y = 0
            # DEATH
            if hits_lava:
                play_song('sounds/death_song.mp3')
                self.player.pos.y = hits_lava[0].rect.top
                self.player.vel.y = 0
                for sprite in self.all_sprites:
                    sprite.rect.y -= int(max(self.player.vel.y, 10))
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
                if event.key == pg.K_UP:
                    self.player.jump()
                if event.key == pg.K_w:
                    self.player.jump()

    def draw(self):
        # game loop draw poop
        # self.screen.blit(game_background, (0, 0))
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self.draw_text("LEVEL: ", 20, WHITE, WIDTH * 3 / 4, HEIGHT-5)
        # *after* drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        # game start screen
        self.playing = True
        if (pg.time.get_ticks() % 2000) <= 500:
            self.screen.blit(start_background0, (0, 0))
        if (pg.time.get_ticks() % 2000) <= 1000:
            self.screen.blit(start_background1, (0, 0))
        # if (pg.time.get_ticks() % 2000) <= 1500:
        #    self.screen.blit(start_background2, (0, 0))
        # if (pg.time.get_ticks() % 2000) <= 2000:
        #    self.screen.blit(start_background3, (0, 0))

        pg.display.flip()
        self.wait_for_key()

    def show_pause_screen(self):
        # game start screen
        pass

    def show_go_screen(self):
        # game over screen
        game_over_sound.play()
        if not self.running:
            return
        self.screen.blit(end_background, (0, 0))
        pg.display.flip()
        self.wait_for_key()
        game_over_sound.stop()
        pg.mixer.music.unpause()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    print(current_song)
                    if event.key == pg.K_RETURN and current_song != 'sounds/uzi_music.mp3':
                        play_song('sounds/uzi_music.mp3')
                        waiting = False
                    if event.key == pg.K_ESCAPE:
                        if self.playing:
                            self.playing = False
                        self.running = False

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




