import select
from helpers import NonBlockingSocket, Client, ClientDisconnected, Message
import base64
import os
from time import sleep
import logging
import sys

class Server:
    def __init__(self):
        self.socket = NonBlockingSocket()
        self.connectedClients = []
        logging.basicConfig(filename="server.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

        logging.info("Server ready to listen.")

    def listen(self, address):
        self.socket.listen(address)
        logging.info(f'Server listening on {address}')

    def acceptNewClients(self):
        newClient = self.socket.accept()
        if newClient:
            client = Client(newClient)
            self.connectedClients.append(
                client
            )
            print(f"Client connected: {client.peerName()}")
            logging.info(f"Client connected: {client.peerName()}")
            client.sendMessage(
                Message(
                    "You are connected to the server, welcome!"
                )
            )
        
    def getClientAddresses(self):
        return [[client.getConfig('username'), client.getConfig('address')] for client in self.connectedClients]

    def handleMessage(self, message):
        logging.info(f"Message from {message.origin}: {message.body}")
        client = self.selectClient(message.origin)
        if message.type == 'command':
            if message.body['command'] == 'files':
                client.setConfig('files', os.listdir('downloads'), callback='table')
            if message.body['command'] == 'clients':
                clientAddresses = self.getClientAddresses()
                client.setConfig('clients', clientAddresses, callback='table')
            if message.body['command'] == 'download':
                self.sendFile(message.body['argument'], message.origin)
            if message.body['command'] == 'ready':
                self.broadcast(Message(
                    f'{client.getConfig("username")} joined the server.'
                ))
                clientAddresses = self.getClientAddresses()
                for client in self.connectedClients:
                    client.setConfig('clients', clientAddresses)

    def routeMessage(self, message):
        if message.destination == 'server':
            return self.handleMessage(message)
        if message.destination == 'broadcast':
            logging.info("Message broadcasted.")
            return self.broadcast(message)
        logging.info("Message forwarded to destination.")
        return self.unicast(message)

    def receiveMessages(self):
        clientsWithMessages, _, _ = select.select(self.connectedClients, [], [], 0.1)

        for client in clientsWithMessages:
            try:
                message = client.receive()
                if message:
                    print(f'{client.getConfig('username')}: {message}')
                    self.routeMessage(message)
                    
            except ClientDisconnected:
                self.broadcast(Message(
                    f'{client.getConfig("username")} left the server.'
                ))
                logging.info(f'{client.getConfig("username")} left the server.')
                self.connectedClients.remove(client)

    def broadcast(self, message):
        for client in self.connectedClients:
            client.sendMessage(message)

    def unicast(self, message):
        self.selectClient(message.destination).sendMessage(message)

    def selectClient(self, address):
        for client in self.connectedClients:
            if address == client.getConfig('address'):
                return client
            
    def sendFile(self, file, address):
        self.unicast(
            Message(
                'Transfering file.', destination=address
            )
        )
        logging.info(f"Started file transmission to {address}")
        f = open(f'downloads/{file}', 'rb')
        file_chunk = f.read(2000)
        while file_chunk:
            self.unicast(
                Message(
                    {"file_chunk": base64.b64encode(file_chunk).decode(), 'file_name': file}, type='file_chunk', destination=address, origin='server'
                )
            )
            file_chunk = f.read(2000)
            sleep(0.01)
        f.close()
        self.unicast(
            Message(
                'File transmission complete.', destination=address
            )
        )
        logging.info(f"File transmitted to {address}")


if __name__ == "__main__":
    try:
        port = int(sys.argv[1])
    except:
        print("useage: python server.py [port]")
        exit()

    server = Server()
    server.listen(('localhost', 5555))

    while True:
        server.acceptNewClients()
        server.receiveMessages()

