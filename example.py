import socket

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 5556))
    server_socket.listen(5)

    print("Server listening on port 5555...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")

            # Handle client communication in a separate function or thread
            handle_client(client_socket, client_address)

    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server_socket.close()

def handle_client(client_socket, client_address):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                print(f"Connection with {client_address} closed.")
                break
            # Handle received data as needed
            print(f"Received data from {client_address}: {data.decode('utf-8')}")

    except ConnectionResetError:
        print(f"Connection with {client_address} reset by the client.")
    finally:
        client_socket.close()


if __name__ == "__main__":
    start_server()