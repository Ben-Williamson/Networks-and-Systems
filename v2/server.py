from connection import NonBlockingSocket
import socket
from connection import ClientDisconnected
from message import Message
import time
import base64
import os

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
            self.send(
                Message(
                        f"Hello! Welcome to the server.",
                        type='unicast',
                        dest=client_socket.get_client_address()
                        )
                    )
            print(f"New connection {client_socket.get_client_address()}")
        except socket.error:
            pass

    def client_disconnect(self, client):
        self.connected_clients.remove(client)
        self.broadcast(
            Message(
                f'{client.get_username()} dissconnected.'
            )
        )

    def broadcast(self, data):
        for c in self.connected_clients:
            if data.get_origin() != c.get_client_address():
                try:
                    c.send(data)
                except ClientDisconnected:
                    self.client_disconnect(c)

    def unicast(self, message):
        if message.dest == "server":
            print(message.get_message())
            if message.get_message()['command'] == "connected_clients":
                self.unicast(
                    Message(
                        {'connected_clients': 
                        [{'name': client.get_username(), 'address': client.get_client_address()} for client in self.connected_clients]
                        },
                        dest=message.get_origin(),
                        datatype='config'
                        )
                )
            elif message.get_message()['command'] == "files":
                self.unicast(
                    Message(
                        {'files': 
                            [{"name": file} for file in os.listdir('downloads/')]
                        },
                        dest=message.get_origin(),
                        datatype='config'
                        )
                    )
            elif message.get_message()['command'] == "download":
                print('sending')
                with open('downloads/doc.pdf', 'rb') as f:
                    print('sending file')
                    buffer_size = 6000
                    data = f.read(buffer_size)
                    chunk_no = 0
                    while data:
                        # print("test")
                        # print(data, base64.b64encode(data).decode('utf-8'))
                        self.unicast(
                            Message(
                                {
                                    'filename': 'test',
                                    'chunk': base64.b64encode(data).decode('utf-8'),
                                    'chunk_no': chunk_no
                                },
                                datatype='file_chunk',
                                dest=message.get_origin()
                                )
                                )
                        # print(chunk_no)
                        chunk_no += 1
                        data=f.read(buffer_size)
                        time.sleep(0.09)
                print('done')
                self.unicast(
                    Message(
                        {"download": "test"},
                        dest=message.get_origin(),
                        datatype='config'
                    )
                )

        
        elif message.get_dest():
            for client in self.connected_clients:
                if list(client.get_client_address()) == list(message.get_dest()):
                    # print("sent to dest")
                    client.send(message)
                    return 0
        return 1

    def send(self, message):
        if message.get_type() == 'unicast':
            self.unicast(message)
        if message.get_type() == 'broadcast':
            self.broadcast(message)

    def route_data(self, data):
        if data.get_type() == 'broadcast':
            self.broadcast(data)
        elif data.get_type() == 'unicast':
            self.unicast(data)
        


    def listen(self):
        self.accept_new_connections()
        # Receive data from connected clients
        for client_socket in self.connected_clients:
            if client_socket != self.socket:
                try:
                    data = client_socket.receive()
                    if data:
                        print(data)
                        data.set_origin(client_socket.get_client_address())
                        self.route_data(data)
                except ClientDisconnected:
                    self.client_disconnect(client_socket)
                
                if client_socket.get_new_client_status():
                    self.send(
                        Message(f'{client_socket.get_username()} joined the server.'))
                    client_socket.set_new_client_status(False)

    def close(self):
        self.socket.close()
try:
    s = Server(5555)
    while True:
        s.listen()
        

except KeyboardInterrupt:
    print('cleaning up')
    s.close()