import socket
import json
import select
import base64
import os

class SocketDisconnected(Exception):
    pass

class ClientDisconnected(Exception):
    pass

class NonBlockingSocket:
    def __init__(self, customSocket=None):
        self.messageLength = 4000

        if customSocket:
            self.socket = customSocket
        else:
            self.socket = socket.socket()
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.setblocking(0)

    def fileno(self):
        return self.socket.fileno()

    def listen(self, address):
        self.socket.bind(address)
        self.socket.listen(5)

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

    def accept(self):
        try:
            clientSocket, clientAddress = self.socket.accept()
            return NonBlockingSocket(customSocket=clientSocket)
        except:
            return None
        
    def receive(self):
        data = self.socket.recv(self.messageLength)
        if data:
            data = data.rstrip(b'\0')
            return data
        else:
            # The socket has disconnected
            raise SocketDisconnected

    def send(self, data):
        data = data.ljust(self.messageLength, b'\0')
        return self.socket.send(data)
    
    def peerName(self):
        return self.socket.getpeername()
    
    def sockName(self):
        return self.socket.getsockname()

class Client:
    def __init__(self, customSocket):
        self.socket = customSocket
        self.config = {}
        self.callbacks = {'table': self.table}
        self.destination = 'broadcast'
        self.type = 'text'

    @classmethod
    def connectClient(self, hostname, port, username):
        clientSocket = NonBlockingSocket()
        while not clientSocket.connect((hostname, port)):
            pass
        client = Client(clientSocket)
        client.setConfig(
            'username', username
        )
        client.setConfig(
            'address', clientSocket.sockName()
        )
        client.handleCommand("ready")
        return client
    
    def peerName(self):
        return self.socket.peerName()
    
    def sockName(self):
        return self.socket.sockName()
    
    def fileno(self):
        return self.socket.fileno()
    
    def receive(self):
        try:
            message = Message.deserialize(
                self.socket.receive()
            )
            if message.type == 'config':
                return self.handleConfigMessage(message)
            if message.type == 'file_chunk':
                os.makedirs(f'{self.getConfig('username')}/', exist_ok=True)
                f = open(f'{self.getConfig('username')}/{message.body['file_name']}', 'ab')
                f.write(base64.b64decode(message.body['file_chunk']))
                f.close()
            else:
                return message
        except SocketDisconnected:
            raise ClientDisconnected
    
    def convertToUsername(self, origin):
        try:
            for client in self.getConfig('clients'):
                if client[1] == origin:
                    return client[0]
        except:
            # Fallback to IP address
            return origin

    def send(self, text):
        message = Message(
            text, destination=self.destination, origin=self.sockName(), type=self.type
        )
        self.socket.send(message.serialize())

    def sendMessage(self, message):
        self.socket.send(message.serialize())

    def handleConfigMessage(self, message):
        self.config[message.body['key']] = message.body['value']
        if message.body['callback']:
            message.body = self.callbacks[message.body['callback']](message.body['key'])
            return message

    def setConfig(self, key, value, callback=None):
        self.config[key] = value
        self.type = 'config'
        self.send(
                {"key": key, "value": value, "callback": callback}
        )

    def table(self, key):
        tableRows = []
        tableRows.append(key)
        count = 1
        for item in self.getConfig(key):
            tableRows.append(f'{count}. {item}')
            count += 1
        rowLength = max([len(str(row)) for row in tableRows]) + 2

        outputString = ''
        outputString += f'+{"-"*rowLength}+\n'
        for row in tableRows:
            outputString += f'| {row}{" " * (rowLength-len(str(row))-1)}|\n'
        outputString += f'+{"-"*rowLength}+\n'
        return outputString
    
    def getConfig(self, key=None):
        if key == None:
            return self.config
        if key in self.config:
            return self.config[key]
        return None

    def handleCommand(self, command):
        command = command.strip("\\")
        commandSplit = command.split(" ")

        if len(commandSplit) > 1:
            command = commandSplit[0]
            argument = commandSplit[1]
        else:
            command = commandSplit[0]
            argument = ""

        if command == 'broadcast':
            self.destination = 'broadcast'
        elif command == 'unicast':
            self.destination = self.getConfig('clients')[int(argument)-1][1]
        elif command== 'exit':
            exit()
        else:
            if command == 'download':
                argument = self.getConfig('files')[int(argument)-1]
            prevMode = self.destination
            prevType = self.type
            self.destination = 'server'
            self.type = 'command'
            self.send({"command": command, "argument": argument})
            self.destination = prevMode
            self.type = prevType

class Message:
    def __init__(self, body, type='text', destination='broadcast', origin=""):
        self.body = body
        self.type = type
        self.destination = destination
        self.origin = origin

    def getOrigin(self):
        return self.origin
    
    def setOrigin(self, origin):
        self.origin = origin

    @classmethod
    def deserialize(self, serializedMessage):
        message = json.loads(serializedMessage.decode())
        return Message(message['body'], type=message['type'], destination=message['destination'], origin=message['origin'])

    def serialize(self):
        return json.dumps(
                {
                    "body": self.body,
                    "type": self.type,
                    "destination": self.destination,
                    "origin": self.origin
                }
            ).encode()

    def __str__(self):
        return str(self.body)
    
def selector(items):
    ready, _, _ = select.select(items, [], [], 1)
    return ready