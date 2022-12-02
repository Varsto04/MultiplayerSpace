class InteractionManager:
    @staticmethod
    def new_connection_message(ip, port):
        return f'm;{ip}:{port}'.encode()

    @staticmethod
    def coords_message(ip, port, coords):
        return f'c;{ip}:{port};{coords[0]}:{coords[1]}#'.encode()

    @staticmethod
    def coords_message2(address, coords):
        return f'c;{address};{coords[0]}:{coords[1]}'.encode()

    @staticmethod
    def parse_coords_message(message):
        message = message.split(';')
        address = message[1]
        coords_str = message[2].split(':')
        coords = [int(coords_str[0]), int(coords_str[1])]
        return address, coords

    @staticmethod
    def move_message(move_dict: dict):
        message = ''
        for values in move_dict.values():
            message += str(values) + ':'
        # data += str(values) + ';'
        #
        # data = data[:-1].encode('utf-8')
        # data = bytes(data)
        message = message[:-1]
        message += '#'
        #return message.encode()
        return message
