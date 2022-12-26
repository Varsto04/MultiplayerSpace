import sys

from game import *
import arcade
import socket
from threading import Thread
from interaction_manager import InteractionManager
import space_station as space_station
import bullet as bullet
import rocket as rocket
import server as server
import explosion as expl
import icons as icons
import arcade.gui
import time


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
        game = StartView()
        window.show_view(game)
        arcade.run()


class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = None

        self.texture = arcade.load_texture(":resources:images/backgrounds/stars.png")

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.v_box = arcade.gui.UIBoxLayout()

        #sound_button = arcade.Sound(file_name='Sounds/Retro3.wav')

        button_style = {
            "font_size": 30,
            "font_color": arcade.color.AQUA,
            "border_width": 2,
            "border_color": arcade.color.AQUA,
            "bg_color": None,

            "bg_color_pressed": None,
            "border_color_pressed": arcade.color.BLUE,
            "font_color_pressed": arcade.color.BLUE,
        }

        start_button = arcade.gui.UIFlatButton(text="Начать", width=400, height=100, font_size=100, style=button_style)
        self.v_box.add(start_button.with_space_around(bottom=20))

        # authors_button = arcade.gui.UIFlatButton(text="Авторы", width=400, height=100, style=button_style)
        # self.v_box.add(authors_button.with_space_around(bottom=20))

        quit_button = arcade.gui.UIFlatButton(text="Выход", width=400, height=100, style=button_style)
        self.v_box.add(quit_button.with_space_around(bottom=20))

        @start_button.event("on_click")
        def on_click_start(event):
            #arcade.play_sound(sound_button)
            game_view = EnterView()
            self.window.show_view(game_view)
            self.manager.disable()

        @quit_button.event("on_click")
        def on_click_quit(event):
            #arcade.play_sound(sound_button)
            arcade.close_window()
            arcade.exit()

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box,)
        )

        arcade.set_background_color((0, 0, 0))

    def on_draw(self):
        self.clear()
        self.texture.draw_sized(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
                                WINDOW_WIDTH, WINDOW_HEIGHT)
        self.manager.draw()


class EnterView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = None

        self.texture = arcade.load_texture(":resources:images/backgrounds/stars.png")

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.v_box = arcade.gui.UIBoxLayout()

        #self.sound_button = arcade.Sound(file_name='Sounds/Retro3.wav')

        button_style = {
            "font_size": 30,
            "font_color": arcade.color.AQUA,
            "border_width": 2,
            "border_color": arcade.color.AQUA,
            "bg_color": None,

            "bg_color_pressed": None,
            "border_color_pressed": arcade.color.BLUE,
            "font_color_pressed": arcade.color.BLUE,
        }

        self.input_field = arcade.gui.UIInputText(text="Введите сюда ваш ник", width=650, height=40, font_size=24,
                                                  text_color=arcade.color.AQUA)
        self.v_box.add(self.input_field)

        self.label = arcade.gui.UILabel(text=f"#Ваш ник: ", width=650, height=40, font_size=16,
                                        text_color=arcade.color.AQUA)
        self.v_box.add(self.label.with_space_around(bottom=0))

        self.label2 = arcade.gui.UILabel(text="", width=650, height=40, font_size=16,
                                         text_color=arcade.color.AQUA)

        submit_button = arcade.gui.UIFlatButton(text="Обновить", width=400, height=40, style=button_style)
        self.v_box.add(submit_button.with_space_around(bottom=10))
        submit_button.on_click = self.on_click

        clear_button = arcade.gui.UIFlatButton(text="Очистить", width=400, height=40, style=button_style)
        self.v_box.add(clear_button.with_space_around(bottom=300))

        start_button = arcade.gui.UIFlatButton(text="Продолжить", width=400, height=100, style=button_style)
        self.v_box.add(start_button.with_space_around(bottom=20))

        back_button = arcade.gui.UIFlatButton(text="Назад", width=400, height=100, style=button_style)
        self.v_box.add(back_button)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box, )
        )

        @clear_button.event("on_click")
        def on_click_start(event):
            #arcade.play_sound(self.sound_button)
            self.input_field.text = ''

        @start_button.event("on_click")
        def on_click_start(event):
            #arcade.play_sound(self.sound_button)
            if (len(self.input_field.text) <= 20) and (self.input_field.text != 'Введите сюда ваш ник'):
                #arcade.play_sound(self.sound_button)
                game_view = ClientGame()
                self.window.show_view(game_view)
                self.manager.disable()
            else:
                if len(self.input_field.text) > 20:
                    self.label2.text = '#Ваш ник не должен превышать 20 символов'
                    self.v_box.add(self.label2.with_space_around(bottom=0))
                elif self.input_field.text == 'Введите сюда ваш ник':
                    self.label2.text = '#Вы забыли изменить ник или нажать кнопку "Обновить"'
                    self.v_box.add(self.label2.with_space_around(bottom=0))

        @back_button.event("on_click")
        def on_click_quit(event):
            #arcade.play_sound(self.sound_button)
            game_view = StartView()
            self.window.show_view(game_view)
            self.manager.disable()

        arcade.set_background_color((0, 0, 0))

    def on_draw(self):
        self.clear()
        self.texture.draw_sized(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
                                WINDOW_WIDTH, WINDOW_HEIGHT)
        self.manager.draw()

    def update_text(self):
        self.label.text = f'#Ваш ник: {self.input_field.text}'
        global nickname
        nickname = self.input_field.text

    def on_click(self, event):
        #arcade.play_sound(self.sound_button)
        self.update_text()


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

        self.icon_rocket = icons.IconRocket(1)
        self.icon_rocket_2 = icons.IconRocket(2)
        self.icon_bullet = icons.IconBullet(1)
        self.icon_bullet_2 = icons.IconBullet(2)

        self.explosion_texture_list = []
        columns = 16
        count = 60
        sprite_width = 256
        sprite_height = 256
        file_name = ":resources:images/spritesheets/explosion.png"
        self.explosion_texture_list = arcade.load_spritesheet(file_name, sprite_width, sprite_height, columns, count)
        self.explosions_list = arcade.SpriteList()

        #global bullet_k
        #bullet_k = 1

        global bullet_flag
        bullet_flag = True

        # global bullets_flag
        # bullets_flag = False

        # global shot_counter
        # shot_counter = 0

        #self.sound_explosion = arcade.Sound(file_name="Sounds/explosion09.wav")

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
        bullet_list_client.draw()
        rocket_list.draw()
        rocket_list_client.draw()
        self.explosions_list.draw()

        for i in range(0, len(sprite_players_list)):
            if int(sprite_players_list[i].address.split(':')[1]) == int(user_socket):
                self.score_text = f'Health: {sprite_players_list[i].health}|Ammunition: {sprite_players_list[i].bullets_ammunition}'
                arcade.draw_text(
                    self.score_text,
                    sprite_players_list[i].center_x - 150,
                    sprite_players_list[i].center_y + 70,
                    arcade.csscolor.AQUA,
                    18,
                )

                global nickname
                self.rating_table = f'{nickname}'
                arcade.draw_text(
                    self.rating_table,
                    sprite_players_list[i].center_x - 30,
                    sprite_players_list[i].center_y + 110,
                    arcade.csscolor.AQUA,
                    18,
                )

        self.icon_rocket.draw()
        self.icon_rocket_2.draw()
        self.icon_bullet.draw()
        self.icon_bullet_2.draw()

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
        bullet_list_client.update()

        rocket_list.update()
        rocket_list_client.update()

        for bullet in bullet_list:
            if bullet.center_x < 0:
                bullet.remove_from_sprite_lists()
            elif bullet.center_y < 0:
                bullet.remove_from_sprite_lists()
            elif bullet.center_x > 5000:
                bullet.remove_from_sprite_lists()
            elif bullet.center_y > 3000:
                bullet.remove_from_sprite_lists()

        for rocket in rocket_list:
            if rocket.center_x < 0:
                rocket.remove_from_sprite_lists()
            elif rocket.center_y < 0:
                rocket.remove_from_sprite_lists()
            elif rocket.center_x > 5000:
                rocket.remove_from_sprite_lists()
            elif rocket.center_y > 3000:
                rocket.remove_from_sprite_lists()

        for bullet_client in bullet_list_client:
            if bullet_client.center_x < 0:
                bullet_client.remove_from_sprite_lists()
            elif bullet_client.center_y < 0:
                bullet_client.remove_from_sprite_lists()
            elif bullet_client.center_x > 5000:
                bullet_client.remove_from_sprite_lists()
            elif bullet_client.center_y > 3000:
                bullet_client.remove_from_sprite_lists()

        for rocket_client in rocket_list_client:
            if rocket_client.center_x < 0:
                rocket_client.remove_from_sprite_lists()
            elif rocket_client.center_y < 0:
                rocket_client.remove_from_sprite_lists()
            elif rocket_client.center_x > 5000:
                rocket_client.remove_from_sprite_lists()
            elif rocket_client.center_y > 3000:
                rocket_client.remove_from_sprite_lists()

        for i in range(0, len(sprite_players_list)):
            if int(sprite_players_list[i].address.split(':')[1]) == int(user_socket):
                if sprite_players_list[i].angle >= 360 or sprite_players_list[i].angle <= 0:
                    if sprite_players_list[i].angle >= 360:
                        while sprite_players_list[i].angle >= 360:
                            sprite_players_list[i].angle -= 360
                    elif sprite_players_list[i].angle <= 0:
                        while sprite_players_list[i].angle <= 0:
                            sprite_players_list[i].angle += 360

        for i in range(0, len(sprite_players_list)):
            if int(sprite_players_list[i].address.split(':')[1]) == int(user_socket):
                if sprite_players_list[i].center_x < 45:
                    sprite_players_list[i].center_x += 20
                elif sprite_players_list[i].center_y < 45:
                    sprite_players_list[i].center_y += 20
                elif sprite_players_list[i].center_y > 2955:
                    sprite_players_list[i].center_y -= 20
                elif sprite_players_list[i].center_x > 4955:
                    sprite_players_list[i].center_x -= 20

        for bullet in bullet_list:
            for i in range(0, len(sprite_players_list)):
                if int(sprite_players_list[i].address.split(':')[1]) == int(user_socket):
                    collision_player_bullet = arcade.check_for_collision(bullet, sprite_players_list[i])
                    if collision_player_bullet:
                        #bullet_remove.acquire()
                        bullet.remove_from_sprite_lists()
                        #bullet_remove.release()
                        sprite_players_list[i].health -= 5

        for rocket in rocket_list:
            for i in range(0, len(sprite_players_list)):
                if int(sprite_players_list[i].address.split(':')[1]) == int(user_socket):
                    collision_player_bullet = arcade.check_for_collision(rocket, sprite_players_list[i])
                    if collision_player_bullet:
                        rocket.remove_from_sprite_lists()
                        sprite_players_list[i].health -= 50

        for bullet_client in bullet_list_client:
            for i in range(0, len(sprite_players_list)):
                if int(sprite_players_list[i].address.split(':')[1]) != int(user_socket):
                    collision_player_client_bullet = arcade.check_for_collision(bullet_client, sprite_players_list[i])
                    if collision_player_client_bullet:
                        #bullet_remove.acquire()
                        bullet_client.remove_from_sprite_lists()
                        #bullet_remove.release()
                        sprite_players_list[i].health -= 5

        for rocket_client in rocket_list_client:
            for i in range(0, len(sprite_players_list)):
                if int(sprite_players_list[i].address.split(':')[1]) != int(user_socket):
                    collision_player_client_bullet = arcade.check_for_collision(rocket_client, sprite_players_list[i])
                    if collision_player_client_bullet:
                        rocket_client.remove_from_sprite_lists()
                        sprite_players_list[i].health -= 50

        for i in range(0, len(sprite_players_list)):
            for j in range(0, len(sprite_players_list)):
                collision_players = arcade.check_for_collision(sprite_players_list[j], sprite_players_list[i])
                if collision_players and i != j:
                    sprite_players_list[j].health -= 25
                    sprite_players_list[i].health -= 25
                    explosion = expl.Explosion(self.explosion_texture_list)
                    explosion.scale = 3
                    explosion.center_x = sprite_players_list[i].center_x
                    explosion.center_y = sprite_players_list[i].center_y
                    explosion.update()
                    explosion_list_mutex.acquire()
                    self.explosions_list.append(explosion)
                    explosion_list_mutex.release()
                    #arcade.play_sound(self.sound_explosion, volume=0.1)
                    sprite_players_list[i].center_x -= 80
                    sprite_players_list[i].center_y -= 80
                    sprite_players_list[j].center_x += 80
                    sprite_players_list[j].center_y += 80

        for i in range(0, len(sprite_players_list)):
            if sprite_players_list[i].health <= 0:
                explosion = expl.Explosion(self.explosion_texture_list)
                explosion.center_x = sprite_players_list[i].center_x
                explosion.center_y = sprite_players_list[i].center_y
                explosion.update()
                explosion_list_mutex.acquire()
                self.explosions_list.append(explosion)
                explosion_list_mutex.release()
                if i == 0:
                    sprite_players_list[i].center_x = server.DEFAULT_COORD[0][0]
                    sprite_players_list[i].center_y = server.DEFAULT_COORD[0][1]
                elif i == 1:
                    sprite_players_list[i].center_x = server.DEFAULT_COORD[1][0]
                    sprite_players_list[i].center_y = server.DEFAULT_COORD[1][1]
                elif i == 2:
                    sprite_players_list[i].center_x = server.DEFAULT_COORD[2][0]
                    sprite_players_list[i].center_y = server.DEFAULT_COORD[2][1]
                elif i == 3:
                    sprite_players_list[i].center_x = server.DEFAULT_COORD[3][0]
                    sprite_players_list[i].center_y = server.DEFAULT_COORD[3][1]
                sprite_players_list[i].health = 100

        for i in range(0, len(sprite_players_list)):
            if i == 0:
                collision_player_station = arcade.check_for_collision(sprite_players_list[i], self.space_station)
            elif i == 1:
                collision_player_station = arcade.check_for_collision(sprite_players_list[i], self.space_station_2)
            elif i == 2:
                collision_player_station = arcade.check_for_collision(sprite_players_list[i], self.space_station_3)
            elif i == 3:
                collision_player_station = arcade.check_for_collision(sprite_players_list[i], self.space_station_4)

            if collision_player_station and sprite_players_list[i].health != 100:
                sprite_players_list[i].health += 0.125
                print(sprite_players_list[i].health)

        for i in range(0, len(sprite_players_list)):
            collision_players_npcstation = arcade.check_for_collision(sprite_players_list[i], self.npc_station)
            if collision_players_npcstation and sprite_players_list[i].bullets_ammunition != 100:
                sprite_players_list[i].bullets_ammunition += 1
                print(sprite_players_list[i].bullets_ammunition)

            collision_players_npcstation2 = arcade.check_for_collision(sprite_players_list[i], self.npc_station_2)
            if collision_players_npcstation2 and sprite_players_list[i].bullets_ammunition != 100:
                sprite_players_list[i].bullets_ammunition += 1
                print(sprite_players_list[i].bullets_ammunition)

            collision_players_npcstation3 = arcade.check_for_collision(sprite_players_list[i], self.npc_station_3)
            if collision_players_npcstation3 and sprite_players_list[i].bullets_ammunition != 100:
                sprite_players_list[i].bullets_ammunition += 1
                print(sprite_players_list[i].bullets_ammunition)

            collision_players_npcstation4 = arcade.check_for_collision(sprite_players_list[i], self.npc_station_4)
            if collision_players_npcstation4 and sprite_players_list[i].bullets_ammunition != 100:
                sprite_players_list[i].bullets_ammunition += 1
                print(sprite_players_list[i].bullets_ammunition)

        for i in range(0, len(sprite_players_list)):
            collision_player_icon_bullet = arcade.check_for_collision(sprite_players_list[i], self.icon_bullet)
            if collision_player_icon_bullet:
                sprite_players_list[i].flag_bullets = True
                sprite_players_list[i].shot_counter = 0

            collision_player_icon_bullet2 = arcade.check_for_collision(sprite_players_list[i], self.icon_bullet_2)
            if collision_player_icon_bullet2:
                sprite_players_list[i].flag_bullets = True
                sprite_players_list[i].shot_counter = 0

        for i in range(0, len(sprite_players_list)):
            collision_player_icon_rocket = arcade.check_for_collision(sprite_players_list[i], self.icon_rocket)
            if collision_player_icon_rocket:
                sprite_players_list[i].flag_rocket = True

            collision_player_icon_rocket2 = arcade.check_for_collision(sprite_players_list[i], self.icon_rocket_2)
            if collision_player_icon_rocket2:
                sprite_players_list[i].flag_rocket = True

        self.explosions_list.update()

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
            arcade.close_window()
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

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button & arcade.MOUSE_BUTTON_LEFT:
            for i in range(0, len(sprite_players_list)):
                if int(sprite_players_list[i].address.split(':')[1]) == int(user_socket) and \
                        sprite_players_list[i].bullets_ammunition > 3:
                    client_mouse['left_mouse'] = 1

                    if not(sprite_players_list[i].flag_bullets):
                        sprite_players_list[i].bullets_ammunition -= 2

                    elif sprite_players_list[i].flag_bullets:
                        sprite_players_list[i].bullets_ammunition -= 4

        if button & arcade.MOUSE_BUTTON_RIGHT:
            for i in range(0, len(sprite_players_list)):
                if int(sprite_players_list[i].address.split(':')[1]) == int(user_socket) and \
                        sprite_players_list[i].bullets_ammunition > 3:
                    if sprite_players_list[i].flag_rocket:
                        client_mouse['right_mouse'] = 1
                        sprite_players_list[i].bullets_ammunition -= 1

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        global bullet_flag
        if button & arcade.MOUSE_BUTTON_LEFT:
            client_mouse['left_mouse'] = 0
            bullet_flag = True

        if button & arcade.MOUSE_BUTTON_RIGHT:
            client_mouse['right_mouse'] = 0
            bullet_flag = True
            for i in range(0, len(sprite_players_list)):
                if int(sprite_players_list[i].address.split(':')[1]) == int(user_socket):
                    sprite_players_list[i].flag_rocket = False


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
            time.sleep(0.000005)

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

        global bullet_flag
        if 1 in client_mouse.values() and bullet_flag:
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
                bullet_flag = False
            except socket.error:
                print('Socket error')


class TCPReciv(Thread):
    def __init__(self, tcp_sock):
        super().__init__()
        self.__tcp_socket = tcp_sock
        self.work = True
        #self.sound_laser = arcade.Sound(file_name=":resources:sounds/laser1.mp3")

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
                        x, y = cur_data[1].split(':')[0], cur_data[1].split(':')[1]
                        angle = cur_data[2]

                        shot_type = cur_data[3].split(':')
                        print(shot_type)

                        x = float(x)
                        y = float(y)
                        angle = float(angle)

                        if shot_type[0] == '1':
                            self.bullet_sprite = bullet.Bullet()
                            self.bullet_sprite.change_x = -math.sin(math.radians(angle)) * 22
                            self.bullet_sprite.change_y = math.cos(math.radians(angle)) * 22

                            self.bullet_sprite_2 = bullet.Bullet()
                            self.bullet_sprite_2.change_x = -math.sin(math.radians(angle)) * 22
                            self.bullet_sprite_2.change_y = math.cos(math.radians(angle)) * 22

                            for i in range(0, len(sprite_players_list)):
                                if int(sprite_players_list[i].address.split(':')[1]) == int(cur_data[0]):
                                    if sprite_players_list[i].flag_bullets and sprite_players_list[i].shot_counter < 10:
                                        self.bullet_sprite_3 = bullet.Bullet()
                                        self.bullet_sprite_3.change_x = -math.sin(math.radians(angle)) * 22
                                        self.bullet_sprite_3.change_y = math.cos(math.radians(angle)) * 22

                                        self.bullet_sprite_4 = bullet.Bullet()
                                        self.bullet_sprite_4.change_x = -math.sin(math.radians(angle)) * 22
                                        self.bullet_sprite_4.change_y = math.cos(math.radians(angle)) * 22

                                        sprite_players_list[i].shot_counter += 1

                                        if (angle >= 0) and (angle <= 25):
                                            self.bullet_sprite_3.center_x = x - 50
                                            self.bullet_sprite_3.center_y = y
                                            self.bullet_sprite_4.center_x = x + 50
                                            self.bullet_sprite_4.center_y = y
                                        elif (angle > 25) and (angle < 65):
                                            self.bullet_sprite_3.center_x = x - 45
                                            self.bullet_sprite_3.center_y = y - 45
                                            self.bullet_sprite_4.center_x = x + 65
                                            self.bullet_sprite_4.center_y = y
                                        elif (angle >= 65) and (angle <= 115):
                                            self.bullet_sprite_3.center_x = x
                                            self.bullet_sprite_3.center_y = y + 50
                                            self.bullet_sprite_4.center_x = x
                                            self.bullet_sprite_4.center_y = y - 50
                                        elif (angle > 115) and (angle < 155):
                                            self.bullet_sprite_3.center_x = x - 45
                                            self.bullet_sprite_3.center_y = y + 45
                                            self.bullet_sprite_4.center_x = x - 45
                                            self.bullet_sprite_4.center_y = y - 65
                                        elif (angle >= 155) and (angle <= 205):
                                            self.bullet_sprite_3.center_x = x + 50
                                            self.bullet_sprite_3.center_y = y
                                            self.bullet_sprite_4.center_x = x - 50
                                            self.bullet_sprite_4.center_y = y
                                        elif (angle > 205) and (angle < 245):
                                            self.bullet_sprite_3.center_x = x - 45
                                            self.bullet_sprite_3.center_y = y - 45
                                            self.bullet_sprite_4.center_x = x + 45
                                            self.bullet_sprite_4.center_y = y + 53
                                        elif (angle >= 245) and (angle <= 295):
                                            self.bullet_sprite_3.center_x = x
                                            self.bullet_sprite_3.center_y = y - 50
                                            self.bullet_sprite_4.center_x = x
                                            self.bullet_sprite_4.center_y = y + 50
                                        elif (angle > 295) and (angle < 335):
                                            self.bullet_sprite_3.center_x = x + 45
                                            self.bullet_sprite_3.center_y = y - 45
                                            self.bullet_sprite_4.center_x = x + 45
                                            self.bullet_sprite_4.center_y = y + 63
                                        elif (angle >= 335) and (angle <= 360):
                                            self.bullet_sprite_3.center_x = x - 50
                                            self.bullet_sprite_3.center_y = y
                                            self.bullet_sprite_4.center_x = x + 50
                                            self.bullet_sprite_4.center_y = y

                                        self.bullet_sprite_3.angle = angle + 90
                                        self.bullet_sprite_3.update()

                                        self.bullet_sprite_4.angle = angle + 90
                                        self.bullet_sprite_4.update()

                                        if sprite_players_list[i].shot_counter >= 10:
                                            sprite_players_list[i].flag_bullets = False

                                        if int(cur_data[0]) == int(user_socket):
                                            bullet_list_client_mutex.acquire()
                                            bullet_list_client.append(self.bullet_sprite_3)
                                            bullet_list_client_mutex.release()

                                            bullet_list_client_mutex.acquire()
                                            bullet_list_client.append(self.bullet_sprite_4)
                                            bullet_list_client_mutex.release()
                                        else:
                                            bullet_list_mutex.acquire()
                                            bullet_list.append(self.bullet_sprite_3)
                                            bullet_list_mutex.release()

                                            bullet_list_mutex.acquire()
                                            bullet_list.append(self.bullet_sprite_4)
                                            bullet_list_mutex.release()

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

                            if int(cur_data[0]) == int(user_socket):
                                bullet_list_client_mutex.acquire()
                                bullet_list_client.append(self.bullet_sprite)
                                bullet_list_client_mutex.release()

                                bullet_list_client_mutex.acquire()
                                bullet_list_client.append(self.bullet_sprite_2)
                                bullet_list_client_mutex.release()

                            else:
                                bullet_list_mutex.acquire()
                                bullet_list.append(self.bullet_sprite)
                                bullet_list_mutex.release()

                                bullet_list_mutex.acquire()
                                bullet_list.append(self.bullet_sprite_2)
                                bullet_list_mutex.release()

                        if shot_type[1] == '1':
                            for i in range(0, len(sprite_players_list)):
                                if int(sprite_players_list[i].address.split(':')[1]) == int(cur_data[0]):
                                    if sprite_players_list[i].flag_rocket:
                                        self.rocket_sprite = rocket.Rocket()
                                        self.rocket_sprite.change_x = -math.sin(math.radians(angle)) * 11
                                        self.rocket_sprite.change_y = math.cos(math.radians(angle)) * 11

                                        self.rocket_sprite.center_x = x
                                        self.rocket_sprite.center_y = y
                                        self.rocket_sprite.angle = angle

                                        if int(cur_data[0]) == int(user_socket):
                                            rocket_list_client_mutex.acquire()
                                            rocket_list_client.append(self.rocket_sprite)
                                            rocket_list_client_mutex.release()
                                        else:
                                            rocket_list_mutex.acquire()
                                            rocket_list.append(self.rocket_sprite)
                                            rocket_list_mutex.release()

                print()
            except socket.error:
                break


def main():
    with open('ip_port.txt', encoding='utf-8') as f:
        read_data = f.read()
    f.close()
    read_data = read_data.split(';')
    ip = read_data[0].split(':')[1]
    port = read_data[1].split(':')[1]
    print(ip, port)
    client = SpaceGameClient()
    if client.init():
        client.run()
    else:
        pass


if __name__ == '__main__':
    main()
