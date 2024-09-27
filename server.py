from colorama import Fore, Style, init
import threading
import socket
import time
import sys

PORT = 5050
HEADER = 1024
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = {}
clients_lock = threading.Lock()


def remove_client(username, conn):
    with clients_lock:
        if username in clients:
            del clients[username]
            conn.close()


def broadcast(message, sender=None, recipient=None):
    with clients_lock:
        if recipient:
            if recipient in clients:
                try:
                    clients[recipient].send(message)
                except Exception as e:
                    print(f"[ERROR] Could not send message to {recipient}: {e}")
                    remove_client(recipient, clients[recipient])
        else:
            for username, client in clients.items():
                if client != sender:
                    try:
                        client.send(message)
                    except Exception as e:
                        print(f"[ERROR] Could not send message to {username}: {e}")
                        remove_client(username, client)


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} Connected")

    try:
        username = conn.recv(HEADER).decode(FORMAT)
        with clients_lock:
            clients[username] = conn
        print(f"[NEW USER] {username} connected.")

        join_message = f"{Fore.GREEN}{username} has joined the chat.{Style.RESET_ALL}".encode(FORMAT)
        broadcast(join_message, conn)

        connected = True
        while connected:
            msg = conn.recv(HEADER).decode(FORMAT)
            if not msg:
                break

            if msg == DISCONNECT_MESSAGE:
                connected = False
                break

            if "@" in msg:
                mentioned_user = msg.split('@')[1].split()[0]
                if mentioned_user in clients:
                    private_msg = f"{Fore.MAGENTA}[PRIVATE] {msg}{Style.RESET_ALL}".encode(FORMAT)
                    broadcast(private_msg, conn, recipient=mentioned_user)
                    print(f"[PRIVATE] {msg}")
                else:
                    error_msg = f"{Fore.RED}User @{mentioned_user} not found.{Style.RESET_ALL}".encode(FORMAT)
                    conn.send(error_msg)
            else:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                formatted_msg = f"[{timestamp}] {msg}".encode(FORMAT)
                broadcast(formatted_msg, conn)
                print(f"[{timestamp}] {msg}")

                sys.stdout.write("Server: ")
                sys.stdout.flush()

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        remove_client(username, conn)
        leave_message = f"{Fore.RED}{username} has left the chat.{Style.RESET_ALL}".encode(FORMAT)
        broadcast(leave_message)
        print(f"[DISCONNECTED] {username} has left.")


def server_broadcast_input():
    while True:
        sys.stdout.write("Server: ")
        sys.stdout.flush()
        msg = input("")

        if msg:
            formatted_msg = f"{Fore.YELLOW}[SERVER]: {msg}{Style.RESET_ALL}".encode(FORMAT)
            broadcast(formatted_msg)


def start():
    init()

    print(f"[LISTENING] Server is listening on {SERVER}")
    server.listen()
    input_thread = threading.Thread(target=server_broadcast_input, daemon=True)
    input_thread.start()

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[Active Connections] {threading.active_count() - 1}")


print("[STARTING] Server is starting ...")
start()
