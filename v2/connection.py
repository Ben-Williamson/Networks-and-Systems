import socket
import select
import pickle
from message import Message

class ClientDisconnected(Exception):
    def __init__(self, message='Client disconnected.'):
        self.message = message
        super().__init__(self.message)

class ConnectedClient:
    def __init__(self, client_socket, username):
        self.socket = NonBlockingSocket(client_socket)
        self.username = username

    def get_username(self):
        return self.username

    def receive(self):
        try:
            message = self.socket.receive()
            if message:
                if message.get_type() == 'config':
                    if 'username' in message.get_message():
                        self.username = message.get_message()['username']
                    return None
                return message
            return None
        except socket.error:
            raise ClientDisconnected()

    def send(self, message, type='message'):
        try:
            self.socket.send(
                Message(
                    message, 'server', type=type
                )
            )
            return True
        except:
            return False

class NonBlockingSocket:
    def __init__(self, custom_socket=None):
        if not custom_socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        else:
            self.socket = custom_socket
        self.socket.setblocking(0)  # Set to non-blocking mode

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
        self.socket.send(pickle.dumps(data))

    def receive(self, buffer_size=1024):
        ready_to_read, _, _ = select.select([self.socket], [], [], 0.1)
        if self.socket in ready_to_read:
            data = self.socket.recv(buffer_size)
            return pickle.loads(data) if data else None
        return None

    def close(self):
        self.socket.close()


