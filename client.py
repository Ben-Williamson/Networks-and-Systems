import sys
import socket
import json
import select

class Client:
    def __init__(self, username, serverAddress, serverPort):
        self.username = username
        self.serverPort = serverPort
        self.serverAddress = serverAddress
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(0)
        self.connected = False
        self.connecting = False

    def connect(self):
        if not self.connected and not self.connecting:
            try:
                self.socket.connect((self.serverAddress, self.serverPort))
                self.connected = True
                print(f"Connected to server at {self.server_address}")
            except BlockingIOError:
                self.connecting = True
        elif self.connecting:
            # Connection in progress, check if it's complete
            try:
                self.socket.getpeername()
                self.connected = True
                self.connecting = False
                print(f"Connected to server at {(self.serverAddress, self.serverPort)}")
            except BlockingIOError:
                pass  # Connection still in progress
            except Exception as e:
                print(f"Error checking connection status: {e}")

        self.__send_json(
            {
                "type": "config",
                "settings": {
                    "username": self.username
                }
             }
        )

    # def connect(self):
    #     if not client.connected:
    #         try:
    #             self.socket.connect((self.serverAddress, self.serverPort))
    #             self.connected = True
    #         except BlockingIOError:
    #             pass  # Connection in progress, not an error for non-blocking socket

    #     # self.__send_json(
    #     #     {
    #     #         "type": "config",
    #     #         "settings": {
    #     #             "username": self.username
    #     #         }
    #     #      }
    #     # )

    def __send_json(self, obj):
        if not self.connected:
            print("Not connected to the server.")
            return
        
        self.socket.sendall(json.dumps(obj).encode())

    def send(self, message):
        self.__send_json({"type": "message", "message": message})

    def receive_messages(self):
        if not self.connected:
            print("Not connected to the server.")
            return

        try:
            readable, _, _ = select.select([self.socket], [], [], 0.1)
            for sock in readable:
                data = sock.recv(1024)
                if not data:
                    print("Server closed the connection.")
                    self.connected = False
                else:
                    
                    decoded_data = data.decode('utf-8')
                    messages = decoded_data.split('\n')
                    print(messages)
                    for message in messages:
                        try:
                            message = json.loads(message)
                            if message['type'] == 'message':
                                print(message['message'])
                        except:
                            # invalid message format
                            pass
        except BlockingIOError:
            pass  # No data available, not an error for non-blocking socket


if __name__ == "__main__":
    username, address, port = sys.argv[1:]
    client = Client(username, address, int(port))

    while not client.connected:
        client.connect()

    while True:
        client.receive_messages()
        ready, _, _ = select.select([sys.stdin], [], [], 0.1)

        if ready:
            user_input = sys.stdin.readline().strip()
            if user_input.lower() == 'exit':
                print("Exiting...")
                break
            else:
                client.send(user_input)