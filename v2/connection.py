import socket
import select
from message import Message
import json

class ClientDisconnected(Exception):
    def __init__(self, message='Client disconnected.'):
        self.message = message
        super().__init__(self.message)

class ConnectedClient:
    def __init__(self, client_socket, client_address):
        self.socket = NonBlockingSocket(client_socket)
        self.username = None
        self.new_client_status = False

    def get_new_client_status(self):
        return self.new_client_status
    
    def set_new_client_status(self, value):
        self.new_client_status = value

    def get_username(self):
        return self.username
    
    def get_client_address(self):
        return self.socket.get_client_address()

    def receive(self):
        try:
            message = self.socket.receive()
            if message:
                message.set_origin(self.get_client_address())
                print(message.get_datatype())
                if message.get_type() == 'config':
                    if 'username' in message.get_message():
                        self.username = message.get_message()['username']
                        self.set_new_client_status(True)
                    return None
                if message.get_datatype() == 'file_chunk':
                    print(message.get_message())
                    return None
                message.set_username(self.get_username())
                return message
            return None
        except socket.error:
            raise ClientDisconnected()

    def send(self, data):
        try:
            self.socket.send(data)
            return True
        except:
            raise ClientDisconnected()

class NonBlockingSocket:
    def __init__(self, custom_socket=None):
        self.buffer_size = 8192
        if not custom_socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        else:
            self.socket = custom_socket
        self.socket.setblocking(0)  # Set to non-blocking mode

    def get_client_address(self):
        return self.socket.getpeername()

    def connect(self, address):
        try:
            self.socket.connect(address)
            print("Connection established!")
            return True
        except socket.error as e:
            # Check if the error is due to the connection still in progress
            if e.errno == socket.errno.EINPROGRESS or e.errno == socket.errno.EALREADY:
                return False
            else:
                # socket connected
                return True

    def bind_and_listen(self, address):
        self.socket.bind(address)
        self.socket.listen(5)

    def accept(self):
        client_socket, client_address = self.socket.accept()
        return ConnectedClient(client_socket, client_address)

    def send(self, data):
        data = data.json()
        data = data.ljust(self.buffer_size, '\0')
        self.socket.send(data.encode('utf-8'))

    def receive(self):
        ready_to_read, _, _ = select.select([self.socket], [], [], 0.1)
        if self.socket in ready_to_read:
            data = self.socket.recv(self.buffer_size).decode()
            data = data.rstrip('\0')
            if data:
                message = Message()
                try:
                    message.load_json(json.loads(data))
                    return message
                except Exception as e:
                    print(data)
                    print("ERRRORRRR", e)
                    exit()

                    # exit()
            # return pickle.loads(data) if data else None
        return None

    def close(self):
        self.socket.close()


