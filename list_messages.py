import socket

SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
PORT = 5050
HEADER = 1024


def connect():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        print(f"Connected to server at {ADDR}")
        return client
    except Exception as e:
        print(f"[ERROR] can not connect to server: {e}")
        return None


def start():
    connection = connect()
    if not connection:
        return

    try:
        while True:
            try:
                msg = connection.recv(HEADER).decode(FORMAT)
                if msg:
                    print(f"{msg}")
                else:
                    print("[SERVER] Connection closing by the server.")
                    break

                if msg == DISCONNECT_MESSAGE:
                    print("Disconnected from server.")
                    break
            except Exception as e:
                print(f"[ERROR] erorr not receiving message: {e}")
                break
    except KeyboardInterrupt:
        print("\n[USER] Disconnected by user.")
    finally:
        connection.close()
        print("Connection closed.")


start()
