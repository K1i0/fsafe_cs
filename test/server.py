from flask import Flask, request, jsonify

app = Flask(__name__)

board = [[' ' for _ in range(3)] for _ in range(3)]
current_player = 'X'


@app.route('/test_async', methods=['GET'])
async def test_async():
    return jsonify({'test': 1})


@app.route('/make_move', methods=['POST'])
def make_move():
    global current_player
    data = request.get_json()
    x = data['x']
    y = data['y']
    print(data)
    board[y][x] = current_player
    current_player = 'O' if current_player == 'X' else 'X'
    print(board)
    return jsonify({'board': board})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
