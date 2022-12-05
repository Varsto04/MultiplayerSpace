from game import *
import arcade
from components.chat import *
import socket
from threading import Thread
from interaction_manager import InteractionManager
import space_station as space_station
import bullet as bullet


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

        #global bullet_list
        #bullet_list = arcade.SpriteList()

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
        bullet_list.draw()

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

        bullet_list.update()

        for bullet in bullet_list:
            if bullet.center_x < 0:
                bullet.remove_from_sprite_lists()
            elif bullet.center_y < 0:
                bullet.remove_from_sprite_lists()
            elif bullet.center_x > 5000:
                bullet.remove_from_sprite_lists()
            elif bullet.center_y > 3000:
                bullet.remove_from_sprite_lists()

        for i in range(0, len(sprite_players_list)):
            if int(sprite_players_list[i].address.split(':')[1]) == int(user_socket):
                if sprite_players_list[i].angle >= 360 or sprite_players_list[i].angle <= 0:
                    if sprite_players_list[i].angle >= 360:
                        while sprite_players_list[i].angle >= 360:
                            sprite_players_list[i].angle -= 360
                    elif sprite_players_list[i].angle <= 0:
                        while sprite_players_list[i].angle <= 0:
                            sprite_players_list[i].angle += 360


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
        print(f'!!!{client_input}')

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.A:
            client_input['left'] = 0
        if symbol == arcade.key.D:
            client_input['right'] = 0
        if symbol == arcade.key.W:
            client_input['top'] = 0
        if symbol == arcade.key.S:
            client_input['bottom'] = 0

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button & arcade.MOUSE_BUTTON_LEFT:
            client_mouse['left_mouse'] = 1
            global bullet_k
            bullet_k = 1

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if button & arcade.MOUSE_BUTTON_LEFT:
            client_mouse['left_mouse'] = 0
            global bullet_k
            bullet_k = 0


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
            time.sleep(0.00005)

    def send_data(self):
        # отправление на сервер адреса, координат и угол клиента
        if 1 in client_input.values():
            #print('Sending move...')
            #data = f'g;{user_socket};'
            for i in range(0, len(sprite_players_list)):
                if int(sprite_players_list[i].address.split(':')[1]) == int(user_socket):
                    x = sprite_players_list[i].center_x
                    y = sprite_players_list[i].center_y
                    angle = sprite_players_list[i].angle
            data = f'g;{user_socket};{x}:{y};{angle};'
            data += InteractionManager.move_message(client_input)
            data = data.encode()
            try:
                self.__tcp_socket.sendall(data)
            except socket.error:
                print('Socket error')

        if 1 in client_mouse.values():
            for i in range(0, len(sprite_players_list)):
                if int(sprite_players_list[i].address.split(':')[1]) == int(user_socket):
                    x = sprite_players_list[i].center_x
                    y = sprite_players_list[i].center_y
                    angle = sprite_players_list[i].angle
            data = f'z;{user_socket};{x}:{y};{angle};'
            data += InteractionManager.move_message(client_mouse)
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
                print(data)
                for cur_data in data:
                    cur_data.strip()
                    if len(cur_data) and cur_data[0] == 'c':
                        #print(cur_data)
                        address, coords = InteractionManager.parse_coords_message(cur_data)
                        player_sprite = Player(address)
                        player_sprite.center_x = coords[0]
                        player_sprite.center_y = coords[1]
                        sprite_players_list.append(player_sprite)
                    if len(cur_data) and cur_data[0] == 'g':
                        #print(cur_data)
                        cur_data = cur_data.split(';', 1)[1]
                        cur_data = cur_data.split(';')
                        print(cur_data)
                        for i in range(0, len(sprite_players_list)):
                            if int(sprite_players_list[i].address.split(':')[1]) == int(cur_data[0]):
                                #print(cur_data)
                                x, y = cur_data[1].split(':')[0], cur_data[1].split(':')[1]
                                angle = cur_data[2]
                                sprite_players_list[i].angle = float(angle)
                                sprite_players_list[i].center_x = float(x)
                                sprite_players_list[i].center_y = float(y)
                    if len(cur_data) and cur_data[0] == 'z':
                        #print(cur_data)
                        cur_data = cur_data.split(';', 1)[1]
                        cur_data = cur_data.split(';')
                        #print(cur_data)
                        global bullet_k
                        #for i in range(0, len(sprite_players_list)):
                            #if int(sprite_players_list[i].address.split(':')[1]) == int(cur_data[0]) and bullet_k < 2:
                        if bullet_k < 2:
                            x, y = cur_data[1].split(':')[0], cur_data[1].split(':')[1]
                            angle = cur_data[2]

                            x = float(x)
                            y = float(y)
                            angle = float(angle)

                            self.bullet_sprite = bullet.Bullet()
                            self.bullet_sprite.change_x = -math.sin(math.radians(angle)) * 22
                            self.bullet_sprite.change_y = math.cos(math.radians(float(angle))) * 22

                            self.bullet_sprite_2 = bullet.Bullet()
                            self.bullet_sprite_2.change_x = -math.sin(math.radians(angle)) * 22
                            self.bullet_sprite_2.change_y = math.cos(math.radians(angle)) * 22

                            self.bullet_sprite.center_x = x
                            self.bullet_sprite.center_y = y
                            self.bullet_sprite_2.center_x = x + 10
                            self.bullet_sprite_2.center_y = y + 10

                            if (angle >= 0) and (angle <= 25):
                                self.bullet_sprite.center_x = x - 15
                                self.bullet_sprite.center_y = y
                                self.bullet_sprite_2.center_x = x + 15
                                self.bullet_sprite_2.center_y = y
                            elif (angle > 25) and (angle < 65):
                                self.bullet_sprite.center_x = x - 10
                                self.bullet_sprite.center_y = y - 10
                                self.bullet_sprite_2.center_x = x - 10
                                self.bullet_sprite_2.center_y = y + 30
                            elif (angle >= 65) and (angle <= 115):
                                self.bullet_sprite.center_x = x
                                self.bullet_sprite.center_y = y + 15
                                self.bullet_sprite_2.center_x = x
                                self.bullet_sprite_2.center_y = y - 15
                            elif (angle > 115) and (angle < 155):
                                self.bullet_sprite.center_x = x - 10
                                self.bullet_sprite.center_y = y + 10
                                self.bullet_sprite_2.center_x = x - 10
                                self.bullet_sprite_2.center_y = y - 30
                            elif (angle >= 155) and (angle <= 205):
                                self.bullet_sprite.center_x = x + 15
                                self.bullet_sprite.center_y = y
                                self.bullet_sprite_2.center_x = x - 15
                                self.bullet_sprite_2.center_y = y
                            elif (angle > 205) and (angle < 245):
                                self.bullet_sprite.center_x = x - 10
                                self.bullet_sprite.center_y = y - 10
                                self.bullet_sprite_2.center_x = x + 10
                                self.bullet_sprite_2.center_y = y + 18
                            elif (angle >= 245) and (angle <= 295):
                                self.bullet_sprite.center_x = x
                                self.bullet_sprite.center_y = y - 15
                                self.bullet_sprite_2.center_x = x
                                self.bullet_sprite_2.center_y = y + 15
                            elif (angle > 295) and (angle < 335):
                                self.bullet_sprite.center_x = x + 10
                                self.bullet_sprite.center_y = y - 10
                                self.bullet_sprite_2.center_x = x + 10
                                self.bullet_sprite_2.center_y = y + 28
                            elif (angle >= 335) and (angle <= 360):
                                self.bullet_sprite.center_x = x - 15
                                self.bullet_sprite.center_y = y
                                self.bullet_sprite_2.center_x = x + 15
                                self.bullet_sprite_2.center_y = y

                            self.bullet_sprite.angle = angle + 90
                            self.bullet_sprite.update()

                            self.bullet_sprite_2.angle = angle + 90
                            self.bullet_sprite_2.update()

                            bullet_list_mutex.acquire()
                            bullet_list.append(self.bullet_sprite)
                            bullet_list_mutex.release()

                            bullet_list_mutex.acquire()
                            bullet_list.append(self.bullet_sprite_2)
                            bullet_list_mutex.release()

                            bullet_k += 1
                print()
            except socket.error:
                break


def main():
    client = SpaceGameClient()
    if client.init():
        client.run()
    else:
        pass


if __name__ == '__main__':
    main()
