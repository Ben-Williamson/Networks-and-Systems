from helpers import Client, selector
import sys
from io import TextIOWrapper


if __name__ == "__main__":
    try:
        username, hostname, port = sys.argv[1:]
        port = int(port)
    except:
        print("usage: python client.py [username] [hostname] [port]")
        exit()
    
    client = Client.connectClient(hostname, int(port), username)
    while True:
        for item in selector([client, sys.stdin]):
            if isinstance(item, Client):
                message = client.receive()
                if message and message.getOrigin() != list(client.sockName()):
                    origin = client.convertToUsername(message.getOrigin())
                    if origin:
                        print(f'{origin}: {message}')
                    else:
                        print(message)
            elif isinstance(item, TextIOWrapper):
                text = sys.stdin.readline().strip()

                if text.startswith("\\"):
                    client.handleCommand(text)
                else:
                    client.type = 'text'
                    client.send(text)