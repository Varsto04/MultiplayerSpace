import arcade
from game import *
import socket
from threading import Thread
from interaction_manager import InteractionManager
import schedule


BUFSIZE = 1024
SENDING_SPEED = 1/15

with open('ip_port.txt', encoding='utf-8') as f:
    read_data = f.read()
f.close()
read_data = read_data.split(';')
ip = read_data[0].split(':')[1]
port = read_data[1].split(':')[1]
# SERVER_IP = ip
# SERVER_PORT = port
ADDRESS = (ip, int(port))

#ADDRESS = (SERVER_IP, SERVER_PORT)

DEFAULT_COORD = ((1800, 800), (1800, 1800), (2800, 800), (2800, 1800))

rating_table = {}


class TCPReciv(Thread):
    def __init__(self, client_socket):
        super().__init__()
        self.__client_socket = client_socket
        self.__client_address = client_socket.getpeername()

    def run(self):
        while True:
            try:
                data = self.__client_socket.recv(BUFSIZE).decode('utf-8')
                data = data.split(';', 1)
                print(data)
                if data[0] == 'm':
                    msg = f'{self.__client_address[0]}:{self.__client_address[1]} {data[1]}'
                    for player in players_list:
                        player.client_socket.sendall(f'm;{msg}'.encode())
                if data[0] == 'g':
                    data = data[1].split(';')
                    move_input = data[3].split(':')
                    if move_input[0] == '1':
                        data[2] = float(data[2]) + 0.6
                    elif move_input[1] == '1':
                        data[2] = float(data[2]) - 0.6
                    if move_input[2] == '1':
                        coords = data[1].split(':')
                        x, y = coords[0], coords[1]
                        angle = float(data[2])

                        change_x = -math.sin(math.radians(angle)) * 2
                        change_x = round(change_x)
                        change_y = math.cos(math.radians(angle)) * 2
                        change_y = round(change_y)

                        if float(x) < 25:
                            x = float(x)
                        elif float(x) > 4975:
                            x = float(x)
                        else:
                            x = float(x) + change_x

                        if float(y) < 25:
                            y = float(y)
                        elif float(y) > 2975:
                            y = float(y)
                        else:
                            y = float(y) + change_y

                        data[1] = str(x) + ':' + str(y)
                    if move_input[3] == '1':
                        msg = f'{data[0]};{data[1]};{float(data[2])}'
                    msg = f'{data[0]};{data[1]};{float(data[2])}'
                    print()
                    for player in players_list:
                        player.get_tcp_sock().sendall(f'g;{msg}#'.encode())
                if data[0] == 'z':
                    data = data[1].split(';')
                    msg = f'{data[0]};{data[1]};{float(data[2])};{data[3]}'
                    for player in players_list:
                        player.get_tcp_sock().sendall(f'z;{msg}#'.encode())
            except socket.error as e:
                print(e)
                break
        #remove_player(self.client_socket)


class TCPConnect(Thread):
    def __init__(self, tcp_sock):
        super().__init__()
        self.__sock = tcp_sock

    def run(self):
        while True:
            client_socket, client_address = self.__sock.accept()
            if len(players_list) <= 4:
                print(f'{client_address[0]}:{client_address[1]} connect to the server')

                players_list_size = len(players_list)

                coords = DEFAULT_COORD[players_list_size]
                player = ServerPlayer(client_address, client_socket, coords)
                players_list_mutex.acquire()
                players_list.append(player)
                players_list_mutex.release()

                players_list_size = len(players_list)

                # отправление начальных координат всем клиентам
                for i in range(0, players_list_size):
                    cur_player = players_list[i]
                    cur_player.get_tcp_sock().sendall(InteractionManager.coords_message(
                        client_address[0], client_address[1], coords))
                    if i != players_list_size - 1:
                        player.get_tcp_sock().sendall(InteractionManager.coords_message(
                            cur_player.get_address()[0],
                            cur_player.get_address()[1],
                            cur_player.get_coords()
                        ))

                print(players_list)
            else:
                print('Server full')


class SpaceGameServer:
    def __init__(self):
        self.__tcp_socket = None
        self.__acceptor = None

    def __del__(self):
        if self.__tcp_socket:
            self.__tcp_socket.close()
        if self.__acceptor:
            self.__acceptor.join()

    def init(self):
        self.__tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__tcp_socket.bind(ADDRESS)

    def run(self):
        self.__tcp_socket.listen()
        print(f'Server runnung on {SERVER_IP}:{SERVER_PORT}...')

        self.__acceptor = TCPConnect(self.__tcp_socket)
        self.__acceptor.start()


def remove_player(client_socket):
    client_address = client_socket.getpeername()
    for player in players_list:
        if player.address == client_address:
            players_list.remove(player)
            break
    client_socket.close()
    for player in players_list:
        player.client_socket.sendall(f'd;{client_address[0]};{client_address[1]}'.encode())
    print(f'{client_address[0]}:{client_address[1]} disconect.')
    #if len(players_list) == 0:
        #arcade.unschedule(game.server_update)


class ServerPlayer:
    def __init__(self, address, client_socket, coord=(50, 50)):
        self.__client_address = address
        self.__client_socket = client_socket
        self.__coords = [coord[0], coord[1]]
        self.__tcp_reciver = TCPReciv(self.__client_socket)
        self.__tcp_reciver.start()

    def get_coords(self):
        return self.__coords

    def get_address(self):
        return self.__client_address

    def get_tcp_sock(self):
        return self.__client_socket


def main():
    server = SpaceGameServer()
    server.init()
    server.run()
    arcade.run()


if __name__ == '__main__':
    main()
