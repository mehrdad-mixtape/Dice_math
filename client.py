import sys
from socket import socket, AF_INET, SOCK_STREAM
from time import sleep

SERVER_ADDR: tuple = ('127.0.0.1', 9999)
# SERVER_ADDR_2: tuple = tuple(map(lambda arg: int(arg) if arg.isdigit() else arg, '2.tcp.ngrok.io:16699'.split(':')))
BUFFER: int = 4096

def _reconnect(broken_socket: socket) -> None:
    broken_socket.close()
    new_socket: socket = socket(family=AF_INET, type=SOCK_STREAM)
    connect_to_server(new_socket, SERVER_ADDR)

def send_msg(sender_socket: socket, msg: str) -> None:
    try:
        msg: bytes = msg.encode('utf-8')
        sender_socket.send(msg)
    except Exception as E:
        print(f"CLIENT: ERROR > sending problem: {E}")
        print(f"CLIENT: INFO > try to reconnect...")
        _reconnect(sender_socket)

def recv_msg(receiver_socket: socket) -> str:
    try:
        msg: str = receiver_socket.recv(BUFFER).decode('utf-8')
        return msg
    except Exception as E:
        print(f"CLIENT: ERROR > receiving problem: {E}")
        return 'false'

def cheater(player_socket: socket) -> str:
    # send 'start' to server, then server send to me challenge
    send_msg(player_socket, 'start')
    # if I solve 40 challenge server give me VICTORY_FLAG
    target: int = 20
    for _ in range(0, target):
        challenge: str = recv_msg(player_socket)
        answer: int = challenge.count('@')
        # sleep(0.01)
        send_msg(player_socket, str(answer))
        print(challenge)

    VICTORY_FLAG: str = recv_msg(player_socket)
    return VICTORY_FLAG # I beat the server!

def connection_handler(client_socket: socket) -> None:
    stop: bool = False
    while not stop:
        try:
            msg: str = recv_msg(client_socket)
            if msg == 'false':
                stop = True
            else:
                print(f"CLIENT: INFO > msg is\n{msg}")
                stop = True
        except Exception as E:
            print(f"CLIENT: ERROR > handling connection has {E}")
            client_socket.close()
            stop = True

def connect_to_server(client_socket: socket, addr: tuple, ttc: int=5) -> None:
    for time in range(ttc):
        try:
            client_socket.connect(addr)
            print(f"CLIENT: INFO > connect to server successfully")
            connection_handler(client_socket)
        except (OSError, Exception):
            print(f"CLIENT: WARNING > cannot connect to server after {time + 1}s")
            sleep(1)
        else:
            while True:
                msg: str = input('>>> ')
                if msg == '':
                    continue
                elif msg == 'exit':
                    send_msg(client_socket, msg)
                    connection_handler(client_socket)
                    client_socket.close()
                    sys.exit(f"CLIENT: INFO > disconnect from server successfully")
                elif msg == 'cheat':
                    print('>>> start')
                    print(cheater(client_socket))
                else:
                    send_msg(client_socket, msg)
                    connection_handler(client_socket)
    sys.exit(f"CLIENT: WARNING > timeout, Good bye!")

def main() -> None:
    with socket(family=AF_INET, type=SOCK_STREAM) as client_socket:
        connect_to_server(client_socket, SERVER_ADDR)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit('\nGood bye!')
