import argparse
import json
import time
import threading
import numpy as np
from flask import Flask, jsonify, request

import make_request as mq

app = Flask(__name__)

# Переменные для реализации игровой логики
board = np.full((3, 3), " ")
tokens = ["x", "o"]
current_player = tokens[0]
winner = None
is_game_start = False
is_draw = False

# <uid>: (<token>, <client_address>)
players = {}

# Реализация отказоустойчивости
# url: is_available
reserve_servers = {}


@app.route('/ping', methods=['GET'])
def ping():
    return 'OK'


def ping_server(url):
    stat, response = mq.make_request('GET', 'http://' + url + '/ping')
    if stat:
        print(f"Ответ от {url + '/ping'}: {response.text}")
        return True
    return False


def init_interconnect(servers):
    global reserve_servers
    while True:
        for server in servers:
            ping_server(server)
        time.sleep(5)
        # for i in range(10):
        # if ping_server(server):
        #     reserve_servers[server] = True
        #     time.sleep(1)
        #     break
        # else:
        #     reserve_servers[server] = False
    print(reserve_servers)


@app.route("/sync", methods=['POST'])
def sync_data():
    data = request.json()
    print(data)


def broadcast_game_progress():
    for url, is_available in reserve_servers:
        stat, response = mq.make_request('POST', url + '/sync', jsonify(board=board, winner=winner))


@app.route("/", methods=['GET'])
def index():
    return "Welcome to Tic Tac Toe Server!"


# Возвращает текущий статус игры (текущий токен и состояние доски)
@app.route("/status", methods=['GET'])
def status():
    return jsonify(player=current_player, is_game_start=is_game_start, board=board.tolist())


@app.route("/join", methods=['POST'])
def join():
    global players
    global is_game_start

    if not request.is_json:
        return jsonify({"error": "Data must be sent as JSON"}), 400
    request_data = request.json

    uid = request_data.get("uid")

    if uid is None:
        return jsonify({"error": "There is not enough data. The request must contain uid"}), 400

    print("Client with uid {} connected!".format(uid))

    if len(players) == 0:
        players[uid] = 'x'
    elif len(players) == 1:
        players[uid] = 'o'
        is_game_start = True
    else:
        return jsonify({"error": "The maximum number of players has already been joined"}), 400

    return jsonify(player=current_player, token=players[uid], board=board.tolist()), 200


@app.route("/move", methods=["GET", "POST"])
def move():
    global current_player
    global winner
    global players

    # Проверка - определен ли уже победитель
    if request.method == "GET":
        if check_winner():
            game_result = jsonify(player=current_player, board=board.tolist(), winner=winner, draw=is_draw)
            init_game()
            return game_result
        return jsonify(player=current_player, board=board.tolist(), winner=None, draw=False)

    if not request.is_json:
        return jsonify({"error": "Data must be sent as JSON"}), 400

    request_data = request.json
    # get() returns uid or None
    uid = request_data.get("uid")
    row = request_data.get("row")
    col = request_data.get("col")

    if uid is None:
        return jsonify({"error": "Invalid request, please specify uid"}), 400
    if uid not in players:
        return jsonify({"error": "Cannot make move. Not on the list of players"}), 400

    # Validation
    if row is None or col is None:
        return jsonify({"error": "Invalid move, please specify row and column"}), 400
    if row < 0 or row > 2 or col < 0 or col > 2:
        return jsonify({"error": "Invalid move, row and column must be between 0 and 2"}), 400
    if board[row][col] != " ":
        return jsonify({"error": "Invalid move, cell already occupied"}), 400

    board[row][col] = current_player

    if check_winner():
        # init_game()
        return jsonify(board=board.tolist(), winner=winner, draw=(winner is None))

    # 0 ^ 1 == 1, 1 ^ 1 == 0
    current_player = tokens[tokens.index(current_player) ^ 1]
    return jsonify(board=board.tolist(), winner=None, draw=False)


def check_winner():
    global winner
    global is_draw
    for token in tokens:
        # Check rows and columns
        for i in range(3):
            # По идее, можно заменить на all(board[i] == token) or all(board[:, i] == token)
            if all(t == token for t in board[i]) or all(t == token for t in board[:, i]):
                winner = token
                return True
        # Check diagonals
        if np.all(np.diag(board) == token) or np.all(np.diag(np.fliplr(board)) == token):
            winner = token
            return True
    # Check for draw
    if " " not in board:
        winner = None
        is_draw = True
        return True
    return False


def init_game():
    global players
    global board
    global winner
    global current_player
    global is_game_start

    board[:, :] = " "
    current_player = tokens[0]
    winner = None
    players.clear()
    is_game_start = False


def main():
    global reserve_servers
    # Создаем парсер аргументов
    parser = argparse.ArgumentParser(description="Command line arguments parser")
    # Добавляем аргументы
    parser.add_argument('--config', type=str, default='config/c1.json',
                        help='Server config file')
    # Разбираем аргументы командной строки
    args = parser.parse_args()
    with open(args.config, 'r') as config_file:
        data = json.load(config_file)
        host = data["host"]
        port = data["port"]
        servers = data["reserve"]

    ping_thread = threading.Thread(target=init_interconnect, args=(servers, ))
    ping_thread.start()

    app.run(host=host, port=port, debug=True)
    # init_interconnect(servers)


if __name__ == '__main__':
    main()
