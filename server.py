import arcade

import interaction_manager
from game import *
import socket
from threading import Thread
from interaction_manager import InteractionManager

import schedule

BUFSIZE = 1024
ADDRESS = (SERVER_IP, SERVER_PORT)
SENDING_SPEED = 1/15

DEFAULT_COORD = ((1800, 800), (1800, 1800), (2800, 800), (2800, 1800))

#tcp_socket = None
#udp_socket = None

#if data[0] == 'g':
    #if data[1].find('1') == 0:
        #msg = '-x'
    #if data[1].find('1') == 2:
        #msg = '+x'
    #if data[1].find('1') == 4:
        #msg = '+y'
    #if data[1].find('1') == 6:
        #msg = '-y'

    #for player in players_list:
        #player.client_socket.sendall(f'g;{msg}'.encode())


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
                if data[0] == 'm':
                    msg = f'{self.__client_address[0]}:{self.__client_address[1]} {data[1]}'
                    for player in players_list:
                        player.client_socket.sendall(f'm;{msg}'.encode())
                if data[0] == 'g':
                    data = data[1].split(';')
                    if data[3].find('1') == 0:
                        msg = f'{data[0]};{data[1]};{float(data[2]) + 1}'
                    if data[3].find('1') == 2:
                        msg = f'{data[0]};{data[1]};{float(data[2]) - 1}'
                    if data[3].find('1') == 4:
                        coords = data[1].split(':')
                        x, y = coords[0], coords[1]
                        angle = float(data[2])
                        change_x = -math.sin(math.radians(angle)) * 2
                        change_x = round(change_x)
                        change_y = math.cos(math.radians(angle)) * 2
                        change_y = round(change_y)
                        x = float(x) + change_x
                        y = float(y) + change_y
                        msg = f'{data[0]};{x}:{y};{data[2]}'
                    if data[3].find('1') == 6:
                        msg = f'{data[0]};{data[1]};{float(data[2])}'
                for player in players_list:
                    player.get_tcp_sock().sendall(f'g;{msg}'.encode())
            except socket.error as e:
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

                # отправление начальных координат всем игрокам
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
        # self.__receiver = None
        self.__acceptor = None
        #self.__udp_socket = None

    def __del__(self):
        if self.__tcp_socket:
            self.__tcp_socket.close()
        # if self.__receiver:
        #     self.__receiver.join()
        if self.__acceptor:
            self.__acceptor.join()

    def init(self):
        self.__tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__tcp_socket.bind(ADDRESS)

        #self.__receiver = TCPReciv(self.__tcp_socket)
        #self.__receiver.start()

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


# class UDPRecive(Thread):
#     def __init__(self):
#         super().__init__()
#
#     def run(self):
#         while True:
#             data, address = udp_socket.recvfrom(BUFSIZE)
#             data = data.decode('utf-8')
#             data = data.split(';')
#             for player in players_list:
#                 if player.address == address:
#                     count = 0
#                     for key in player.client_input.keys():
#                         player.client_input[key] = int(data[count])
#                         count += 1
#                     print(f'{player.address[0]}:{player.address[1]} {player.client_input} {player.server_output}')
#                     break


# def UDPSend():
#     print('UDPSend')
#     data = ''
#     for player in players_list:
#         for key in player.client_input.keys():
#             player.client_input[key] = 0
#         data += player.address[0] + ';' + str(player.address[1]) + ';'
#         for value in player.server_output.values():
#             data += str(value) + ';'
#         data += ';'
#     data = data[:-2].encode()
#     for player in players_list:
#         udp_socket.sendto(data, player.address)

def main():
    server = SpaceGameServer()
    server.init()
    server.run()
    #udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #udp_socket.bind(ADDRESS)

    #game = Game()

    #udp_reciver = UDPRecive()
    #udp_reciver.start()

    #tcp_connector = TCPConnect()
    #tcp_connector.start()

    # schedule.every(1).seconds.do(UDPSend)
    # arcade.schedule(game.server_update, 1/60)
    # arcade.schedule(UDPSend, SENDING_SPEED)
    arcade.run()


if __name__ == '__main__':
    main()
