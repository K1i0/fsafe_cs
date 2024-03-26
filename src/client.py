import uuid
import time
import sys
import argparse
import json
import threading

import make_request as mq

SERVER_IP = ''
SERVER_URL = ''
user_id = str(uuid.uuid4())

servers_ip = []
servers_stat = {}


def update_servers_status():
    global servers_stat

    # Обновление статусов (up / down) серверов
    while True:
        for server in servers_ip:
            servers_stat[server] = mq.ping(server)
        time.sleep(1)


def change_server():
    global SERVER_IP, SERVER_URL

    # Если сервак нужно сменить, значит он еще оффлайн
    servers_stat[SERVER_IP] = False

    for ip_address in servers_ip:
        if servers_stat[ip_address]:
            SERVER_IP = ip_address
            SERVER_URL = 'http://' + SERVER_IP + '/'
            return True

    # Неn серверов для замены
    print(f"Невозможно подключиться к серверам игры: {servers_stat}")
    return False


def print_board(board):
    print(" ", "0   1   2")
    for i in range(3):
        print(str(i), " | ".join(board[i]))
        print("-" * 13)
    print('')


def connect():
    status, response = mq.make_request('POST', SERVER_URL + "join", data={"uid": user_id})

    if response == 503:
        if change_server():
            return connect()
        else:
            sys.exit()
    
    if response.json().get("code"):
            print(response.json()["code"])
            if change_server():
                return connect()
            else:
                sys.exit()

    if status:
        data = response.json()
        return data["player"], data["board"], data["token"]
    else:
        sys.exit()


def make_move():
    global user_id

    while True:
        row, col = map(int, input("Enter row and col (0, 1, or 2): ").split())
        move = {"uid": user_id, "row": row, "col": col}
        status, response = mq.make_request('POST', SERVER_URL + "move", data=move)

        if status:
            return response
        elif response == 503:
            if not change_server():
                sys.exit()
            status, response = mq.make_request('POST', SERVER_URL + "move", data=move)
            if status:
                return response


def animated_loading(phrase):
    chars = "/—\\|"
    for char in chars:
        sys.stdout.write('\r' + phrase + char)
        time.sleep(.1)
        sys.stdout.flush()


def wait_server(stage, token=None):
    if stage == 'start':
        while True:
            status, response = mq.make_request('GET', SERVER_URL + "status")
            if status:
                if response.json()["is_game_start"]:
                    print()
                    return
            animated_loading('Waiting for opponent to connect... ')
            time.sleep(.5)
    elif stage == 'player':
        while True:
            status, response = mq.make_request('GET', SERVER_URL + "move")

            if not status and response == 503:
                if not change_server():
                    sys.exit()
                status, response = mq.make_request('GET', SERVER_URL + "move")

            try:
                data = response.json()
                board = data["board"]
                player = response.json()["player"]
                if player == token:
                    print()
                    return token, board
                if data["winner"]:
                    print_board(board)
                    print("Opponent wins!")
                    # break
                    sys.exit()
                elif data["draw"]:
                    print_board(board)
                    print("It's a draw!")
                    # break
                    sys.exit()
            except:
                continue
            
            animated_loading('Waiting for opponent\'s move...')
            time.sleep(.5)
    else:
        sys.exit()


k = 0


def main():
    global SERVER_IP
    global SERVER_URL
    global servers_ip

    parser = argparse.ArgumentParser(description="Command line arguments parser")
    parser.add_argument('--config', type=str, default='config/cc.json',
                        help='Client config file (contains server\'s ip)')
    parser.add_argument('--server', type=str, default='127.0.0.1:8080',
                        help='Default server\'s address to connect')
    args = parser.parse_args()
    
    SERVER_IP = args.server
    SERVER_URL = 'http://' + SERVER_IP + '/'

    with open(args.config, 'r') as config_file:
        data = json.load(config_file)
        servers_ip = data["servers"]

    ping_thread = threading.Thread(target=update_servers_status)
    ping_thread.start()
    time.sleep(1)

    player, board, token = connect()
    if any(var is None for var in (player, board, token)):
        return

    wait_server('start')

    while True:
        if player == token:
            print_board(board)
            response = make_move()
            data = response.json()
            board = data["board"]
            print_board(board)
            if data["winner"]:
                print("You win!")
                break
            elif data["draw"]:
                print("It's a draw!")
                break

            status, response = mq.make_request('GET', SERVER_URL + "move")
            player = response.json()["player"]
        else:
            player, board = wait_server('player', token)


if __name__ == '__main__':
    main()
