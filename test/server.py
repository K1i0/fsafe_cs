import argparse
import json

import numpy as np
from flask import Flask, jsonify, request

app = Flask(__name__)

board = np.full((3, 3), " ")
tokens = ["x", "o"]
current_player = tokens[0]
winner = None


@app.route("/", methods=['GET'])
def index():
    return "Welcome to Tic Tac Toe Server!"


# Возвращает текущий статус игры (текущий токен и состояние доски)
@app.route("/status", methods=['GET'])
def status():
    global current_player
    return jsonify(player=current_player, board=board.tolist())


def check_winner():
    global winner
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
        return True
    return False


if __name__ == '__main__':
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
        reserve = data["reserve"]

    app.run(host=host, port=port, debug=True)
