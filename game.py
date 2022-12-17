import arcade
import copy
import math
import time
from threading import Lock

WINDOW_WIDTH, WINDOW_HEIGHT = arcade.window_commands.get_display_size()
SERVER_IP = '127.0.0.1'
SERVER_PORT = 65334
TITLE = 'Multiplayer game'
PLAYER_MOVE_SPEED = 5


client_input = {
    'left': 0,
    'right': 0,
    'top': 0,
    'bottom': 0,
}

client_mouse = {
    'left_mouse': 0,
    'right_mouse': 0,
}

server_output = {
    'x': 100,
    'y': 100
}

interpolate_output = {
    'x': 100,
    'y': 100
}

player_stats = {
    'kill': 0,
    'death': 0
}


players_list = []
players_list_mutex = Lock()

sprite_players_list = arcade.SpriteList()

bullet_list = arcade.SpriteList()
bullet_list_mutex = Lock()

bullet_list_client = arcade.SpriteList()
bullet_list_client_mutex = Lock()

rocket_list = arcade.SpriteList()
rocket_list_mutex = Lock()

rocket_list_client = arcade.SpriteList()
rocket_list_client_mutex = Lock()

explosion_list_mutex = Lock()

#bullet_remove = Lock()


class Player(arcade.Sprite):
    def __init__(self, address):
        super().__init__("Textures/fighter3.png", hit_box_algorithm='Detailed')
        self.client_input = copy.copy(client_input)
        self.server_output = copy.copy(server_output)
        self.interpolate_output = copy.copy(interpolate_output)
        self.player_stats = copy.copy(player_stats)
        #self.thrust = 2
        #self.rot_speed = 2
        #self.speed = 5
        self.flag_bullets = False
        self.shot_counter = 0
        self.bullets_ammunition = 100
        self.health = 100
        self.address = address  # server address
        self.server_output_buffer = []

    def on_update(self, delta_time: float = 1 / 60):
        super().update()
        self.angle = math.degrees(math.atan2(self.change_y, self.change_x))
