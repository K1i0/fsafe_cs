import uuid
import json

class Board:
    def __init__(self, size):
        self.size = size
        self.board = [[' ' for _ in range(size)] for _ in range(size)]

    def print_board(self):
        print("-" * (4 * self.size - 1))
        for row in self.board:
            print(" | ".join(row))
            print("-" * (4 * self.size - 1))
        print('')

    def is_set_possible(self, x, y):
        if 0 <= x < self.size:
            if 0 <= y < self.size:
                return True
        return False

    def set_cell(self, x, y, s):
        if self.is_set_possible(x, y):
            self.board[y][x] = s

class Game:
    def __init__(self):
        self.game_uuid = uuid.uuid4()
        self.players = []
        self.current_player = None

    def join_game(self, player_uuid):
        if len(self.players) < 2:
            self.players.append(uuid)
            symbol = 'x' if len(self.players) == 1 else 'o'
            data = {"gid": self.game_uuid, "sym": symbol}
            return data
        else:
            print('Невозможно подключиться к игре. В игре участвует максимальное количество игроков')


class Player:
    def __init__(self, game: Game):
        self.id = uuid.uuid4()
        self.session = game.join_game(self.id)["gid"]

    def print_data(self):
        print('Id: {}, Session: {}'.format(self.id, self.session))

def main():
    size = int(input("Введите размер игрового поля: "))
    board = Board(size)
    board.print_board()
    board.set_cell(0, 0, 'x')
    board.set_cell(0, 1, '0')
    board.set_cell(2, 1, 'x')
    board.print_board()

    game = Game()
    player1 = Player(game)
    player1.print_data()

# Если файл скрипта запускается напрямую, то переменная __name__ равна __main__
# Если же скрипт импортирован как модуль в другой скрипт, значение __name__ будет установлено равным имени модуля
# Блок if __name__ == "__main__": позволяет изолировать код, который должен выполняться только при запуске скрипта напрямую из командной строки
if __name__ == "__main__":
    main()