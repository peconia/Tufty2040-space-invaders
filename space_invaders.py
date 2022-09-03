import time
import random
from pimoroni import Button
from picographics import PicoGraphics, DISPLAY_TUFTY_2040

display = PicoGraphics(display=DISPLAY_TUFTY_2040)
WIDTH, HEIGHT = display.get_bounds()

# Load the spritesheet. Note that it uses white as the "transparent" colour
character = bytearray(128 * 128)
open("space_invaders_spritesheet.rgb332", "rb").readinto(character)

display.set_spritesheet(character)

# Buttons
button_a = Button(7, invert=False)
button_b = Button(8, invert=False)
button_c = Button(9, invert=False)
button_up = Button(22, invert=False)
button_down = Button(6, invert=False)

display.set_backlight(1.0)
display.set_pen(255)
display.clear()


class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = 150
        self.y = 205
        self.w = 32  # 8 pixels scaled 4 times
        self.h = 32
        self.speed = 7
        self.is_alive = True
        self.lives = 3
        self.score = 0
        self.ammo = 100

    def move(self, x, y):
        if self.x + x > 0 - 15 and self.x + x < WIDTH - self.w + 10:
            self.x += x
            self.y += y

    def sprite(self):
        display.set_spritesheet(character)
        display.sprite(6, 0, self.x, self.y, 4, 255)

    def shoot(self):
        if self.ammo > 0:
            self.ammo -= 1
            bullet = Bullet(self.x + 15, self.y)
            return bullet


class Alien:
    def __init__(self, x, y, alien_type=1):
        self.w = 24  # 8 pixels scaled 3 times
        self.h = 24
        self.x = x
        self.y = y
        self.is_alive = True
        self.image_number = 1
        self.alien_type = alien_type
        self.movement_counter = 0
        self.animation_counter = 0

    def move(self):
        # the animation is too fast, slow it down a bit by only changing every now and again
        self.animation_counter += 1
        if self.animation_counter > 5:
            self.image_number *= -1
            self.animation_counter = 0

        # check if off screen
        if self.y > HEIGHT:
            self.is_alive = False

    def sprite(self):
        display.set_spritesheet(character)
        if self.alien_type == 1:
            display.sprite(0 if self.image_number > 0 else 1, 0, self.x, self.y, 3, 255)
        else:
            display.sprite(3 if self.image_number > 0 else 4, 0, self.x, self.y, 3, 255)
        self.move()

    def move_down(self):
        self.y += 10
        if self.movement_counter % 2 == 0:
            self.x += 10
        else:
            self.x -= 10
        self.movement_counter += 1

    def shoot(self):
        if not random.randrange(700):
            bullet = AlienBullet(self.x + self.w // 2, self.y + self.h)
            return bullet


class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 3  # 1 pixel scaled 3 times
        self.h = 6
        self.speed = 5
        self.is_alive = True

    def move(self):
        self.y -= self.speed
        if self.y < -self.h:
            self.is_alive = False

    def sprite(self):
        display.set_spritesheet(character)
        display.sprite(5, 0, self.x, self.y, 3, 255)


class AlienBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 3  # 1 pixel scaled 3 times
        self.h = 6
        self.speed = 2
        self.is_alive = True

    def move(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.is_alive = False

    def sprite(self):
        display.set_spritesheet(character)
        display.sprite(15, 0, self.x - 2, self.y, 3, 255)


class Ufo:
    def __init__(self):
        self.x = WIDTH + 30
        self.y = 30
        self.w = 24  # 1 pixel scaled 3 times
        self.h = 18
        self.speed = 3
        self.is_alive = True
        self.animation_counter = 0
        self.image_number = 1

    def move(self):
        # the animation is too fast, slow it down a bit by only changing every now and again
        self.animation_counter += 1
        if self.animation_counter > 5:
            self.image_number *= -1
            self.animation_counter = 0

        # check if off screen
        self.x -= self.speed
        if self.x < -self.w:
            self.is_alive = False

    def sprite(self):
        display.set_spritesheet(character)
        display.sprite(7 if self.image_number > 0 else 8, 0, self.x - 2, self.y, 3, 255)


class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_alive = True
        self.stage = 0

    def sprite(self):
        if self.stage >= 6:
            self.is_alive = False
        else:
            display.set_spritesheet(character)
            display.sprite(9 + self.stage, 0, self.x, self.y, 3, 255)
            self.stage += 1


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.ufo_sprites_list = []
        self.player_bullet_sprite_list = []
        self.alien_sprite_list = []
        self.alien_bullet_sprite_list = []
        self.explosions_sprite_list = []
        self.player = Player()
        self.SKY = display.create_pen(0, 0, 0)
        self.alien_move_interval = 100
        self.event_counter = 1

        # add in some aliens
        self.add_aliens()

    def level_up(self):
        self.add_aliens()
        self.player.ammo += 45
        self.event_counter = 1
        if self.alien_move_interval > 10:
            self.alien_move_interval -= 30

    def add_aliens(self):
        alien_type = 1
        for y in range(30, 180, 30):
            for x in range(15, 280, 32):
                alien = Alien(x, y, alien_type % 2)
                self.alien_sprite_list.append(alien)
            alien_type += 1

    def get_input(self):
        if button_c.read():
            self.player.move(self.player.speed, 0)
        if button_a.read():
            self.player.move(-self.player.speed, 0)
        if button_b.read():
            if self.player.is_alive:
                bullet = self.player.shoot()
                if bullet:
                    self.player_bullet_sprite_list.append(bullet)

    def update_spritelist(self, spritelist):
        # remove dead sprites and draw the rest
        live_sprites = [sprite for sprite in spritelist if sprite.is_alive]
        for sprite in live_sprites:
            sprite.sprite()
        return live_sprites

    def background(self):
        display.set_pen(self.SKY)
        display.clear()

    def draw(self):
        self.background()
        self.player.sprite()
        self.player_bullet_sprite_list = self.update_spritelist(self.player_bullet_sprite_list)
        self.alien_sprite_list = self.update_spritelist(self.alien_sprite_list)
        self.alien_bullet_sprite_list = self.update_spritelist(self.alien_bullet_sprite_list)
        self.ufo_sprites_list = self.update_spritelist(self.ufo_sprites_list)
        self.explosions_sprite_list = self.update_spritelist(self.explosions_sprite_list)
        display.set_pen(255)
        display.text("Score: " + str(self.player.score), 10, 10, 320, 2)
        display.text("Ammo: " + str(self.player.ammo), 228, 10, 320, 2)
        display.set_pen(0)

        display.update()
        time.sleep(0.02)

    def check_collision(self, a, b):
        return a.x + a.w >= b.x and a.x <= b.x + b.w and a.y + a.h >= b.y and a.y <= b.y + b.h

    def update(self):
        self.event_counter += 1
        self.aliens_shoot()

        for bullet in self.player_bullet_sprite_list:
            bullet.move()

        for bullet in self.alien_bullet_sprite_list:
            bullet.move()

        for ufo in self.ufo_sprites_list:
            ufo.move()

        self.handle_player_bullets()
        self.handle_alien_bullets()
        self.check_alien_positions()

        if self.event_counter % self.alien_move_interval == 0:
            for alien in self.alien_sprite_list:
                alien.move_down()
            if len(self.alien_sprite_list) == 0:
                self.level_up()
        if self.event_counter == 400 and len(self.ufo_sprites_list) < 1:
            ufo = Ufo()
            self.ufo_sprites_list.append(ufo)
            self.event_counter = 0

    def aliens_shoot(self):
        """
        Handle the aliens shooting at the player
        """
        for alien in self.alien_sprite_list:
            if self.player.is_alive:
                bullet = alien.shoot()
                if bullet:
                    self.alien_bullet_sprite_list.append(bullet)

    def handle_player_bullets(self):
        """
        Handle the player bullet collisions
        """
        for bullet in self.player_bullet_sprite_list:
            # check if hit alien
            alien_hit_list = []
            for alien in self.alien_sprite_list:
                if bullet.y >= alien.y and self.check_collision(bullet, alien):
                    alien.is_alive = False
                    alien_hit_list.append(alien)

            for alien in alien_hit_list:
                bullet.is_alive = False
                explosion = Explosion(alien.x, alien.y)
                self.explosions_sprite_list.append(explosion)
                self.player.score += 1

            # check if hit alien bullet
            alien_bullet_hit_list = []
            for alien_bullet in self.alien_bullet_sprite_list:
                if bullet.y >= alien_bullet.y and self.check_collision(bullet, alien_bullet):
                    alien_bullet.is_alive = False
                    alien_bullet_hit_list.append(alien_bullet)

            for alien_bullet in alien_bullet_hit_list:
                bullet.is_alive = False
                self.player.score += 1

            for ufo in self.ufo_sprites_list:
                if self.check_collision(bullet, ufo):
                    bullet.is_alive = False
                    ufo.is_alive = False
                    explosion = Explosion(ufo.x, ufo.y)
                    self.explosions_sprite_list.append(explosion)
                    self.player.score += 50

    def check_alien_positions(self):
        """
        Handle the aliens colliding with the player or touching the bottom of the screen
        """
        for alien in self.alien_sprite_list:
            if self.check_collision(self.player, alien):
                # alien hit player
                self.player.is_alive = False

            if alien.y + alien.h > HEIGHT:
                # alien went off screen, end game
                self.player.is_alive = False

    def handle_alien_bullets(self):
        """
        Handle the alien bullet collisions with player
        """
        for bullet in self.alien_bullet_sprite_list:
            if self.check_collision(self.player, bullet):
                # alien hit player
                self.player.is_alive = False


game = Game()

while True:
    game.background()
    display.set_pen(255)
    display.text("Space Invaders", 40, 35, 200, 6)
    display.text("Press Up to Start", 80, 150, 180, 2)
    display.update()

    while not button_up.read():
        pass

    while game.player.is_alive:
        game.get_input()
        game.update()
        game.draw()

    game.background()
    display.set_pen(255)
    display.text("GAME OVER", 15, 65, 305, 6)
    display.text("Your score:  " + str(game.player.score), 80, 150, 180, 2)
    display.update()

    while not button_up.read():
        pass

    game.reset()
