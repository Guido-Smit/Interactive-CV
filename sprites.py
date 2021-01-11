from settings import *
from tilemap import collide_hit_rect_to_rect
import pytweening as tween
import random


vec = pg.math.Vector2


class Spritesheet:
    # utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert_alpha()

    def get_image(self, x, y, width, height):
        # grab an image out of a larger spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width // 2, height // 2))
        return image


def collide_with_walls(sprite, group, dir):
    if dir == "x":
        x_hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect_to_rect)
        if x_hits:
            if x_hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = x_hits[0].rect.left - sprite.hit_rect.width / 2
            if x_hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = x_hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == "y":
        y_hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect_to_rect)
        if y_hits:
            if y_hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = y_hits[0].rect.top - sprite.hit_rect.height / 2
            if y_hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = y_hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.interact_rect = PLAYER_INTERACT_RECT
        self.interact_rect.center = self.rect.center

        self.health = PLAYER_HEALTH
        self.speed = PLAYER_SPEED

        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.last_hit = 0
        self.stun = 0

        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.interact_pos = 0
        self.rot = 0
        self.knockback = vec(0,0)

    def get_keys(self):
        self.rot_speed = 0
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel = vec(0, self.speed).rotate(-self.rot)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(0, -self.speed / 2).rotate(-self.rot)

    def update(self):

        if self.stun > 0:
            self.stun -= 1
            self.vel = vec(0, 0)
            self.knockback = self.knockback * 0.9
            self.image = pg.transform.rotate(self.game.player_stunned_img, self.rot)
            pg.display.flip()
        else:
            self.stun = 0
            self.knockback = vec(0, 0)
            self.animate()
            self.get_keys()
            self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
            self.interact_pos = vec(0, 35).rotate(-self.rot)
            if not self.walking:
                self.image = pg.transform.rotate(self.game.player_img, self.rot)


        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.interact_rect.center = self.pos + self.interact_pos
        self.pos += (self.vel + self.knockback) * self.game.dt

        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, "x")
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, "y")


    def add_health(self, amount):
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH

    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0 or self.vel.y != 0:
            self.walking = True
        else:
            self.walking = False

        if self.walking:
            if now - self.last_update > 100:
                self.last_update = now
                self.current_frame = ((self.current_frame + 1) % len(WALK_IMAGES))
            self.image = pg.transform.rotate(self.game.walk_images[self.current_frame], self.rot)


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class Interactable(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.interactables
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class NPC(pg.sprite.Sprite):
    def __init__(self, game, pos, type, subtype, direction, movement):
        self._layer = NPC_LAYER
        self.groups = game.all_sprites, game.npcs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.transform.scale(game.npc_images[type][0], (NPC_SIZE, NPC_SIZE))
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.type = type
        self.subtype = subtype
        self.direction = direction
        self.movement = movement
        self.pos = pos
        self.rect.center = pos
        self.interact_rect = pg.Rect(pos.x, pos.y, 30, 30)
        self.interact_rect.center = self.rect.center
        self.rot = 0
        self.last_update = 0
        self.current_frame = 0

        if self.direction == "N":
            self.rot = 180
        elif self.direction == "W":
            self.rot = -90
        elif self.direction == "E":
            self.rot = 90
        elif self.direction == "S":
            self.rot = 0

        self.image = pg.transform.rotate(self.image, self.rot)

    def rot_center(self, image, angle):
        orig_rect = self.rect
        rot_image = pg.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

    def update(self):
        now = pg.time.get_ticks()

        if now - self.last_update > 1000:
            self.last_update = now
            self.current_frame = ((self.current_frame + 1) % len(self.game.npc_images[self.type]))

        self.image = pg.transform.rotate(self.game.npc_images[self.type][self.current_frame], self.rot)

class Car(pg.sprite.Sprite):
    def __init__(self, game, pos, direction):
        self._layer = CAR_LAYER
        self.groups = game.all_sprites, game.cars
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.colour = random.choice(list(CAR_IMAGES.keys()))
        self.rot = 0
        self.current_frame = 0
        self.pos = pos
        self.direction = direction
        self.last_update = 0
        self.moving = True
        self.crosstime = 0
        self.crossing = False
        self.stop_pos = 0
        self.stop_rect = pg.Rect(pos.x, pos.y, 30, 30)

        if self.direction == "N":
            self.rot = 0
        elif self.direction == "W":
            self.rot = 90
        elif self.direction == "E":
            self.rot = -90
        elif self.direction == "S":
            self.rot = 180

        self.image = pg.transform.rotate(self.game.car_images[self.colour][self.current_frame], self.rot)
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.rect.center = pos




    def update(self):
        now = pg.time.get_ticks()

        if self.moving:
            if self.direction == "N":
                self.pos.y -= 10
            elif self.direction == "W":
                self.pos.x -= 10
            elif self.direction == "E":
                self.pos.x += 10
            elif self.direction == "S":
                self.pos.y += 10

        if now - self.last_update > 1000:
            self.last_update = now
            self.current_frame = ((self.current_frame + 1) % len(self.game.car_images[self.colour]))

        self.image = pg.transform.rotate(self.game.car_images[self.colour][self.current_frame], self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.hit_rect = self.rect
        self.stop_pos = vec(0, 50).rotate(-self.rot)
        self.stop_rect.center = self.pos - self.stop_pos

        if self.pos.x < -(self.game.map.width*0.5) or self.pos.x > self.game.map_rect.width * 1.5 or \
                self.pos.y < -self.game.map.height * 0.5 or self.pos.y > self.game.map.height * 1.5:
            self.kill()


class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type):
        self._layer = ITEM_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.transform.scale(game.item_images[type], (ITEM_SIZE, ITEM_SIZE))
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.type = type
        self.pos = pos
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update(self):
        # Itembounce motion
        offset = BOUNCE_RANGE * (self.tween(self.step / BOUNCE_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOUNCE_SPEED
        if self.step > BOUNCE_RANGE:
            self.step = 0
            self.dir *= -1

class Crossroad(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.crossroads
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.crossing_cars = {}