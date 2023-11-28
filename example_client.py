import socket

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 5556)

    try:
        client_socket.connect(server_address)
        print(f"Connected to {server_address}")

        # Send data to the server
        while True:
            message = input(">>> ")
            client_socket.sendall(message.encode('utf-8'))

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    start_client()