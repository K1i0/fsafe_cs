import requests

SERVER_URL = 'http://127.0.0.1:5000'


def make_move():
    data = {'x': 1, 'y': 2}
    response = requests.post(f'{SERVER_URL}/make_move', json=data)
    print(response.json()['board'])


if __name__ == '__main__':
    make_move()
