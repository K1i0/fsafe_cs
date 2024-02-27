import uuid
import time
import sys


import make_request as mq

SERVER_URL = 'http://127.0.0.1:8080/'
user_id = str(uuid.uuid4())


def print_board(board):
    print(" ", "0   1   2")
    for i in range(3):
        print(str(i), " | ".join(board[i]))
        print("-" * 13)
    print('')


def connect():
    status, response = mq.make_request('POST', SERVER_URL + "join", data={"uid": user_id})

    if status:
        data = response.json()
        player = data["player"]
        board = data["board"]
        token = data["token"]
    else:
        return None, None, None

    return player, board, token


def make_move():
    global user_id

    while True:
        row, col = map(int, input("Enter row and col (0, 1, or 2): ").split())
        move = {"uid": user_id, "row": row, "col": col}
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
            animated_loading('Waiting for opponent\'s move...')
            time.sleep(.5)
    else:
        sys.exit()


k = 0


def main():
    print("Welcome to Tic Tac Toe!")

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
