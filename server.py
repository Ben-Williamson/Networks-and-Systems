import sys
import socket
import select
import json
import pickle

class Message:
    def __init__(self, type, sender, payload):
        self.type = type
        self.payload = payload
        self.sender = sender
    


class Client:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.username = self.address
        print(f'Client connected from {self.address[0]} on port {self.address[1]}.')

    def set_username(self, username):
        self.username = username
        return self.username
    
    def get_username(self):
        return self.username

    def fileno(self):
        return self.socket.fileno()

    def listen(self):
        data = self.socket.recv(1024)
        if not data:
            self.socket.close()
            return False
        
        data = data.decode()
        print(data)
        data = json.loads(data)
        if data['type'] == 'config':
            if 'username' in data['settings']:
                self.set_username(data['settings']['username'])
            self.send(f'Hello {self.get_username()}! Welcome to the server.')
            return 1
        if data['type'] == 'message':
            return data['message']
        
    def send(self, message):
        self.socket.sendall(json.dumps({
            'type': 'message',
            'message': message
        }).encode() + b'\n')

class Server:
    def __init__(self, port) -> None:
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = [self.socket]

    def start(self):
        self.socket.bind(('', self.port))
        self.socket.listen(5)
        print('server ready')

    def broadcast(self, message, exclude=[]):
        for client in self.clients:
            if client not in [self.socket, *exclude]:
                client.send(message)

    def listen(self):
        r,w,e=select.select(self.clients,[],self.clients)
        
        for client in r:
            if client == self.socket:
                client_socket, client_address = self.socket.accept()
                self.clients.append(Client(client_socket, client_address))
            else:
                data = client.listen()
                if not data:
                    print(f"Connection with {client.username} closed.")
                    self.clients.remove(client)
                else:
                    print(f"Received data from {client.username}: {data}")
                    self.broadcast(data, exclude=[client])

if __name__ == '__main__':
    try:
        port = sys.argv[1]
    except:
        print('No port provided, stopping.')
        exit()
    try:
        port = int(port)
    except:
        print('Provided port is not an integer, stopping.')
        exit()

    server = Server(port)
    server.start()
    
    while True:
        server.listen()

    try:
        while True:
            server.listen()
    except Exception as error:
        server.socket.close()
        print(error)