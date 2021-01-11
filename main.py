import sys
import os
from os import path
from sprites import *
from tilemap import *
from language import *
import random
import copy
import sys

if getattr(sys, 'frozen', False):  # PyInstaller adds this attribute
    # Running in a bundle
    game_folder = sys._MEIPASS
else:
    # Running in normal Python environment
    game_folder = os.path.dirname(__file__)

os.environ['SDL_VIDEO_CENTERED'] = '1'

# Create shortcut Vec
vec = pg.math.Vector2


# HUD functions

def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    bar_length = 100
    bar_height = 20
    fill = pct * bar_length
    outline_rect = pg.Rect(x, y, bar_length, bar_height)
    fill_rect = pg.Rect(x, y, fill, bar_height)
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED

    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)


class Game:
    def __init__(self):

        # Preload music mixer and pygame module
        pg.mixer.pre_init(44100, -16, 4, 2048)
        pg.init()
        self.clockcheck = pg.mixer.Channel(1)
        self.ambient_channel = pg.mixer.Channel(2)
        self.car_channel = pg.mixer.Channel(3)

        # Make the game start in fullscreen
        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.WIDTH, self.HEIGHT = pg.display.get_surface().get_size()
        self.scale_width_factor = (self.WIDTH/1920)
        self.scale_height_factor = (self.HEIGHT/1080)

        # Set a title for the appliction
        pg.display.set_caption(TITLE)

        # Make a clock for use further on
        self.clock = pg.time.Clock()

        # Define folders that contain the artwork and music for the game

        # Art folders
        png_folder = path.join(game_folder, "Artwork", "PNG")
        spritesheet_folder = path.join(game_folder, "Artwork", "Spritesheets")
        background_folder = path.join(game_folder, "Artwork", "PNG", "Backgrounds")
        effect_folder = path.join(game_folder, "Artwork", "PNG", "Effects")
        items_folder = path.join(png_folder, "Items")
        miscellaneous_folder = path.join(png_folder, "Misc")
        player_folder = path.join(png_folder, "Player")
        npc_folder = path.join(png_folder, "NPC")
        vehicles_folder = path.join(png_folder, "Vehicles")
        car_folder = path.join(vehicles_folder, "Cars")
        cv_folder = path.join(png_folder, "CV")

        # Music folders
        sound_folder = path.join(game_folder, "Sounds")
        self.music_folder = path.join(game_folder, "Music")
        self.song = "town"

        # Map related data
        self.map_folder = path.join(game_folder, "maps")

        # Fonts
        font_folder = path.join(game_folder, "Artwork", "Fonts")

        self.title_font = path.join(font_folder, GAMEFONT)
        self.hud_font = path.join(font_folder, HUDFONT)
        self.txt_font = path.join(font_folder, TXT_FONT)

        # A dim surface to highlight opened menu's
        self.dim = pg.Surface.convert_alpha(pg.Surface(self.screen.get_size()))
        self.dim.fill((0, 0, 0, 180))

        # Load Fixed images

        # People fixed images
        self.player_img = pg.image.load(path.join(player_folder, PLAYER_IMAGE)).convert_alpha()
        self.player_stunned_img = pg.image.load(path.join(player_folder, PLAYER_STUNNED_IMAGE)).convert_alpha()

        self.walk_images = {}
        for image in WALK_IMAGES:
            self.walk_images[image] = pg.image.load(path.join(player_folder, WALK_IMAGES[image])).convert_alpha()

        self.cry_images = {}
        for image in CRY_IMAGES:
            self.cry_images[image] = pg.image.load(path.join(player_folder, CRY_IMAGES[image])).convert_alpha()

        self.cheer_images = {}
        for image in CHEER_IMAGES:
            self.cheer_images[image] = pg.image.load(path.join(player_folder, CHEER_IMAGES[image])).convert_alpha()

        self.npc_images = {}
        for npc in NPC_IMAGES:
            self.npc_images[npc] = []
            for sprite in NPC_IMAGES[npc]:
                self.npc_images[npc].append(pg.image.load(path.join(npc_folder, sprite)).convert_alpha())

        self.car_images = {}
        for car in CAR_IMAGES:
            self.car_images[car] = []
            for sprite in CAR_IMAGES[car]:
                self.car_images[car].append(pg.image.load(path.join(car_folder, sprite)).convert_alpha())

        # Object fixed images

        self.txtbox_img = pg.transform.scale(pg.image.load(path.join(cv_folder, TEXTBOX_IMAGE)).convert_alpha(),
                                             (int(self.WIDTH * 0.6), int(self.HEIGHT * 0.1)))
        self.opening_img = pg.transform.scale(
            pg.image.load(path.join(background_folder, BACKGROUNDIMAGE)).convert_alpha(), (self.WIDTH, self.HEIGHT))

        self.end_img = pg.transform.scale(
            pg.image.load(path.join(background_folder, END_IMAGE)).convert_alpha(), (self.WIDTH, self.HEIGHT))

        # CV Images
        self.undiscovered_image = pg.transform.scale(pg.image.load(
            path.join(cv_folder, UNDISCOVERED_IMAGE)).convert_alpha(), (int((950 * self.scale_width_factor)), int((700 * self.scale_height_factor))))

        self.collected_cv_parts_image = pg.transform.scale(
            pg.image.load(path.join(items_folder, CVPARTS_IMAGE)).convert_alpha(), (int((100 * self.scale_width_factor)),
                                                                                    int((50 * self.scale_height_factor))))

        self.CV_images = {}
        for CVdict in CVPARTS:
            self.CV_images[CVdict] = {}
            for CVpart in CVPARTS[CVdict]:
                self.CV_images[CVdict][CVpart] = pg.image.load(
                    path.join(cv_folder, CVPARTS[CVdict][CVpart])).convert_alpha()

        # UI images
        self.timer_image = pg.transform.scale(pg.image.load(path.join(items_folder, TIMERIMAGE)).convert_alpha(),
                                              (int((75 * self.scale_width_factor)),
                                               int((75 * self.scale_height_factor))))

        self.empty_shoe_image = pg.transform.scale(
            pg.image.load(path.join(items_folder, EMPTY_SHOE_IMAGE)).convert_alpha(),
            (int((75 * self.scale_width_factor)),
             int((75 * self.scale_height_factor))))

        self.flags = {}
        for flag in FLAGS:
            self.flags[flag] = pg.transform.scale(pg.image.load(path.join(miscellaneous_folder, FLAGS[flag])),
                                                  (int((30 * self.scale_width_factor)), int((30 * self.scale_height_factor))))

        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(items_folder, ITEM_IMAGES[item])).convert_alpha()

        self.star_images = {}
        for star in STAR_IMAGES:
            self.star_images[star] = pg.image.load(path.join(miscellaneous_folder, STAR_IMAGES[star])).convert_alpha()

        self.perfect_images = {}
        for stamp in PERFECT_STAMPS:
            self.perfect_images[stamp] = pg.transform.scale(
                pg.image.load(path.join(miscellaneous_folder, PERFECT_STAMPS[stamp])).convert_alpha(), ((int((125 * self.scale_width_factor)),
                                                                                                        int((125 * self.scale_height_factor)))))
        # Screen images
        self.introscreen = {}
        for screen in INTRO_IMAGE:
            self.introscreen[screen] = pg.transform.scale(pg.image.load(path.join(cv_folder, INTRO_IMAGE[screen])),
                                                          (int((950 * self.scale_width_factor)), int((700 * self.scale_height_factor))))

        self.controls_img = {}
        for screen in CONTROLSIMAGE:
            self.controls_img[screen] = pg.transform.scale(pg.image.load(path.join(cv_folder, CONTROLSIMAGE[screen])),
                                                          (int((950 * self.scale_width_factor)), int((700 * self.scale_height_factor))))

        self.goals = {}
        for screen in GOAL_IMAGE:
            self.goals[screen] = pg.transform.scale(pg.image.load(path.join(cv_folder, GOAL_IMAGE[screen])),
                                                    (self.WIDTH, self.HEIGHT))

        self.info = {}
        for screen in INFO_IMAGE:
            self.info[screen] = pg.transform.scale(pg.image.load(path.join(cv_folder, INFO_IMAGE[screen])),
                                                   (self.WIDTH, self.HEIGHT))

        self.quit_img = {}
        for screen in QUIT_IMAGES:
            self.quit_img[screen] = pg.transform.scale(pg.image.load(path.join(cv_folder, QUIT_IMAGES[screen])),
                                                          (int((950 * self.scale_width_factor)), int((700 * self.scale_height_factor))))

        # sound loading
        self.effects_sounds = {}
        for sound in EFFECT_SOUNDS:
            self.effects_sounds[sound] = pg.mixer.Sound(path.join(sound_folder, EFFECT_SOUNDS[sound]))
            self.effects_sounds[sound].set_volume(0.5)

        self.load_song(self.song)

        # Misc. init
        self.controls = False
        self.quitting = False
        self.language = "NL"

        # Pre init values in the init function (So that the editor does not complain)
        self.player = None
        self.CVPARTS = None
        self.CVcount = None
        self.timer = None
        self.timer_colour = None
        self.paused = None
        self.hand_in = None
        self.cv_found = None
        self.menu_open = None
        self.intro = None
        self.camera = None
        self.draw_debug = None
        self.CV_part = None
        self.wait = None
        self.show_moment = None
        self.menu_selector = None
        self.animation_frame = None
        self.last_cry_update = None
        self.last_cheer_update = None
        self.should_update = None
        self.playing = None
        self.dt = None
        self.choice = None

        self.all_sprites = None
        self.walls = None
        self.crossroads = None
        self.interactables = None
        self.npcs = None
        self.cars = None
        self.items = None
        self.last_npc_animation = None
        self.last_car_animation = None
        self.last_ambient = None
        self.has_died = False
        self.item_count = []

        # Map initialisation
        self.map = None
        self.map_img = None
        self.map_rect = None

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, int((size * ((self.scale_height_factor + self.scale_width_factor)/2))))
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()

        # Alignment shortcuts
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_song(self, song):
        self.song = song
        pg.mixer.music.stop()
        pg.mixer.music.load(path.join(self.music_folder, MUSIC[song]))
        pg.mixer.music.play(loops=-1)
        pg.mixer.music.set_volume(0.2)

    def new(self):
        # initialize all variables and do all the setup for a new game

        # Reset the music
        if self.song != "town":
            self.load_song("town")

        # Spritegroups
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.crossroads = pg.sprite.Group()
        self.interactables = pg.sprite.Group()
        self.npcs = pg.sprite.Group()
        self.cars = pg.sprite.Group()
        self.items = pg.sprite.Group()

        # Map initialisation
        self.map = TiledMap(path.join(self.map_folder, "CV.tmx"))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

        # Load maps made in Tiled editor
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
            if tile_object.name == "Player":
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == "wall":
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == "Crossroad":
                Crossroad(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == "Interactable":
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
                Interactable(self, tile_object.x + 5, tile_object.y + 5, tile_object.width - 10,
                             tile_object.height - 10)
            if tile_object.name in ["NPC"]:
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
                NPC(self, obj_center, tile_object.type, tile_object.subtype, tile_object.direction,
                    tile_object.movement)
            if tile_object.name in ["Health", "Time", "Running shoes"]:
                Item(self, obj_center, tile_object.name)

        # Initialisation of the game variables
        self.CVPARTS = copy.deepcopy(CVPARTS)
        self.CVcount = len(self.CVPARTS[self.language])
        self.timer = TIMER
        self.timer_colour = GREEN

        # Reset previous game data
        PARTSCOLLECTED.clear()
        TIMEBOOSTSCOLLECTED.clear()
        SPEEDBOOSTSCOLLECTED.clear()

        # Menu Variables
        self.paused = False
        self.hand_in = False
        self.cv_found = False
        self.menu_open = False
        self.intro = True

        # Other game variables
        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.CV_part = None
        self.wait = 100
        self.show_moment = 0
        self.menu_selector = pg.Rect(int((self.WIDTH * 0.05)), int((self.HEIGHT * 0.2)), int((self.WIDTH * 0.15)),
                                     int((self.HEIGHT * 0.3)))
        self.animation_frame = 0
        self.last_cry_update = 0
        self.last_cheer_update = 0
        self.last_npc_animation = 0
        self.last_car_animation = 0
        self.last_ambient = 0
        self.has_died = False
        self.clocksound = False

        # Controls whether the game updates (Thus advancing time/calculations etc). Should be false when idle like in
        # menu's.
        self.should_update = False

        self.item_count = []
        for item in self.items:
            self.item_count.append(item.type)

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True

        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            if self.should_update:
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.WIDTH, self.HEIGHT, self.player)

        # In game deadline/timer
        if self.timer > 0 and self.should_update:
            self.timer -= (1 / FPS)
            self.set_timer_colour()
            if self.timer < 0:
                self.timer = 0
        if self.timer == 0:
            self.clockcheck.stop()
            self.playing = False

        # Play ambient sound
        now_ambient = pg.time.get_ticks()
        if now_ambient - self.last_ambient > 10000:
            self.last_ambient = now_ambient
            if random.randint(0, 100) < 25:
                self.ambient_channel.play(self.effects_sounds['Bird1'])

        # Move NPC's
        now = pg.time.get_ticks()
        if now - self.last_npc_animation > 1000:
            self.last_npc_animation = now
            for sprite in self.npcs:
                if sprite.movement == "looking":
                    if random.randint(0, 100) < 15:
                        sprite.rot += int(random.choice((-90, 90)))

        # Spawn cars
        if now - self.last_car_animation > 1000:
            self.last_car_animation = now
            for tile_object in self.map.tmxdata.objects:
                obj_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
                if tile_object.name in ["Car"] and random.randint(0, 100) < 15:
                    Car(self, obj_center, tile_object.direction)

        # player hits items
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == "Health" and self.player.health < PLAYER_HEALTH:
                HEALTHCOLLECTED.append(hit)
                hit.kill()
                self.effects_sounds['Health'].play()
                self.player.add_health(HEALTH_PACK_AMOUNT)
            if hit.type == "Time":
                TIMEBOOSTSCOLLECTED.append(hit)
                hit.kill()
                self.effects_sounds['Time'].play()
                self.timer += 30
            if hit.type == "Running shoes":
                SPEEDBOOSTSCOLLECTED.append(hit)
                hit.kill()
                self.effects_sounds['Speedboost'].play()
                self.player.speed += 100

        # player hits car
        hits = pg.sprite.spritecollide(self.player, self.cars, False, collide_hit_rect_to_rect)
        if hits:
            current_hit = pg.time.get_ticks()
            if current_hit > self.player.last_hit + 400:
                self.car_channel.play(self.effects_sounds['Car'])
                self.player.last_hit = current_hit
                self.player.health -= CAR_DAMAGE
                self.player.stun = 25

                if self.player.rect.top < hits[0].rect.top:
                    self.player.knockback -= vec(0, CAR_KNOCKBACK)
                if self.player.rect.top > hits[0].rect.top:
                    self.player.knockback += vec(0, CAR_KNOCKBACK)
                if self.player.rect.left < hits[0].rect.left:
                    self.player.knockback -= vec(CAR_KNOCKBACK, 0)
                if self.player.rect.left > hits[0].rect.left:
                    self.player.knockback += vec(CAR_KNOCKBACK, 0)

        # Cars cross at crossroads
        crossroads_in_use = pg.sprite.groupcollide(self.crossroads, self.cars, False, False)
        if crossroads_in_use:
            for crossroad in crossroads_in_use:
                crossroad.crossing_cars = {}

                for car in crossroads_in_use[crossroad]:
                    car.crosstime += 1
                    crossroad.crossing_cars.update({car: car.crosstime})

                if len(crossroads_in_use[crossroad]) > 1:
                    firstcar = max(crossroad.crossing_cars, key=crossroad.crossing_cars.get)
                    for car in crossroad.crossing_cars:
                        if car != firstcar:
                            car.moving = False
                        else:
                            car.moving = True
                else:
                    crossroads_in_use[crossroad][0].moving = True

        on_crossroad = pg.sprite.groupcollide(self.cars, self.crossroads, False, False)
        stopping_cars = pg.sprite.groupcollide(self.cars, self.cars, False, False, collide_stop_rect_to_rect)
        for car in self.cars:
            if car not in on_crossroad:
                car.moving = True
                car.crosstime = 0
            if car not in on_crossroad and car in stopping_cars:
                car.moving = False

        if self.player.health <= 0:
            self.playing = False
            self.has_died = True

    def draw(self):
        # Draw the map
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))

        # Draw the sprites
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            # Draw the rects of sprites in debug mode
            if self.draw_debug:
                pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(sprite.hit_rect), 1)
        # Draw rects in debug mode
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(wall.rect), 1)
            for crossroad in self.crossroads:
                pg.draw.rect(self.screen, RED, self.camera.apply_rect(crossroad.rect), 1)
            for car in self.cars:
                pg.draw.rect(self.screen, BLACK, self.camera.apply_rect(car.stop_rect), 1)
            for interactable in self.interactables:
                pg.draw.rect(self.screen, BLUE, self.camera.apply_rect(interactable.rect), 1)
            # Display FPS
            self.draw_text('FPS: {}'.format(int(self.clock.get_fps())), self.hud_font, 30, WHITE, self.WIDTH * 0.85, 70,
                           align="nw")

            self.draw_text('pos: {}'.format(int(self.player.pos.x)), self.hud_font, 30, WHITE, self.WIDTH * 0.85, 100,
                           align="nw")
            self.draw_text('widthfac: {}'.format(float(self.scale_width_factor)), self.hud_font, 30, WHITE, self.WIDTH * 0.85, 130,
                           align="nw")
            self.draw_text('heightfac: {}'.format(float(self.scale_height_factor)), self.hud_font, 30, WHITE,
                           self.WIDTH * 0.85, 160,
                           align="nw")
            self.draw_text('width: {}'.format(int(self.WIDTH)), self.hud_font, 30, WHITE,
                           self.WIDTH * 0.85, 190,
                           align="nw")
            self.draw_text('height: {}'.format(int(self.HEIGHT)), self.hud_font, 30, WHITE,
                           self.WIDTH * 0.85, 220,
                           align="nw")
            # Check rect of interact box
            pg.draw.rect(self.screen, RED, self.camera.apply_rect(self.player.interact_rect), 1)

        # HUD Drawing
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)

        self.screen.blit(self.flags[self.language], [int(self.WIDTH * 0.98), int(self.HEIGHT * 0.01)])

        timer_rect = self.timer_image.get_rect(topleft=(20, 50))
        self.screen.blit(self.timer_image, timer_rect)

        document_rect = self.collected_cv_parts_image.get_rect(topleft=(10, 150))
        self.screen.blit(self.collected_cv_parts_image, document_rect)

        self.draw_text('{}'.format(str(len(PARTSCOLLECTED)) + "/10"), self.txt_font, 25,
                       BLACK, document_rect.centerx, document_rect.centery,
                       align="center")

        self.draw_text('{}'.format(int(self.timer)), self.txt_font, 30, self.timer_colour, timer_rect.centerx,
                       timer_rect.centery + 2, align="center")

        # HUD Menu's
        if self.paused:
            self.screen.blit(self.dim, (0, 0))
            self.draw_text(LANGUAGE[self.language]["PAUSE"], self.title_font, 105, RED, self.WIDTH / 2, self.HEIGHT / 2,
                           align="center")
        if self.cv_found:
            self.should_update = False
            self.screen.blit(self.CV_part, [self.WIDTH * 0.25, self.HEIGHT * 0.1])
            self.wait -= 10
            if self.wait < 0:
                self.wait = 0
        if self.intro:
            self.should_update = False
            self.screen.blit(self.introscreen[self.language], [self.WIDTH * 0.25, self.HEIGHT * 0.1])
            self.wait -= 5
            if self.wait < 0:
                self.wait = 0
        if self.menu_open:
            self.should_update = False
            self.screen.blit(self.dim, (0, 0))
            self.draw_text(LANGUAGE[self.language]["COLLECTED"], self.title_font, 40, WHITE, self.WIDTH / 2,
                           self.HEIGHT * 0.1,
                           align="center")

            # Draw the menu and the CV pieces
            pos = vec(int(self.WIDTH * 0.05), int(self.HEIGHT * 0.2))
            for number in range(1, (self.CVcount + 1)):
                # Make rects to check which piece is selected with the menu-selector
                MenuPieces.append(pg.Rect(pos.x, pos.y, int(self.WIDTH * 0.15), int(self.HEIGHT * 0.3)))
                # Check which pieces have been found
                if str(number) in PARTSCOLLECTED:
                    self.screen.blit(
                        pg.transform.scale(self.CV_images[self.language][str('CV' + str(number))],
                                           (int(self.WIDTH * 0.15), int(self.HEIGHT * 0.3))),
                        [pos.x, pos.y])
                # Draw an undefined image if no piece has been found yet
                else:
                    self.screen.blit(
                        pg.transform.scale(self.undiscovered_image,
                                           (int(self.WIDTH * 0.15), int(self.HEIGHT * 0.3))),
                        [pos.x, pos.y])
                # Advance the position of each pieces
                pos.x += int((350 * self.scale_width_factor))
                if pos.x > (self.WIDTH - int(self.WIDTH * 0.15)):
                    pos.y += int((50 * self.scale_height_factor)) + int(self.HEIGHT * 0.3)
                    pos.x = int(self.WIDTH * 0.05)

            # Ensure the menu is open for a min. time before it can be closed again
            self.wait -= 10
            if self.wait < 0:
                self.wait = 0

            # Draw the selector
            pg.draw.rect(self.screen, RED, self.menu_selector, 5)

        # Show the controls while playing the game
        if self.controls:
            self.should_update = False
            self.screen.blit(self.controls_img[self.language], [self.WIDTH * 0.25, self.HEIGHT * 0.1])
            self.wait -= 5
            if self.wait < 0:
                self.wait = 0

        if self.quitting:
            self.should_update = False
            self.screen.blit(self.quit_img[self.language], [self.WIDTH * 0.25, self.HEIGHT * 0.1])
            self.wait -= 5
            if self.wait < 0:
                self.wait = 0

        # Command to display all the drawn parts, almost always comes last
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_p:
                    self.paused = not self.paused
                    self.should_update = not self.should_update

                # nonfunctional fullscreen and windowed
                # if event.key == pg.K_f:
                #     if self.screen.get_flags() & pg.FULLSCREEN:
                #         pg.display.set_mode((WINDOWED_WIDTH, WINDOWED_HEIGHT))
                #
                #     else:
                #         pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN)

            if event.type == pg.KEYUP:
                # Determine which action to take place when the "Enter" key is pressed on an interactable
                if event.key == pg.K_RETURN and self.should_update:
                    # Find a CV parts
                    if len(self.CVPARTS[self.language]) > 0:
                        found_part = pg.sprite.spritecollide(self.player, self.interactables, True,
                                                             collide_interact_rect_to_rect)
                        if found_part:
                            self.cv_found = not self.cv_found
                            self.choice = random.choice(list(self.CVPARTS[self.language]))
                            PARTSCOLLECTED.append(self.choice.lstrip('CV'))
                            self.CV_part = self.CV_images[self.language][self.choice]
                            self.effects_sounds['searching'].play()
                            self.wait = 100

                    # Speak with a NPC
                    npc_interacts = pg.sprite.spritecollide(self.player, self.npcs, False,
                                                            collide_interact_rect_to_interact_rect)

                    for npc in npc_interacts:
                        self.all_sprites.remove(npc)
                        self.all_sprites.update()
                        self.draw()

                        newimage = npc.rot_center(npc.image, (self.player.rot - 180 - npc.rot))

                        self.screen.blit(newimage,
                                         self.camera.apply(npc))
                        if npc.type == "boss":
                            self.show_boss_screen()
                        else:
                            self.show_npc_text(npc.subtype)

                        self.all_sprites.add(npc)

                # Close a found CV screen
                if event.key == pg.K_RETURN and self.cv_found and self.wait == 0:
                    self.cv_found = not self.cv_found
                    self.should_update = True
                    for language in self.CVPARTS:
                        del self.CVPARTS[language][self.choice]

                # Open and close the menu with collected CV parts
                if event.key == pg.K_m and not self.menu_open and self.should_update:
                    self.menu_open = True
                    self.wait = 100
                elif event.key == pg.K_m and self.wait == 0:
                    self.menu_open = False
                    self.should_update = True

                # Movement of the menu selector
                if event.key == pg.K_RIGHT and self.menu_open and self.menu_selector.x < (self.WIDTH * 0.75):
                    self.menu_selector.move_ip(int((350 * self.scale_width_factor)), 0)
                    self.effects_sounds['Menu'].play()
                if event.key == pg.K_LEFT and self.menu_open and self.menu_selector.x > int(self.WIDTH * 0.05):
                    self.menu_selector.move_ip(int((-350 * self.scale_width_factor)), 0)
                    self.effects_sounds['Menu'].play()
                if event.key == pg.K_DOWN and self.menu_open and self.menu_selector.y < int(self.HEIGHT * 0.5):
                    self.menu_selector.move_ip(0, int((50 * self.scale_height_factor)) + int((self.HEIGHT * 0.3)))
                    self.effects_sounds['Menu'].play()
                if event.key == pg.K_UP and self.menu_open and self.menu_selector.y > int(self.HEIGHT * 0.3):
                    self.menu_selector.move_ip(0, int((-50 * self.scale_height_factor)) - int((self.HEIGHT * 0.3)))
                    self.effects_sounds['Menu'].play()

                # Bekijk een gevonden CV onderdeel in t menu
                if event.key == pg.K_RETURN and self.menu_open:
                    for i in MenuPieces:
                        if self.menu_selector.colliderect(i):
                            cv_number = (MenuPieces.index(i) + 1)
                            if str(cv_number) in PARTSCOLLECTED:
                                self.screen.blit(self.dim, (0, 0))
                                self.screen.blit(
                                    self.CV_images[self.language][str('CV' + str(cv_number))],
                                    (self.WIDTH * 0.25, self.HEIGHT * 0.1))
                                pg.display.flip()
                                self.effects_sounds['searching'].play()
                                self.wait_for_key()
                                break
                        else:
                            pass

                # Change the language midgame
                if event.key == pg.K_l and self.language == "NL" and not self.menu_open and self.should_update:
                    self.language = "EN"
                    self.show_moment = pg.time.get_ticks()
                if event.key == pg.K_l and (
                        pg.time.get_ticks() - self.show_moment > 250) and self.language == "EN" and not \
                        self.menu_open and self.should_update:
                    self.language = "NL"
                    self.show_moment = pg.time.get_ticks()

                # Close the introduction text
                if event.key == pg.K_RETURN and self.intro and self.wait == 0:
                    self.intro = False
                    self.should_update = True

                # Show the controls
                if event.key == pg.K_c and not self.controls and self.should_update:
                    self.wait = 100
                    self.controls = True
                    self.effects_sounds['searching'].play()
                elif event.key == pg.K_c and self.wait == 0:
                    self.controls = False
                    self.should_update = True

                # Show the quit screen
                if event.key == pg.K_ESCAPE and not self.quitting and self.should_update:
                    self.wait = 100
                    self.quitting = True
                    self.effects_sounds['searching'].play()
                elif event.key == pg.K_ESCAPE and self.wait == 0 and self.quitting:
                    self.quitting = False
                    self.should_update = True
                if event.key == pg.K_RETURN and self.quitting and self.wait == 0:
                    self.quit()

    def set_timer_colour(self):
        if self.timer > (0.5 * TIMER):
            self.timer_colour = GREEN
            self.clockcheck.stop()
        if (0.5 * TIMER) >= self.timer > (0.25 * TIMER):
            self.timer_colour = ORANGE
            self.clockcheck.stop()
        if self.timer <= (0.25 * TIMER):
            if not self.clockcheck.get_busy():
                self.clockcheck.play(self.effects_sounds['Clock'])
            self.timer_colour = RED

    def show_start_screen(self):
        self.screen.blit(self.opening_img, [0, 0])
        self.draw_text(LANGUAGE[self.language]["TITLE"], self.title_font, 80, BLACK, self.WIDTH / 2,
                       self.HEIGHT * 1 / 4,
                       align="center")

        self.draw_text(LANGUAGE[self.language]["CONTROLKEY"], self.title_font, 25, BLACK, self.WIDTH / 2,
                       self.HEIGHT * 0.45,
                       align="center")
        self.draw_text(LANGUAGE[self.language]["LANGUAGEKEY"], self.title_font, 25, BLACK, self.WIDTH / 2,
                       self.HEIGHT * 0.50,
                       align="center")

        self.draw_text(LANGUAGE[self.language]["STARTKEY"], self.title_font, 50, BLACK, self.WIDTH / 2,
                       self.HEIGHT * 0.7,
                       align="center")

        self.screen.blit(self.flags[self.language], [0, 0])

        self.show_moment = pg.time.get_ticks()
        pg.display.flip()

    def show_goal_screen(self):
        self.screen.blit(self.goals[self.language], [0, 0])
        self.show_moment = pg.time.get_ticks()
        pg.display.flip()
        self.wait_for_key()

    def show_info_screen(self):
        self.screen.blit(self.info[self.language], [0, 0])
        self.show_moment = pg.time.get_ticks()
        pg.display.flip()
        self.wait_for_key()

    def show_control_screen(self):
        self.screen.blit(self.controls_img[self.language], [self.WIDTH * 0.25, self.HEIGHT * 0.1])
        self.show_moment = pg.time.get_ticks()
        self.controls = True
        pg.display.flip()

    def show_quit_screen(self):
        self.screen.blit(self.quit_img[self.language], [self.WIDTH * 0.25, self.HEIGHT * 0.1])
        self.show_moment = pg.time.get_ticks()
        self.quitting = True
        pg.display.flip()

        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP and (pg.time.get_ticks() - self.show_moment > 250):
                    if event.key == pg.K_RETURN:
                        self.quit()
                    if event.key == pg.K_ESCAPE:
                        waiting = False

    def show_go_screen(self):
        self.show_moment = pg.time.get_ticks()

        self.load_song("gameover")

        waiting = True
        while waiting:
            self.screen.fill(BLACK)
            now = pg.time.get_ticks()
            if now - self.last_cry_update > 400:
                self.last_cry_update = now
                self.animation_frame = ((self.animation_frame + 1) % len(CRY_IMAGES))
            self.screen.blit(self.cry_images[self.animation_frame],
                             (self.WIDTH / 2 - self.cry_images[self.animation_frame].get_width() / 2,
                              self.HEIGHT * 0.65))

            self.draw_text("GAME OVER", self.title_font, 100, RED, self.WIDTH / 2, self.HEIGHT * 0.25, align="center")
            if self.has_died:
                self.draw_text(LANGUAGE[self.language]["DEAD1"], self.title_font, 50, RED, self.WIDTH / 2,
                               self.HEIGHT * 0.45,
                               align="center")
                self.draw_text(LANGUAGE[self.language]["DEAD2"], self.title_font, 50, RED, self.WIDTH / 2,
                               self.HEIGHT * 0.55,
                               align="center")
            else:
                self.draw_text(LANGUAGE[self.language]["GAMEOVER"], self.title_font, 50, RED, self.WIDTH / 2,
                               self.HEIGHT * 0.45,
                               align="center")
            self.draw_text(LANGUAGE[self.language]["RESTARTKEY"], self.title_font, 50, WHITE, self.WIDTH / 2,
                           self.HEIGHT * 0.85,
                           align="center")
            self.draw_text(LANGUAGE[self.language]["ESCKEY"], self.title_font, 25, WHITE, self.WIDTH / 2,
                           self.HEIGHT * 0.90,
                           align="center")
            pg.display.flip()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP and (pg.time.get_ticks() - self.show_moment > 750):
                    if event.key == pg.K_RETURN:
                        waiting = False
                    if event.key == pg.K_ESCAPE:
                        self.quit()

    def show_npc_text(self, type):
        self.clockcheck.pause()
        for txt in NPCLANGUAGE[self.language][type]:
            self.effects_sounds['Menu'].play()
            self.screen.blit(self.txtbox_img, (self.WIDTH / 2 - self.txtbox_img.get_width() / 2, self.HEIGHT * 0.55))
            self.draw_text(txt, self.txt_font, 30, BLACK, self.WIDTH / 2, self.HEIGHT * 0.6,
                           align="center")
            self.show_moment = pg.time.get_ticks()
            pg.display.flip()
            self.wait_for_key()
        self.clockcheck.unpause()

    def show_boss_screen(self):
        self.show_npc_text("BOSS")
        self.playing = False
        self.hand_in = True

    def show_hand_in_screen(self):

        self.show_moment = pg.time.get_ticks()
        self.load_song("victory")

        waiting = True
        while waiting:
            self.screen.blit(self.end_img, [0, 0])
            now = pg.time.get_ticks()

            # Page 1
            cvcounter = pg.transform.scale(self.collected_cv_parts_image, (int((110 * self.scale_width_factor)), int((110 * self.scale_height_factor))))

            document_rect = cvcounter.get_rect(center=(self.WIDTH * 0.4, self.HEIGHT * 0.25))
            timer_rect = self.timer_image.get_rect(center=(self.WIDTH * 0.4, self.HEIGHT * 0.35))
            speed_rect = self.empty_shoe_image.get_rect(center=(self.WIDTH * 0.4, self.HEIGHT * 0.45))
            stamp_rect_left = self.perfect_images["Left"].get_rect(center=(self.WIDTH * 0.10, self.HEIGHT * 0.65))
            stamp_rect_right = self.perfect_images["Right"].get_rect(center=(self.WIDTH * 0.40, self.HEIGHT * 0.65))

            self.screen.blit(cvcounter, document_rect)
            self.screen.blit(self.timer_image, timer_rect)
            self.screen.blit(self.empty_shoe_image, speed_rect)

            if now - self.last_cheer_update > 400:
                self.last_cheer_update = now
                self.animation_frame = ((self.animation_frame + 1) % len(CHEER_IMAGES))

            self.screen.blit(self.cheer_images[self.animation_frame],
                             (self.WIDTH * 0.25 - self.cheer_images[self.animation_frame].get_width() / 2,
                              self.HEIGHT * 0.8))
            self.draw_text(LANGUAGE[self.language]["YOUHAVE"], self.txt_font, 70, BLACK, self.WIDTH * 0.25,
                           self.HEIGHT * 0.15,
                           align="center")
            self.draw_text(LANGUAGE[self.language]["CVPARTS"], self.txt_font, 50, BLACK, self.WIDTH * 0.075,
                           self.HEIGHT * 0.25,
                           align="w")

            self.draw_text(LANGUAGE[self.language]["TIMEBOOSTS"], self.txt_font, 50, BLACK, self.WIDTH * 0.075,
                           self.HEIGHT * 0.35,
                           align="w")

            self.draw_text(LANGUAGE[self.language]["SPEEDBOOSTS"], self.txt_font, 50, BLACK, self.WIDTH * 0.075,
                           self.HEIGHT * 0.45,
                           align="w")

            self.draw_text(LANGUAGE[self.language]["SCORE"], self.txt_font, 70, BLACK, self.WIDTH * 0.25,
                           self.HEIGHT * 0.55,
                           align="center")

            self.draw_text('{}'.format(str(len(PARTSCOLLECTED)) + "/" + str(len(self.CV_images["NL"]))), self.txt_font,
                           25,
                           BLACK, document_rect.centerx, document_rect.centery,
                           align="center")

            self.draw_text('{}'.format(str(len(TIMEBOOSTSCOLLECTED)) + "/" + str(self.item_count.count("Time"))),
                           self.txt_font, 25,
                           WHITE, timer_rect.centerx, timer_rect.centery,
                           align="center")

            self.draw_text(
                '{}'.format(str(len(SPEEDBOOSTSCOLLECTED)) + "/" + str(self.item_count.count("Running shoes"))),
                self.txt_font, 25, BLACK, speed_rect.centerx, speed_rect.centery,
                align="center")

            score = round(100 * (int(len(PARTSCOLLECTED)) / (int((len(self.CV_images["NL"]))))))

            completion_score = round(100 * (
                    (int(len(SPEEDBOOSTSCOLLECTED)) + int(len(TIMEBOOSTSCOLLECTED) + int(len(PARTSCOLLECTED)))) / (
                    int((len(self.CV_images["NL"])) + int(self.item_count.count("Time"))) + int(
                self.item_count.count("Running shoes")))))

            score_star = 0
            if score <= 17:
                score_star = 0
            if 17 < score <= 33:
                score_star = 1
            if 33 < score <= 50:
                score_star = 2
            if 50 < score <= 67:
                score_star = 3
            if 67 < score <= 83:
                score_star = 4
            if 83 < score <= 100:
                score_star = 5
            if completion_score == 100:
                score_star = 6
                self.screen.blit(self.perfect_images["Left"], stamp_rect_left)
                self.screen.blit(self.perfect_images["Right"], stamp_rect_right)

            star = self.star_images[str(score_star)]
            star_rect = star.get_rect(center=(self.WIDTH * 0.25, self.HEIGHT * 0.65))

            self.screen.blit(self.star_images[str(score_star)], star_rect)

            self.draw_text(LANGUAGE[self.language]["RESTARTKEY"], self.txt_font, 50, BLACK, self.WIDTH * 0.25,
                           self.HEIGHT * 3 / 4,
                           align="center")

            self.draw_text(LANGUAGE[self.language]["ESCKEY"], self.txt_font, 25, BLACK, self.WIDTH * 0.25,
                           self.HEIGHT * 0.88,
                           align="center")

            # Page 2
            self.draw_text(LANGUAGE[self.language]["CONTACT"], self.txt_font, 70, BLACK, self.WIDTH * 0.75,
                           self.HEIGHT * 0.15,
                           align="center")

            self.draw_text("Guido's info:", self.txt_font, 50, BLACK, self.WIDTH * 0.75, self.HEIGHT * 0.25,
                           align="center")

            self.draw_text("Email = guido.smit@casema.nl", self.txt_font, 25, BLACK, self.WIDTH * 0.75,
                           self.HEIGHT * 0.35,
                           align="center")

            self.draw_text("Young Capital info:", self.txt_font, 50, BLACK, self.WIDTH * 0.75, self.HEIGHT * 0.45,
                           align="center")

            self.draw_text("Talentmanager = Valerie Beukeboom", self.txt_font, 25, BLACK, self.WIDTH * 0.75,
                           self.HEIGHT * 0.55,
                           align="center")

            self.draw_text("Email Talentmanager = v.beukeboom@youngcapital.nl", self.txt_font, 25, BLACK,
                           self.WIDTH * 0.75,
                           self.HEIGHT * 0.65,
                           align="center")

            self.draw_text(LANGUAGE[self.language]["THANKS"], self.txt_font, 50, BLACK, self.WIDTH * 0.75,
                           self.HEIGHT * 0.75,
                           align="center")

            pg.display.flip()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP and (pg.time.get_ticks() - self.show_moment > 750):
                    if event.key == pg.K_RETURN:
                        waiting = False
                    if event.key == pg.K_ESCAPE:
                        self.quit()

    def wait_for_key(self):
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP and (pg.time.get_ticks() - self.show_moment > 250):
                    if event.key == pg.K_RETURN:
                        waiting = False

    def startup(self):
        self.show_start_screen()

        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP and (pg.time.get_ticks() - self.show_moment > 500):
                    if event.key == pg.K_RETURN and not self.controls and not self.quitting:
                        waiting = False
                    if event.key == pg.K_c and not self.controls:
                        self.effects_sounds['searching'].play()
                        self.show_control_screen()
                    if event.key == pg.K_c and (pg.time.get_ticks() - self.show_moment > 100) and self.controls:
                        self.show_start_screen()
                        self.controls = False
                    if event.key == pg.K_l and self.language == "NL":
                        self.language = "EN"
                        self.show_start_screen()
                    if event.key == pg.K_l and (pg.time.get_ticks() - self.show_moment > 100) and self.language == "EN":
                        self.language = "NL"
                        self.show_start_screen()
                    if event.key == pg.K_ESCAPE and not self.quitting:
                        self.effects_sounds['searching'].play()
                        self.show_quit_screen()
                    if event.key == pg.K_ESCAPE and (pg.time.get_ticks() - self.show_moment > 100) and self.quitting:
                        self.show_start_screen()
                        self.quitting = False


# create the game object
g = Game()
pg.mouse.set_visible(False)
g.startup()
g.show_goal_screen()
g.show_info_screen()

while True:
    g.new()
    g.run()
    if g.hand_in:
        g.show_hand_in_screen()
    else:
        g.show_go_screen()

