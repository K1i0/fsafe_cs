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
is_init_finished = False
reconnect_count = 3


@app.route('/ping', methods=['GET'])
def ping():
    return 'OK'


def init_interconnect(urls):
    global reserve_servers
    global is_init_finished
    for server in urls:
        for _ in range(reconnect_count):
            if mq.ping(server):
                reserve_servers[server] = True
                break
            else:
                reserve_servers[server] = False
            time.sleep(1)
    print(reserve_servers)
    is_init_finished = True
    return


@app.route("/sync", methods=['POST'])
def sync():
    global board
    global current_player
    global winner
    global is_game_start
    global is_draw
    global players

    if not request.is_json:
        return jsonify({"error": "Data must be sent as JSON"}), 400

    request_data = request.json
    # get() returns uid or None
    board = request_data.get("board")
    board = np.array(board)
    current_player = request_data.get("current_player")
    winner = request_data.get("winner")
    is_game_start = request_data.get("is_game_start")
    is_draw = request_data.get("is_draw")
    players = request_data.get("players")

    print('board: ', board)
    print('current_player', current_player)
    print('winner', winner)
    print('is_game_start', is_game_start)
    print('is_draw', is_draw)
    print('players', players)

    return 'OK', 200


def broadcast_game_progress():
    game_status = {
        "board": board.tolist(),
        "current_player": current_player,
        "winner": winner,
        "is_game_start": is_game_start,
        "is_draw": is_draw,
        "players": players
    }

    for url, is_available in reserve_servers.items():
        if is_available:
            mq.make_request('POST', 'http://' + url + '/sync', game_status)


@app.route("/", methods=['GET'])
def index():
    return "Welcome to Tic Tac Toe Server!"


# Возвращает текущий статус игры (текущий токен и состояние доски)
@app.route("/status", methods=['GET'])
def status():
    broadcast_game_progress()
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

    broadcast_game_progress()
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
            broadcast_game_progress()
            return game_result
        broadcast_game_progress()
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

    broadcast_game_progress()
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
        servers_url = data["reserve"]

    # init_interconnect(servers_url)

    ping_thread = threading.Thread(target=init_interconnect, args=(servers_url,))
    ping_thread.start()

    app.run(host=host, port=port, debug=True)
    # init_interconnect(servers)


if __name__ == '__main__':
    main()