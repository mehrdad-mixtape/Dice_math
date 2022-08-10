import sys
from hashlib import sha1
from select import select
from time import time
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from dice_math import create_challenge, create_canvas, show_canvas, \
    check_answer, BANNER, QUIZ_DURATION, MAX_POINT_TO_GET_VICTORY, REWARD

HOST: tuple = ('127.0.0.1', 9999)
BUFFER: int = 2048
socket_list: list = []
players: list = []
player_answers: list = []
correct_answers: list = []
client_list: dict = {}

def _create_flag(player_id: str) -> str:
    key: str = 'qXTvjA}O1c[dNk_^ZnUs'
    return sha1(''.join((key, player_id)).encode('utf-8')).hexdigest()
    
def _check_victory(player_socket: socket, player_id: str, correct_answers: int, incorrect_answers: int, score: int) -> None:
    victory_msg: str = f"""
    Corrects = {correct_answers}
    InCorrects = {incorrect_answers}
    Score = {score}
    That is unbelievable! You could beat me, you should have muscle brain!
    Ok This is your reward:
    VICTORY-FLAG = {_create_flag(player_id)}
    ##### Server shutdown! #####"""

    try_again_msg: str = f"""
    Corrects = {correct_answers}
    InCorrects = {incorrect_answers}
    Score = {score}
    Type 'exit' to good bye
    Type 'start' to try again"""

    if score == MAX_POINT_TO_GET_VICTORY:
        send_msg(player_socket, victory_msg)
        sys.exit('\n##### You beat me! #####')
    else:
        send_msg(player_socket, try_again_msg)

def _dice_math(player_socket: socket, player_id: str) -> tuple:
    start_time: int = time()
    while time() < start_time + QUIZ_DURATION: # Main game loop.
        # Come up with the dice to display:
        top_left_dice_corners, dice_faces, sum_answer = create_challenge()
        correct_answers.append(sum_answer)
        # Draw the dice on the canvas:
        # Keys are (x, y) tuples of ints, values the character at that position on the canvas:
        canvas: dict = create_canvas(top_left_dice_corners, dice_faces)
        # Display the canvas on the screen:
        screen: str = show_canvas(canvas)
        
        send_msg(player_socket, screen + '\nsum?')
        response: str = recv_msg(player_socket)
        try:
            answer: int = int(response)
        except ValueError:
            send_msg(player_socket, "You can't deceive me, are you cheater?")
            break
        else:
            player_answers.append(answer)
            print(f"player_answers = {player_answers}")
            print(f"correct_answers = {correct_answers}")
            if len(player_answers) == MAX_POINT_TO_GET_VICTORY // REWARD:
                break
    _check_victory(player_socket, player_id, *check_answer(correct_answers, player_answers))

def _add_client(notify_socket: tuple) -> None:
    client_socket, client_address = notify_socket
    print(f"SERVER: INFO > client {client_address} append to server")
    socket_list.append(client_socket)
    client_list[client_socket] = client_address

def _remove_client(notify_socket: socket) -> None:
    try:
        notify_socket.close()
        print(f"SERVER: INFO > client {client_list[notify_socket]} remove from server")
        socket_list.remove(notify_socket)
        players.clear()
        del client_list[notify_socket]
    except (KeyError, IndexError):
        print(f"SERVER: WARNING > client does not exist to remove")

def send_msg(sender_socket: socket, msg: str) -> None:
    try:
        msg: bytes = msg.encode('utf-8')
        sender_socket.send(msg)
    except Exception as E:
        print(f"SERVER: ERROR > sending problem: {E}")
        _remove_client(sender_socket)

def recv_msg(receiver_socket: socket) -> str:
    try:
        msg: str = receiver_socket.recv(BUFFER).decode('utf-8')
        return msg
    except Exception as E:
        print(f"SERVER: ERROR > receiving problem: {E}")
        _remove_client(receiver_socket)

def connection_handler(client_socket: socket, player_id: str) -> None:
    stop: bool = False
    while not stop:
        try:
            msg: str = recv_msg(client_socket)
            if msg is None or len(msg) == 0:
                stop = True
            elif msg == 'exit':
                print(f"SERVER: INFO > connection close with {client_list[client_socket]}")
                send_msg(client_socket, 'goodbye')
                players.remove(player_id)
                _remove_client(client_socket)
                stop = True
            elif msg == 'start':
                print(f"SERVER: INFO > ##### math dice started! #####")
                _dice_math(client_socket, player_id)
                stop = True
            elif msg == 'help':
                send_msg(client_socket, BANNER)
                stop = True
            else:
                print(f"SERVER: INFO > msg from {client_list[client_socket]} is [{msg}]")
                send_msg(client_socket, 'Valid commands:\n1. start\n2. exit')
                stop = True
        except Exception as E:
            print(f"SERVER: ERROR > handling connection has {E}")
            _remove_client(client_socket)
            stop = True

def authorize_client(client_socket: socket) -> None:
    send_msg(client_socket, 'What is your id?\nShould be like this: ID-123456789')
    player_id: str = recv_msg(client_socket)
    try:
        if len(player_id) == 12 and player_id.startswith('ID-'):
            if player_id not in players: players.append(player_id)
            send_msg(client_socket, f"Welcome! player = {player_id}\n{BANNER}")
        else:
            send_msg(client_socket, f"Invalid! id = {player_id}\nYou kicked from server!")
            _remove_client(client_socket)
    except (TypeError, ValueError):
        authorize_client(client_socket)

def run_server() -> None:
    with socket(family=AF_INET, type=SOCK_STREAM) as server_socket:
        try:
            server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            server_socket.bind(HOST)
            server_socket.listen()
            socket_list.append(server_socket)
            print(f"SERVER: INFO > server is running! on {HOST}")
        except Exception as E:
            sys.exit(f"SERVER: ERROR > server has {E}")
        
        while True: # wait for clients
            try:
                print(f"SERVER: INFO > waiting for clients ...")
                read_sockets, _, except_sockets = select(socket_list, [], socket_list, 0.5)
                for read_socket in read_sockets:
                    if read_socket == server_socket:
                        new_client: tuple = server_socket.accept()
                        _add_client(new_client)
                        authorize_client(new_client[0])

                    else: # client_sockets
                        if len(socket_list) > 1: # there are more than 1 client in the list
                            connection_handler(read_socket, players[0]) # handle connection with client

                for except_socket in except_sockets:
                    print(f"SERVER: ERROR > socket {except_socket} has problem")
                    _remove_client(except_socket)

            except Exception as E:
                print(f"SERVER: CRITCAL > {E}")
                for dead_socket in socket_list:
                    _remove_client(dead_socket)
                sys.exit(f"SERVER: CRITCAL > server has problem!")

def main() -> None:
    run_server()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit('\nGood bye!')
