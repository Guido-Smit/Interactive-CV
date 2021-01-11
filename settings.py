import pygame as pg

vec = pg.math.Vector2

# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 125, 30)
BROWN = (106, 55, 5)
BLUE = (0, 0, 255)

# game settings
WINDOWED_WIDTH = 960
WINDOWED_HEIGHT = 720
FPS = 60
TILESIZE = 64
TITLE = "Interactive CV"
INTRO_IMAGE = {"NL": "IntroscreenNL.png",
               "EN": "Introscreen.png"}

GOAL_IMAGE = {"NL": "goalNL.png",
              "EN": "goal.png"}

INFO_IMAGE = {"NL": "Game InfoNL.png",
              "EN": "Game Info.png"}

QUIT_IMAGES = {"NL": "QuitNL.png",
              "EN": "Quit.png"}

BGCOLOR = BLACK
GAMEFONT = "StressGenesis.OTF"
HUDFONT = "Basic.TTF"
TXT_FONT = "Vecna.OTF"

TIMERIMAGE = "timer.png"
TIMER = 600

EMPTY_SHOE_IMAGE = "Shoe_empty.png"

CVparts = []

BACKGROUNDIMAGE = "Openingscreen.png"
END_IMAGE = "end_screen.png"
CONTROLSIMAGE = {"NL": "controlsNL.png",
                 "EN": "controls.png"}

TEXTBOX_IMAGE = "txtbox.png"
UNDISCOVERED_IMAGE = "undiscovered.png"
CVPARTS_IMAGE = "document.png"
NPCSPRITESHEET = "officepeople.png"

# Player Settings
PLAYER_SPEED = 250
PLAYER_ROT_SPEED = 250
PLAYER_IMAGE = "guido_walk2.png"
PLAYER_STUNNED_IMAGE = "guido_stun.png"

WALK_IMAGES = {0: "guido_walk1.png",
               1: "guido_walk2.png",
               2: "guido_walk3.png"}

CRY_IMAGES = {0: "guido_walk2.png",
              1: "guido_cry1.png",
              2: "guido_cry2.png"}

CHEER_IMAGES = {0: "guido_walk2.png",
                1: "guido_cheer1.png",
                2: "guido_cheer2.png",
                3: "guido_cheer3.png",
                4: "guido_cheer4.png"}

PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
PLAYER_INTERACT_RECT = pg.Rect(0, 0, 30, 30)
PLAYER_HEALTH = 100
DAMAGE_ALPHA = [i for i in range(0, 255, 25)]

# NPC
NPC_IMAGES = {  "boss": ["Boss.png"],
                "mom": ["Mom.png"],
                "dad": ["Dad.png"],
                "worker": ["Worker.png"],
                "lady": ["Lady.png", "Lady2.png"],
                "guy1": ["Guy1.png"],
                "guy2": ["Guy2.png"],
                "easteregg": ["Easter.png"],
                 "lady_ponytail": ["Lady_Ponytail.png", "Lady_Ponytail2.png", "Lady_Ponytail3.png", "Lady_Ponytail2.png"],
                "police": ["Police.png"],
                "baldguy": ["Baldguy.png"],
                "footballplayer1": ["footballplayer1.png"],
                "footballplayer2": ["footballplayer2.png"],
                "footballplayer3": ["footballplayer3.png"],
                "footballplayer4": ["footballplayer4.png"],
                "cashier": ["Cashier1.png", "Cashier2.png"]}

NPC_SIZE = 64

# Cars

CAR_SIZE = 64
CAR_DAMAGE = 20
CAR_KNOCKBACK = 400
CAR_IMAGES = {"black": ["car_black_1.png"],
              "blue": ["car_blue_1.png"],
              "green": ["car_green_1.png"],
              "yellow": ["car_yellow_1.png"],
              "red": ["car_red_1.png"]
              }

# Layers
WALL_LAYER = 1
PLAYER_LAYER = 3
EFFECTS_LAYER = 4
ITEM_LAYER = 1
NPC_LAYER = 2
CAR_LAYER = 4

# Items
ITEM_IMAGES = {"Health": "healthpack.png",
               "Time": "time.png",
               "Running shoes": "Shoe.png"}
ITEM_SIZE = 30
HEALTH_PACK_AMOUNT = 50
BOUNCE_RANGE = 15
BOUNCE_SPEED = 0.3

# UI images
STAR_IMAGES = {"0": "zero_stars.png",
               "1": "one_star.png",
               "2": "two_stars.png",
               "3": "three_stars.png",
               "4": "four_stars.png",
               "5": "five_stars.png",
               "6": "perfect_stars.png"}

PERFECT_STAMPS = {"Right": "Perfect_right.png",
                  "Left": "Perfect_left.png"}

# CV
CVPARTS = {"NL": {"CV1": "CV1NL.png",
                  "CV2": "CV2NL.png",
                  "CV3": "CV3NL.png",
                  "CV4": "CV4NL.png",
                  "CV5": "CV5NL.png",
                  "CV6": "CV6NL.png",
                  "CV7": "CV7NL.png",
                  "CV8": "CV8NL.png",
                  "CV9": "CV9NL.png",
                  "CV10": "CV10NL.png"},
           "EN": {"CV1": "CV1.png",
                  "CV2": "CV2.png",
                  "CV3": "CV3.png",
                  "CV4": "CV4.png",
                  "CV5": "CV5.png",
                  "CV6": "CV6.png",
                  "CV7": "CV7.png",
                  "CV8": "CV8.png",
                  "CV9": "CV9.png",
                  "CV10": "CV10.png"
                  }
           }

# List of collections (Ex. 1/2/3/4/5)
# CV parts
PARTSCOLLECTED = []
# Timeboosts
TIMEBOOSTSCOLLECTED = []
# Shoes
SPEEDBOOSTSCOLLECTED = []
# Healthpacks
HEALTHCOLLECTED = []

MenuPieces = []
FLAGS = {"NL": "Dutch.png",
         "EN": "English.png"}

# Sounds
MUSIC = {"town": "TownTheme.wav",
         "gameover": "Game Over.wav",
         "victory": "Victory.wav"}

PLAYER_HIT_SOUNDS = ["Grunt.wav"]
PLAYER_DEATH_SOUNDS = ["Death.wav"]

EFFECT_SOUNDS = {"Health": "health.wav",
                 "searching": "search sound 1.wav",
                 "Time": "time.wav",
                 "Clock": "Clock.wav",
                 "Car": "Car_Horn.wav",
                 "Menu": "Menu Selection Click.wav",
                 "Speedboost": "Speedboost.wav",
                 "Bird1": "Bird1.wav"}
