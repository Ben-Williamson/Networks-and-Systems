from connection import NonBlockingSocket
from time import sleep
from message import Message
import select, sys

# Example of using the NonBlockingSocket class in a client
client_socket = NonBlockingSocket()

# Perform client operations using the client_socket




if __name__ == "__main__":
    username, address, port = sys.argv[1:]
    # client = Client(username, address, int(port))

    while not client_socket.connect((address, int(port))):
        pass

    # client_socket.send(
    #     Message(
    #         type='config',
    #         message={
    #             'username': username
    #         },
    #         origin=type(client_socket)
    #     )
    # )

    while True:
        data = client_socket.receive()
        if data:
            print(data.get_origin())
            print(data)
            # sys.stdout.write("test: ")

        ready, _, _ = select.select([sys.stdin], [], [], 0.1)

        if ready:
            user_input = sys.stdin.readline().strip()
            print(">>> ", end='', flush=True)
            if user_input.lower() == 'exit':
                print("Exiting...")
                client_socket.close()
                break
            else:
                client_socket.send(
                    Message(
                        user_input,
                        username
                        )
                    )
            