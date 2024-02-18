import uuid
import random
import re
import json

BOARD_SIZE = 3
SYMBOLS = ['x', 'o']


def validate_input(input_string):
    pattern = r'^\d+-\d+$'  # Шаблон число-число
    return True if re.match(pattern, input_string) else False


def extract_numbers(input_string):
    pattern = r'\d+'  # Шаблон для поиска чисел
    numbers = re.findall(pattern, input_string)
    return [int(num) for num in numbers]


class Board:
    def __init__(self):
        self.size = BOARD_SIZE
        self.board = [[' ' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    def print_board(self):
        print("-" * (4 * self.size - 1))
        for row in self.board:
            print(" | ".join(row))
            print("-" * (4 * self.size - 1))
        print('')

    def is_win(self):
        # Проверка строк и столбцов
        for i in range(self.size):
            # Проверка строк
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != ' ':
                return True
            # Проверка столбцов
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != ' ':
                return True

        # Проверка главной диагонали
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != ' ':
            return True

        # Проверка побочной диагонали
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != ' ':
            return True

        return False

    def is_draw(self):
        for i in range(0, self.size):
            for j in range(0, self.size):
                if self._is_cell_free(j, i):
                    return False
        return True

    def _is_cell_free(self, x, y) -> bool:
        return True if self.board[y][x] == ' ' else False

    def is_set_possible(self, x, y):
        if (0 <= x < self.size) and (0 <= y < self.size):
            if self._is_cell_free(x, y):
                return True
        return False

    def set_cell(self, x, y, s):
        if self.is_set_possible(x, y):
            self.board[y][x] = s


class Game:
    def __init__(self):
        self.game_uuid = uuid.uuid4()
        self.players = {}
        # Первый ход делает PlayerX
        self.current_player = 'x'
        self.board = Board()

    # Проверить очередность хода
    def check_turn(self, symbol, player_uuid):
        return True if self.players[symbol] == player_uuid else False

    def _validate(self, symbol, player_uuid, x, y):
        results = [
            self.check_turn(symbol, player_uuid),
            self.board.is_set_possible(x, y)
        ]
        return True if all(results) else False

    def join_game(self, player_uuid):
        if len(self.players) == 0:
            symbol = random.choice(['x', 'o'])
            self.players[symbol] = player_uuid
            return {"game_id": self.game_uuid, "sym": symbol}
        elif len(self.players) == 1:
            symbol = 'o' if 'x' in self.players else 'x'
            self.players[symbol] = player_uuid
            return {"game_id": self.game_uuid, "sym": symbol}
        else:
            print('Невозможно подключиться к игре. В игре участвует максимальное количество игроков')

    def make_move(self, symbol, player_uuid, x, y):
        if self._validate(symbol, player_uuid, x, y):
            self.board.set_cell(x, y, symbol)

    def run_game(self):
        k = 0
        while True:
            self.board.print_board()
            format_input = input("Игрок {}. Введите поле в формате y-x: ".format(self.current_player))
            field_coord = extract_numbers(format_input)

            conditions = [
                validate_input(format_input),
                False if len(field_coord) < 2 else self._validate(self.current_player, self.players[self.current_player], field_coord[1], field_coord[0])
            ]
            while not (conditions[0] and conditions[1]):
                if conditions[0]:
                    print("Некорректный формат введенных данных. Введите координаты поля в формате y-x")
                else:
                    print("Некорректные данные. Введите координаты поля в формате y-x (range = [0, 2]))")
                format_input = input("Игрок {}. Введите поле в формате y-x: ".format(self.current_player))
                field_coord = extract_numbers(format_input)
                conditions = [
                    validate_input(format_input),
                    False if len(field_coord) < 2 else self._validate(self.current_player, self.players[self.current_player], field_coord[1],
                                   field_coord[0])
                ]
            self.board.set_cell(field_coord[1], field_coord[0], self.current_player)
            if self.board.is_win():
                return
            elif self.board.is_draw():
                return
            k ^= 1
            self.current_player = SYMBOLS[k]


class Player:
    def __init__(self, game: Game):
        self.id = uuid.uuid4()
        self.data = game.join_game(self.id)

    def print_data(self):
        print('Id: {}, Session: {}, Sign: {}'.format(self.id, self.data["game_id"], self.data["sym"]))


def main() -> None:
    # board = Board()
    # board.print_board()
    # board.set_cell(0, 0, 'x')
    # board.set_cell(0, 1, '0')
    # board.set_cell(2, 1, 'x')
    # board.print_board()

    game = Game()
    player1 = Player(game)
    player1.print_data()
    player2 = Player(game)
    player2.print_data()

    game.run_game()


if __name__ == "__main__":
    main()
