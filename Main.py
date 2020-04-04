import pygame as pg
from pygame.locals import *
import random
from settings import *
from sprites import *
import os
import time


class Game:
    score = 0
    def __init__(self):
        # initialize game windows
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("My Game")
        self.clock = pg.time.Clock()
        play_song('sounds/computer_startup.mp3')
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)

    def new(self):
        # start new game
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.lava = pg.sprite.Group()
        self.goblins = pg.sprite.Group()
        self.coins = pg.sprite.Group()

        for i in range(0, 5):
            goblin = Goblin()
            self.all_sprites.add(goblin)
            self.goblins.add(goblin)
            goblins_arr.append(goblin)
        print(str(goblins_arr))
        print(goblins_arr[0].rect.x)
        print(goblins_arr[0].spawn_platform)
        print(goblins_arr[1].rect.x)
        print(goblins_arr[2].rect.x)
        for i in range(0, 4):
            coin = Coin()
            self.all_sprites.add(coin)
            self.coins.add(coin)
        self.coins = pg.sprite.Group()
        self.player = Player(self)
        self.monster = pg.sprite.Group()
        bullet = MonsterBullet(62, 95)
        self.monsterbullet = pg.sprite.Group()
        self.monsterbullet.add(bullet)
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.monster)
        # self.monster.add()
        self.all_sprites.add(self.monsterbullet)
        for plat in PLATFORM_LIST:
            p = Platform(*plat)
            self.all_sprites.add(p)
            self.platforms.add(p)
        bottom_lava = Lava(0, HEIGHT - 40, 800, 20)
        self.monsterbullet.add(bullet)
        self.all_sprites.add(bottom_lava)
        self.lava.add(bottom_lava)
        self.all_sprites.add(goblin)
        self.run()

    def run(self):
        # game loops

        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update(self.score)
            self.draw()

    def update(self, score):
        self.game_clock = pg.time.Clock()
        # game loop update
        self.all_sprites.update()
        score += 1
        # check if player hits platform
        if self.player.vel.y > 0:
            hits_plat = pg.sprite.spritecollide(self.player, self.platforms, False)
            hits_lava = pg.sprite.spritecollide(self.player, self.lava, False)
            hits_bullet = pg.sprite.spritecollide(self.player, self.monsterbullet, False)
            hits_goblin = pg.sprite.spritecollide(self.player, self.goblins, False)
            hits_coin = pg.sprite.spritecollide(self.player, self.coins, False)
            """hits_monster = pg.sprite.spritecollide(self.player, self.monster, False)"""
            if hits_plat:
                self.player.pos.y = hits_plat[0].rect.top
                self.player.vel.y = 0
            if hits_coin:
                score += 100
                coin.kill()
                return score
            # DEATH
            if hits_lava:
                self.player.pos.y = hits_lava[0].rect.bottom
                self.player.vel.y = 0
                for sprite in self.all_sprites:
                    sprite.rect.y -= int(max(self.player.vel.y, 10))
                pg.mixer.music.stop()
                self.player.hearts -= 100
                if self.player.hearts < 0:
                    lava_burning_sound.play()
                    scream_sound.play()
                    pg.time.wait(10500)
                    play_song('sounds/death_song.mp3')
                    self.playing = False
            elif hits_bullet:
                self.player.hearts -= 5
                if self.player.hearts < 0:
                    pg.mixer.music.stop()
                    play_song('sounds/death_song.mp3')
                    pg.time.wait(500)
                    self.playing = False
            elif hits_goblin:
                # if self.player.lives == 0:
                self.player.hearts -= 2.5
                death_sound_HIT.play()
                if self.player.hearts < 0:
                    pg.mixer.music.stop()
                    play_song('sounds/death_song.mp3')
                    pg.time.wait(500)
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
                    sword_swing.play()
                    self.player.hit()
                if event.key == pg.K_UP:
                    jump_sound.play()
                    self.player.jump()
                if event.key == pg.K_w:
                    jump_sound.play()
                    self.player.jump()

    def draw(self):
        # game loop draw poop
        # self.screen.blit(game_background, (0, 0))
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self.draw_text("LEVEL: ", 20, WHITE, WIDTH * 3 / 4, HEIGHT-22)
        self.draw_text("SCORE: " + str(SCORE), 20, WHITE, WIDTH * 2 / 4, HEIGHT - 22)
        self.draw_text("HEALTH: " + str(self.player.hearts), 20, WHITE, WIDTH * 1 / 4, HEIGHT - 22)
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

    def show_go_screen(self):
        # game over screen
        goblins_arr.clear()
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
        text_rect.midtop = (int(x), int(y))
        self.screen.blit(text_surface, text_rect)


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.QUIT




