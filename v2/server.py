from connection import NonBlockingSocket
import socket
from connection import ClientDisconnected

class Server:
    def __init__(self, port) -> None:
        self.port = port
        self.socket = NonBlockingSocket()
        self.socket.bind_and_listen(('', port))
        self.connected_clients = []

    def accept_new_connections(self):
        try:
            client_socket = self.socket.accept()
            self.connected_clients.append((client_socket))
            self.unicast(client_socket, f"Hello! {client_socket.username}")
            print(f"New connection {client_socket}")
        except socket.error as e:
            # Handle non-blocking error (no new connection)
            pass

    def broadcast(self, data):
        for c in self.connected_clients:
            if data.get_origin() != c.get_username():
                if not c.send(data, type='forward'):
                    self.connected_clients.remove(c)
                    print(f'{c.username} disconnected.')

    def unicast(self, client, data):
        client.send(data)

    def listen(self):
        self.accept_new_connections()
        # Receive data from connected clients
        for client_socket in self.connected_clients:
            if client_socket != self.socket:
                try:
                    data = client_socket.receive()
                    if data:
                        print(data)
                        self.broadcast(data)
                except ClientDisconnected:
                    self.connected_clients.remove(client_socket)
                
                    # Process the received data as needed

    def close(self):
        self.socket.close()
try:
    s = Server(5555)
    while True:
        s.listen()
        

except KeyboardInterrupt:
    print('cleaning up')
    s.close()