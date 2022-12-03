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


class Player(arcade.Sprite):
    def __init__(self, address):
        super().__init__("Textures/fighter3.png", hit_box_algorithm='Detailed')
        self.client_input = copy.copy(client_input)
        self.server_output = copy.copy(server_output)
        self.interpolate_output = copy.copy(interpolate_output)
        self.player_stats = copy.copy(player_stats)
        self.thrust = 2
        self.rot_speed = 2
        self.speed = 5
        self.address = address  # server address
        self.server_output_buffer = []

    def on_update(self, delta_time: float = 1 / 60):
        super().update()
        self.angle = math.degrees(math.atan2(self.change_y, self.change_x))


# class Game:
#     def __init__(self):
#         pass
#
#     def on_key_press(self, symbol: int, modifiers: int):
#         if symbol == arcade.key.Q:
#             arcade.exit()
#         if symbol == arcade.key.A:
#             client_input['left'] = 1
#         if symbol == arcade.key.D:
#             client_input['right'] = 1
#         if symbol == arcade.key.W:
#             client_input['top'] = 1
#         if symbol == arcade.key.S:
#             client_input['bottom'] = 1
#
#     def on_key_release(self, symbol: int, modifiers: int):
#         if symbol == arcade.key.A:
#             client_input['left'] = 0
#         if symbol == arcade.key.D:
#             client_input['right'] = 0
#         if symbol == arcade.key.W:
#             client_input['top'] = 0
#         if symbol == arcade.key.S:
#             client_input['bottom'] = 0
#
#     def server_update(self, delta_time):
#         print('server_update')
#         for player in players_list:
#             if player.client_input['left'] == 1:
#                 player.server_output['x'] -= PLAYER_MOVE_SPEED
#             if player.client_input['right'] == 1:
#                 player.server_output['x'] += PLAYER_MOVE_SPEED
#             if player.client_input['top'] == 1:
#                 player.server_output['y'] += PLAYER_MOVE_SPEED
#             if player.client_input['bottom'] == 1:
#                 player.server_output['y'] -= PLAYER_MOVE_SPEED
#
#     def on_draw(self):
#         arcade.start_render()
#         for player in players_list:
#             player.draw()
