from game import *
import arcade
from components.chat import *
import socket
from threading import Thread
from interaction_manager import InteractionManager
import space_station as space_station


BUFSIZE = 1024
SENDING_SPEED = 1/30
ADDRESS = (SERVER_IP, SERVER_PORT)

# tcp_socket = None
# udp_socket = None
# window = None
# game = None
# work = True


#sprite_players_list = None


class SpaceGameClient:
    def __init__(self):
        self.__tcp_socket = None
        self.__tcp_receiever = None
        self.__own_address = None
        self.__move_sender = None

    def __del__(self):
        if self.__tcp_socket:
            self.__tcp_socket.close()
        if self.__tcp_receiever:
            self.__tcp_receiever.join()
        if self.__move_sender:
            self.__move_sender.join()

    def init(self) -> bool:
        self.__tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.__tcp_socket.connect(ADDRESS)
        except ConnectionRefusedError:
            print('Unable to connect to server')
            return False
        self.__own_address = self.__tcp_socket.getpeername()
        self.__tcp_receiever = TCPReciv(self.__tcp_socket)
        self.__tcp_receiever.start()
        self.__move_sender = TCPSend(self.__tcp_socket)
        self.__move_sender.start()

        global user_socket
        user_socket = self.__tcp_socket.getsockname()[1]
        return True

    def run(self):
        window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, TITLE, fullscreen=True)
        game = ClientGame()
        window.show_view(game)
        arcade.run()


class ClientGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.time = None
        self.window.set_mouse_visible(False)
        self.background = arcade.load_texture(":resources:images/backgrounds/stars.png")

        self.camera = arcade.Camera(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.space_station_list = arcade.SpriteList()
        self.npc_station_list = arcade.SpriteList()

        self.space_station = space_station.Station()
        self.space_station.center_x = 2100
        self.space_station.center_y = 1100
        self.space_station_list.append(self.space_station)

        self.space_station_2 = space_station.Station2()
        self.space_station_2.center_x = 2100
        self.space_station_2.center_y = 1500
        self.space_station_list.append(self.space_station_2)

        self.space_station_3 = space_station.Station3()
        self.space_station_3.center_x = 2500
        self.space_station_3.center_y = 1100
        self.space_station_list.append(self.space_station_3)

        self.space_station_4 = space_station.Station4()
        self.space_station_4.center_x = 2500
        self.space_station_4.center_y = 1500
        self.space_station_list.append(self.space_station_4)

        self.npc_station = space_station.StationNPC()
        self.npc_station.center_x = 200
        self.npc_station.center_y = 200
        self.npc_station_list.append(self.npc_station)

        self.npc_station_2 = space_station.StationNPC()
        self.npc_station_2.center_x = 200
        self.npc_station_2.center_y = 2800
        self.npc_station_list.append(self.npc_station_2)

        self.npc_station_3 = space_station.StationNPC()
        self.npc_station_3.center_x = 4800
        self.npc_station_3.center_y = 200
        self.npc_station_list.append(self.npc_station_3)

        self.npc_station_4 = space_station.StationNPC()
        self.npc_station_4.center_x = 4800
        self.npc_station_4.center_y = 2800
        self.npc_station_list.append(self.npc_station_4)

        arcade.set_background_color((0, 0, 0))

    def on_draw(self):
        self.clear()
        for x in range(0, 6000, 1500):
            for y in range(0, 4000, 1000):
                arcade.draw_lrwh_rectangle_textured(x, y, 1500, 1000, self.background)
        self.camera.use()
        sprite_players_list.draw()
        self.space_station_list.draw()
        self.npc_station_list.draw()

    def on_update(self, delta_time: float):
        self.center_camera_to_player()

        self.space_station.angle += 0.125
        self.space_station_2.angle += 0.125
        self.space_station_3.angle += 0.125
        self.space_station_4.angle += 0.125

        self.npc_station.angle += 0.125
        self.npc_station_2.angle += 0.125
        self.npc_station_3.angle += 0.125
        self.npc_station_4.angle += 0.125

    def center_camera_to_player(self):
        for i in range(0, len(sprite_players_list)):
            if int(sprite_players_list[i].address.split(':')[1]) == int(user_socket):
                screen_center_x = sprite_players_list[i].center_x - (self.camera.viewport_width/2)
                screen_center_y = sprite_players_list[i].center_y - (self.camera.viewport_height/2)

                if screen_center_x < 0:
                    screen_center_x = 0
                if screen_center_y < 0:
                    screen_center_y = 0

                player_centered = screen_center_x, screen_center_y

                self.camera.move_to(player_centered)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.Q:
            arcade.exit()
        if symbol == arcade.key.A:
            client_input['left'] = 1
        if symbol == arcade.key.D:
            client_input['right'] = 1
        if symbol == arcade.key.W:
            client_input['top'] = 1
        if symbol == arcade.key.S:
            client_input['bottom'] = 1

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.A:
            client_input['left'] = 0
        if symbol == arcade.key.D:
            client_input['right'] = 0
        if symbol == arcade.key.W:
            client_input['top'] = 0
        if symbol == arcade.key.S:
            client_input['bottom'] = 0

    def server_update(self, delta_time):
        for player in players_list:
            if player.client_input['left'] == 1:
                player.server_output['x'] -= PLAYER_MOVE_SPEED
            if player.client_input['right'] == 1:
                player.server_output['x'] += PLAYER_MOVE_SPEED
            if player.client_input['top'] == 1:
                player.server_output['y'] += PLAYER_MOVE_SPEED
            if player.client_input['bottom'] == 1:
                player.server_output['y'] -= PLAYER_MOVE_SPEED


def remove_player(address):
    for player in players_list:
        if player.address == address:
            players_list.remove(player)
            break


class TCPSend(Thread):
    def __init__(self, tcp_sock):
        super().__init__()
        self.__tcp_socket = tcp_sock
        self.work = True

    def run(self):
        while True:
            self.send_data()
            time.sleep(0.0005)

    def send_data(self):
        if 1 in client_input.values():
            print('Sending move...')
            data = f'g;{user_socket};'
            for i in range(0, len(sprite_players_list)):
                if int(sprite_players_list[i].address.split(':')[1]) == int(user_socket):
                    pass
            data += InteractionManager.move_message(client_input)
            data = data.encode()
            try:
                self.__tcp_socket.sendall(data)
            except socket.error:
                print('Socket error')


class TCPReciv(Thread):
    def __init__(self, tcp_sock):
        super().__init__()
        self.__tcp_socket = tcp_sock
        self.work = True

    def run(self):
        while self.work:
            try:
                data = self.__tcp_socket.recv(BUFSIZE).decode('utf-8')
                data = data.split('#')
                #print(data)
                for cur_data in data:
                    cur_data.strip()
                    if len(cur_data) and cur_data[0] == 'c':
                        print(cur_data)
                        address, coords = InteractionManager.parse_coords_message(cur_data)
                        player_sprite = Player(address)
                        player_sprite.center_x = coords[0]
                        player_sprite.center_y = coords[1]
                        sprite_players_list.append(player_sprite)
                    if len(cur_data) and cur_data[0] == 'g':
                        cur_data = cur_data.split(';')[1]
                        cur_data = cur_data.split(':')
                        for i in range(0, len(sprite_players_list)):
                            if int(sprite_players_list[i].address.split(':')[1]) == int(cur_data[0]):
                                if cur_data[1] == '+y':
                                    sprite_players_list[i].center_y += 2
                                if cur_data[1] == '-y':
                                    sprite_players_list[i].center_y -= 2
                                if cur_data[1] == '+x':
                                    sprite_players_list[i].center_x += 2
                                if cur_data[1] == '-x':
                                    sprite_players_list[i].center_x -= 2
                print()
            except socket.error:
                break


# class UDPRecive(Thread):
#     def __init__(self):
#         super().__init__()
#         self.work = True
#
#     def update_player(self, player, data):
#         count = 2
#         for key in player.server_output.keys():
#             player.server_output[key] = int(data[count])
#             count += 1
#
#         if len(player.server_output_buffer) == 2:
#             player.server_output_buffer.pop(0)
#         if game is not None:
#             player.server_output_buffer.append((copy.copy(player.server_output), game.time))
#
#     def create_player(self, data):
#         player_address = (data[0], int(data[1]))
#         player = Player(player_address)
#         players_list.append(player)
#         self.update_player(player, data)
#
#     def run(self):
#         while self.work:
#             try:
#                 data, address = udp_socket.recvfrom(BUFSIZE)
#             except socket.error:
#                 break
#             data = data.decode('utf-8')
#
#             players = data.split(';;')
#             for player_data in players:
#                 player_data = player_data.split(';')
#                 player_address = (player_data[0], int(player_data[1]))
#                 player_exist = False
#                 for _player in players_list:
#                     if _player.address == player_address:
#                         player_exist = True
#                         self.update_player(_player, player_data)
#                         break
#                 if player_exist == False:
#                     self.create_player(player_data)
#
#
# def UDPSend(delta_time):
#     if 1 in client_input.values():
#         data = ''
#         for values in client_input.values():
#             data += str(values) + ';'
#         data = data[:-1].encode()
#         udp_socket.sendto(data, ADDRESS)


def main():
    client = SpaceGameClient()
    if client.init():
        client.run()
    else:
        pass

    # global window
    # global game
    # tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tcp_socket.connect(ADDRESS)
    # tcp_reciver = TCPReciv()
    # tcp_reciver.start()
    #
    # udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # udp_socket.bind(tcp_socket.getsockname())
    # udp_reciver = UDPRecive()
    # udp_reciver.start()
    #
    # arcade.schedule(UDPSend, SENDING_SPEED)
    #
    # window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, TITLE, fullscreen=True)
    # game = ClientGame()
    # window.show_view(game)
    # arcade.run()
    #
    # arcade.unschedule(UDPSend)
    # tcp_reciver.work = False
    # udp_reciver.work = False
    # tcp_socket.close()
    # udp_socket.close()
    # tcp_reciver.join()
    # udp_reciver.join()
    # print(f'tcp_reciver: {tcp_reciver.is_alive()}')
    # print(f'udp_reciver: {udp_reciver.is_alive()}')
    # sys.exit()


if __name__ == '__main__':
    main()
