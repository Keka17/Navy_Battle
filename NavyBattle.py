import random
from abc import ABC, abstractmethod
from colorama import Fore, Back, Style


class GameRules:
    def message(self):
        print('Приветствую, моряк 👋! Правила игры "Морской бой" просты:'
              '\n 1) Базовый флот состоит из 4 однопалубных катеров, '
              '\n 2 двухпалубных эсминцев и 1 трехпалубного крейсера;'
              '\n 2) Задача - первым "утопить" корабли противника;'
              '\n 3) Каждая позиция пробивается не более одного раза;'
              '\n 4) Корабли размещаются на расстоянии не менее одной клетки друг от друга.'
              '\n Удачного боя 🤞!')


class GameField:
    def __init__(self):
        self.grid = [[' '] + [str(i) for i in range(1, 7)]]
        self.grid += [[str(i)] + ['◯'] * 6 for i in range(1, 7)]

    def print_field(self):
        for rows in self.grid:
            print(' | '.join(rows))
        print()

    def reset_field(self):
        self.grid = [[' '] + [str(i) for i in range(1, 7)]]
        self.grid += [[str(i)] + ['◯'] * 6 for i in range(1, 7)]


# Класс ограничений на размещение кораблей
class Restrictions:
    def __init__(self):
        self.game_field = GameField()

    def neighbours(self, point1, point2):
        dx = abs(point1[0] - point2[0])
        dy = abs(point1[1] - point2[1])
        return dx <= 1 and dy <= 1

    # Проверяет возможность размещения двух-
    # и трехпалубных кораблей
    def can_place_ships(self, cells, size, amount):
        available_cells = cells.copy()

        for _ in range(amount):
            ship_placed = False

            for i in range(len(available_cells)):
                # Проверка вертикального размещения
                if i + size - 1 < len(available_cells):
                    if all(available_cells[k] == (available_cells[k - 1][0] + 1, available_cells[k - 1][1])
                           for k in range(i + 1, i + size)):
                        ship_placed = True
                        available_cells = available_cells[:i] + available_cells[i + size:]
                        break

                # Проверка горизонтального размещения
                if i + size - 1 < len(available_cells):
                    if all(available_cells[k] == (available_cells[k - 1][0], available_cells[k - 1][1] + 1)
                           for k in range(i + 1, i + size)):
                        ship_placed = True
                        available_cells = available_cells[:i] + available_cells[i + size:]
                        break
                if not ship_placed:
                    continue
            if not ship_placed:
                return False
        return True


# Класс нахождения доступных для размещения
# клеток: ◯ и не имеют соседей
class FindFreeCells:
    def __init__(self):
        self.available_cells = []
        self.restriction = Restrictions()

    def find_free_cells(self, field):

        empty_cells = [(i, j) for i in range(1, 7)
                       for j in range(1, 7) if field[i][j] == '◯']
        filled_cells = [(i, j) for i in range(1, 7)
                        for j in range(1, 7) if field[i][j] == '■']

        self.available_cells = [free_cell for free_cell in empty_cells
                                if not any(self.restriction.neighbours(free_cell, filled_coords)
                                for filled_coords in filled_cells)]

        return self.available_cells


# Полиморфизм: абстрактный класс, определяющий методы,
# общие для игрока и компьютера (коориднаты + направление)
class ChoiceInterface(ABC):
    @abstractmethod
    def coordinates(self):
        pass

    @abstractmethod
    def choose_direction(self):
        pass

    @abstractmethod
    def get_coordinates(self):
        pass

    def get_direction(self):
        pass


class UserChoice(ChoiceInterface):
    def __init__(self):
        self.x = None
        self.y = None
        self.direction = None

    def coordinates(self):
        while True:
            try:
                self.y = int(input('Введите X-координату: '))
                self.x = int(input('Введите Y-координату: '))
                if 1 <= self.x <= 6 and 1 <= self.y <= 6:
                    return self.x, self.y
                print('Выход за пределы поля. Попробуйте снова.')
            except ValueError:
                print('Некорректный ввод. Попробуйте снова.')

    def choose_direction(self):
        while True:
            self.direction = input('Выберите направление (left/right/up/down): ')
            if self.direction in ['left', 'right', 'up', 'down']:
                return self.direction
            else:
                print('Некорректный ввод. Попробуйте снова.')

    def get_coordinates(self):
        return self.x, self.y

    def get_direction(self):
        return self.direction


class RandomChoice(ChoiceInterface):
    def __init__(self):
        self.x = None
        self.y = None
        self.direction = None

    def coordinates(self):
        self.x = random.randint(1, 6)
        self.y = random.randint(1, 6)
        return self.x, self.y

    def choose_direction(self):
        self.direction = random.choice(['left', 'right', 'up', 'down'])
        return self.direction

    def get_coordinates(self):
        return self.x, self.y

    def get_direction(self):
        return self.direction


# Класс размещения кораблями
class Ships:
    def __init__(self, choice: ChoiceInterface):
        self.game_field = GameField()
        self.conditions = Restrictions()
        self.free_cells = FindFreeCells()
        self.coords = []
        self.cells = []
        self.choice = choice

    def reset_field(self):
        self.game_field.reset_field()
        self.coords = []

    def place_ships(self, size, amount):
        placed_ships = 0

        while placed_ships < amount:
            x, y = self.choice.coordinates()

            if size == 1:

                for old_coord in self.coords:
                    if self.conditions.neighbours((x, y), old_coord):
                        print('Соседний корабль! Попробуйте снова.')
                        break
                else:  # Если все ок, то установливаем корабль
                    if self.game_field.grid[x][y] == '◯':
                        self.game_field.grid[x][y] = '■'
                        self.coords.append((x, y))
                        placed_ships += 1
                        self.game_field.print_field()
                    else:
                        print('Позиция занята. Попробуйте снова.')

            else:
                direction = self.choice.choose_direction()

                if direction in ['left', 'right']:
                    dy = -1 if direction == 'left' else 1
                    if (all(1 <= y + dy * i <= 6 for i in range(size))
                            and all(self.game_field.grid[x][y + dy * i] == '◯'
                                    for i in range(size))):
                        if not any(self.conditions.neighbours((x, y + dy * i), old_coord)
                                   for i in range(size) for old_coord in self.coords):

                            for i in range(size):
                                self.game_field.grid[x][y + dy * i] = '■'
                                self.coords.append((x, y + dy * i))
                            placed_ships += 1
                            self.game_field.print_field()
                        else:
                            print('Невозможно разместить. Попробуйте снова.')
                    else:
                        print('Невозможно разместить. Попробуйте снова.')

                if direction in ['up', 'down']:
                    dx = -1 if direction == 'up' else 1
                    if (all(1 <= x + dx * i <= 6 for i in range(size))
                            and all(self.game_field.grid[x + dx * i][y] == '◯'
                                    for i in range(size))):
                        if not any(self.conditions.neighbours((x + dx * i, y), old_coord)
                                   for i in range(size) for old_coord in self.coords):

                            for i in range(size):
                                self.game_field.grid[x + dx * i][y] = '■'
                                self.coords.append((x + dx * i, y))
                            placed_ships += 1
                            self.game_field.print_field()
                        else:
                            print('Невозможно разместить. Попробуйте снова.')
                    else:
                        print('Невозможно разместить. Попробуйте снова.')

            self.cells = self.free_cells.find_free_cells(self.game_field.grid)


# Не каждый раз возвращал заполненное поле,
# использовался для генерации полей в RandomField
class ComputerShips(Ships):
    def __init__(self):
        # Вызов конструктора (__init__ метод) родительского класса (Ships)
        # из дочернего класса (ComputerShips)
        super().__init__(RandomChoice())
        self.restrictions = Restrictions()
        self.game_field = GameField()

    def computer_placing(self):

        while True:
            self.place_ships(1, 4)

            if self.restrictions.can_place_ships(self.cells, 2, 2):
                self.place_ships(2, 2)
                if self.restrictions.can_place_ships(self.cells, 3, 1):
                    self.place_ships(3, 1)
                    self.game_field.print_field()
                    print(self.game_field.grid)
                    break
                else:
                    pass
            else:
                pass


class RandomField:
    def __init__(self):
        self.bombarded_dots = []
        self.fields = [[[' ', '1', '2', '3', '4', '5', '6'], ['1', '■', '■', '■', '◯', '◯', '◯'],
                        ['2', '◯', '◯', '◯', '◯', '◯', '■'], ['3', '◯', '■', '◯', '■', '◯', '◯'],
                        ['4', '◯', '■', '◯', '◯', '◯', '■'], ['5', '◯', '◯', '◯', '◯', '◯', '◯'],
                       ['6', '■', '■', '◯', '◯', '■', '◯']],

                       [[' ', '1', '2', '3', '4', '5', '6'], ['1', '■', '◯', '◯', '■', '■', '◯'],
                        ['2', '◯', '◯', '◯', '◯', '◯', '◯'], ['3', '■', '◯', '■', '◯', '◯', '◯'],
                        ['4', '■', '◯', '◯', '◯', '◯', '■'], ['5', '◯', '◯', '◯', '◯', '◯', '◯'],
                        ['6', '■', '◯', '■', '■', '■', '◯']],

                       [[' ', '1', '2', '3', '4', '5', '6'], ['1', '◯', '◯', '◯', '◯', '◯', '◯'],
                        ['2', '■', '◯', '■', '■', '◯', '■'], ['3', '◯', '◯', '◯', '◯', '◯', '◯'],
                        ['4', '◯', '◯', '■', '◯', '■', '◯'], ['5', '■', '◯', '■', '◯', '◯', '◯'],
                        ['6', '■', '◯', '■', '◯', '◯', '■']],

                       [[' ', '1', '2', '3', '4', '5', '6'], ['1', '◯', '■', '◯', '◯', '■', '◯'],
                        ['2', '◯', '■', '◯', '◯', '◯', '◯'], ['3', '◯', '◯', '◯', '■', '■', '■'],
                        ['4', '■', '■', '◯', '◯', '◯', '◯'], ['5', '◯', '◯', '◯', '◯', '◯', '■'],
                        ['6', '◯', '■', '◯', '■', '◯', '◯']],

                       [[' ', '1', '2', '3', '4', '5', '6'], ['1', '■', '■', '◯', '■', '■', '■'],
                        ['2', '◯', '◯', '◯', '◯', '◯', '◯'], ['3', '◯', '◯', '■', '◯', '◯', '◯'],
                        ['4', '■', '◯', '◯', '◯', '■', '◯'], ['5', '◯', '◯', '◯', '◯', '◯', '◯'],
                        ['6', '■', '■', '◯', '■', '◯', '◯']],

                       [[' ', '1', '2', '3', '4', '5', '6'], ['1', '■', '■', '■', '◯', '■', '■'],
                        ['2', '◯', '◯', '◯', '◯', '◯', '◯'], ['3', '◯', '■', '◯', '■', '◯', '◯'],
                        ['4', '◯', '◯', '◯', '■', '◯', '◯'], ['5', '◯', '◯', '◯', '◯', '◯', '■'],
                        ['6', '■', '◯', '◯', '■', '◯', '◯']],

                       [[' ', '1', '2', '3', '4', '5', '6'], ['1', '■', '◯', '■', '◯', '■', '■'],
                        ['2', '■', '◯', '■', '◯', '◯', '◯'], ['3', '■', '◯', '◯', '◯', '◯', '◯'],
                        ['4', '◯', '◯', '◯', '■', '◯', '◯'], ['5', '■', '◯', '◯', '◯', '◯', '■'],
                        ['6', '◯', '◯', '◯', '■', '◯', '◯']]

                       ]

    def get_random_field(self):
        return random.choice(self.fields)

    # Используется в классе Game
    def set_random_field(self, x, y, symbol):
        self.fields[x][y] = symbol


# Поле заполняется юзером
class User:
    def __init__(self):
        self.game_field = GameField()
        self.ships = Ships(UserChoice())
        self.restrictions = Restrictions()
        self.cells = FindFreeCells()
        self.rules = GameRules()
        self.bombarded_dots = []

    def get_user_field(self):
        return self.game_field.grid

    # Используется в классе Game
    def set_user_field(self, x, y, symbol):
        self.game_field.grid[x][y] = symbol

    def placing_ships(self):
        self.rules.message()
        self.game_field.print_field()

        while True:
            try:
                print('Однопалубные катера')
                self.ships.place_ships(1, 4)

                if not self.restrictions.can_place_ships(self.ships.cells, 2, 2):
                    print('Невозможно разместить. Попробуйте снова.')
                    self.ships.reset_field()
                    continue

                print('Двухпалубные эсминцы')
                self.ships.place_ships(2, 2)

                if not self.restrictions.can_place_ships(self.ships.cells, 3, 1):
                    print('Невозможно разместить. Попробуйте снова.')
                    self.ships.reset_field()
                    continue

                print('Трехпалубный крейсер')
                self.ships.place_ships(3, 1)
                self.game_field.grid = self.ships.game_field.grid
                break
            except Exception as e:
                print(f'Ошибка: {e}')
                self.ships.reset_field()


class Game:
    def __init__(self):
        self.computer = RandomField()
        self.computer_field = self.computer.get_random_field()

        self.user = User()
        self.empty_field = self.user.get_user_field()
        self.user.placing_ships()
        self.user_field = self.user.get_user_field()

    def print_fields(self, field1, field2):
        for i in range(len(field1)):
            print(' | '.join('{:1s}'.format(x) for x in field1[i]) + '    '
                  + ' | '.join('{:1s}'.format(x) for x in field2[i]))

    def battle(self):
        print('Компьютер ходит первым. '
              '\nНа экране будет показано изменение вашего поля и подбитые точки на поле противника. '
              '\nX - попадание, Т - промах ')
        computer_dots = 11
        user_dots = 11

        while True:

            while True:
                x = random.randint(1, 6)
                y = random.randint(1, 6)

                if (x, y) in self.user.bombarded_dots:
                    continue

                if self.user_field[x][y] == '■':
                    self.user.set_user_field(x, y, '𝐗')
                    self.user.bombarded_dots.append((x, y))
                    computer_dots -= 1

                elif self.user_field[x][y] == '◯':
                    self.user.set_user_field(x, y, '𝐓')
                    self.user.bombarded_dots.append((x, y))
                break

            while True:
                try:
                    y = int(input('Введите X-координату: '))
                    x = int(input('Введите Y-координату: '))
                    if x not in range(1, 7) or y not in range(1, 7):
                        print('Выход за пределы поля. Попробуйте снова.')
                        continue
                    if (x, y) in self.computer.bombarded_dots:
                        print('Позиция уже подбита!')
                        continue
                except ValueError:
                    print('Некорректный ввод. Попробуйте снова.')
                    continue

                if self.computer_field[x][y] == '■':
                    self.computer.set_random_field(x, y, '𝐗')
                    self.empty_field[x][y] = Fore.RED + '𝐗' + Style.RESET_ALL
                    self.print_fields(self.user_field, self.empty_field)
                    self.computer.bombarded_dots.append((x, y))
                    user_dots -= 1
                    print('Очки игрока: ', 11 - user_dots)

                elif self.computer_field[x][y] == '◯':
                    self.computer.set_random_field(x, y, '𝐓')
                    self.empty_field[x][y] = Fore.BLUE + '𝐓' + Style.RESET_ALL
                    self.print_fields(self.user_field, self.empty_field)
                    self.computer.bombarded_dots.append((x, y))
                break

            if user_dots == 0 and computer_dots > 0:
                print('Победа!')
                break
            elif computer_dots == 0 and user_dots > 0:
                print('Проигрыш!')
                break


game = Game()
game.battle()

