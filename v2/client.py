from connection import NonBlockingSocket
import time
from message import Message
import select, sys
import base64


class Client:
    def __init__(self, username, address, port):
        self.username = username
        self.address = address
        self.port = port
        self.socket = NonBlockingSocket()
        self.config = {'last_updates': {}}
        self.requests = []
        self.callbacks = {
            'connected_clients': lambda a: print(a)
        }

    def connect(self):
        start_time = time.time()
        timeout = time.time() - start_time > 10
        while not (self.socket.connect((self.address, self.port)) or timeout):
            pass
        if timeout:
            return 1
        
        self.send(
            Message(
                type='config',
                message={
                    'username': username
                }
            )
        )
        return 0
    
    def send(self, message):
        self.socket.send(message)

    def check_for_messages(self):
        message = self.socket.receive()

        if not message:
            return
        
        datatype = message.get_datatype()

        match datatype:
            case 'text':
                print(message)
            case 'config':
                print('got config object')
                print(data.get_message())
                message_body = data.get_message()
                for key in message_body:
                    self.set_config(key, message_body[key])
                    config['last_updates'][key] = time.time()
                    # waiting_for = [x for x in waiting_for if x['command'] != key]

    def set_config(self, key, value):
        self.config[key] = value
        self.config['last_updates'][key] = time.time()
        self.requests = [request for request in self.requests if request != key]
        self.callbacks[key](value)

    def get_input(self):
        ready, _, _ = select.select([sys.stdin], [], [], 0.1)

        if ready:
            user_input = sys.stdin.readline().strip()
            
            self.send(
                Message(
                    user_input
                )
            )


# Example of using the NonBlockingSocket class in a client
client_socket = NonBlockingSocket()

# Perform client operations using the client_socket

def print_connected_clients(config, to_print):
    table_rows = [f'{to_print}:']
    for client_id in range(len(config[to_print])):
        client = config[to_print][client_id]
        table_rows.append(f'{client_id}. {client['name']} at {client['name']}')
    table_cols = max([len(row) for row in table_rows])+5

    print(f'+{'-'*table_cols}+')
    for row in table_rows:
        print(f'| {row}{' '*(table_cols-len(row)-1)}|')
    print(f'+{'-'*table_cols}+')

def handle_unicast(config, user_input):
    try:
        client_id = user_input.split(' ')[1]
    except:
        print('You must provide a client number.')
        return 1
    try:
        client_id = int(client_id)
    except:
        print('Client id must be an integer.')
        return
    try:
        client = config['connected_clients'][client_id]
        return client
    except:
        print('Client id not in connected clients.  Try \\getclients')


if __name__ == '__main__':
    username, address, port = sys.argv[1:]

    client = Client(username, address, int(port))
    client.connect()

    while True:
        client.check_for_messages()
        client.get_input()

if __name__ == "__main__123":
    username, address, port = sys.argv[1:]
    # client = Client(username, address, int(port))

    while not client_socket.connect((address, int(port))):
        pass

    client_socket.send(
        Message(
            type='config',
            message={
                'username': username
            }
        )
    )

    message_mode = 'broadcast'
    message_target = ''
    callbacks = {
        'connected_clients': print_connected_clients,
        'files': print_connected_clients,
        'download': lambda a, b: print(files)
        }
    config = {
        'connected_clients': [],
        'files' : [],
        'last_updates': {
            'connected_clients': 0,
            'files': 0,
            'download': 0
        }
    }
    files = {

    }
    waiting_for = []
    while True:
        data = client_socket.receive()
        if data:
            if data.get_datatype() == 'text':
                print(data)
                pass
            elif data.get_datatype() == 'file_chunk':
                if data.get_message()['filename'] in files:
                    files[
                        data.get_message()['filename']
                    ] += base64.b64decode(data.get_message()['chunk'])
                else:
                    files[
                        data.get_message()['filename']
                    ] = base64.b64decode(data.get_message()['chunk'])
            elif data.get_datatype() == 'config':
                print('got config object')
                print(data.get_message())
                for key in data.get_message():
                    config[key] = data.get_message()[key]
                    config['last_updates'][key] = time.time()
                    waiting_for = [x for x in waiting_for if x['command'] != key]
                    print(waiting_for)
                    callbacks[key](config, key)

        ready, _, _ = select.select([sys.stdin], [], [], 0.1)

        if len(waiting_for):
            print('Waiting for server data...')
            for config_type in waiting_for:
                client_socket.send(
                    Message(
                        config_type,
                        type='unicast',
                        dest='server',
                        datatype='config'
                    )
                )

        elif ready:
            user_input = sys.stdin.readline().strip()
            # print(">>> ", end='', flush=True)
            if user_input.lower() == 'exit':
                print("Exiting...")
                client_socket.close()
                break
            elif user_input.lower().startswith('\\getclients'):
                if time.time() - config['last_updates']['connected_clients'] > 10:
                    waiting_for.append({'command': 'connected_clients', 'args': ''})
            elif user_input.lower().startswith("\\unicast"):
                message_target = handle_unicast(config, user_input)['address']
                message_mode = 'unicast'
            elif user_input.lower().startswith('\\broadcast'):
                message_target = None
                message_mode = 'broadcast'
            elif user_input.lower().startswith('\\getfiles'):
                if time.time() - config['last_updates']['files'] > 10:
                    waiting_for.append({'command': 'files', 'args': ''})
            elif user_input.lower().startswith('\\download'):
                waiting_for.append({'command': 'download', 'args': 1})
            else:
                client_socket.send(
                    Message(
                        user_input,
                        type=message_mode,
                        dest=message_target
                        )
                        
                    )
            