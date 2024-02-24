import uuid
import requests
import time

SERVER_URL = 'http://127.0.0.1:8080/'


def print_board(board):
    print(" ", "0   1   2")
    for i in range(3):
        print(str(i), " | ".join(board[i]))
        print("-" * 13)
    print('')


def make_move():
    row, col = map(int, input("Enter row and col (0, 1, or 2): ").split())
    return row, col

k = 0
def main():
    print("Welcome to Tic Tac Toe!")
    print("Waiting for opponent to connect...\n")

    uid = str(uuid.uuid4())
    # Вывод первоначального состояния доски
    response = requests.post(SERVER_URL + "join", json={"uid": uid})
    data = response.json()

    if response.status_code == 400:
        print(response.json()["error"])
    else:
        player = data["player"]
        board = data["board"]
        token = data["token"]
        # print_board(board)

    while True:
        if player == token:
            global k
            k = k ^ 1

            print_board(board)
            while True:
                row, col = make_move()
                move = {"uid": uid, "row": row, "col": col}
                response = requests.post(SERVER_URL + "move", json=move)
                if response.status_code != 400:
                    break
                else:
                    print(response.json()["error"])
            data = response.json()
            board = data["board"]
            print_board(board)
            if data["winner"]:
                print("You win!")
                break
            elif data["draw"]:
                print("It's a draw!")
                break
            response = requests.get(SERVER_URL + "move", json=move)
            player = response.json()["player"]
        else:
            response = requests.get(SERVER_URL + "move")
            data = response.json()
            board = data["board"]
            player = response.json()["player"]
            if data["winner"]:
                print_board(board)
                print("Opponent wins!")
                break
            elif data["draw"]:
                print_board(board)
                print("It's a draw!")
                break
            if k:
                k = k ^ 1
                print("Waiting for opponent's move (O)...")
            time.sleep(1)


if __name__ == '__main__':
    main()