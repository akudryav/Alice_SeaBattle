#!/usr/bin/env python
# -*- coding: utf-8 -*-



"""
RU:
Это основная чать логики навыка Алисы "Морской бой"
Написана Сайдумаровым Семеном и Елизаровой Анастасией
Переписана и избавлена от костылей(но это не точно) Дином Дмитрием
EN:
This is main logic of Alice skill "Sea battle"
Writing by Saidumarov Semen and Elizarova Anastasiya
Rewriting and removing crutches (But it is not exactly) by Din Dmitriy
"""

from __future__ import unicode_literals
from json import dump
from random import randint, choice
from copy import deepcopy
from re import findall, match
import logging

logging.basicConfig(level=logging.DEBUG)

class NoCellsError(Exception):
    pass


class WinnerError(Exception):
    pass


class ShipBattle:
    def __init__(self):
        # Ключи - буквы, значения - индексы
        self.reversed_alphabet = {j: i for i, j in enumerate(ALPHABET)}
        # Генерируем поле
        self.field = [[0 for _ in range(10)] for _ in range(10)]

    # Вспомогательная функция для проверки на пересечения
    def check_cell(self, cell, first_cell=False):
        x, y = cell
        count = 0
        possible_cells = [(1, 1), (-1, -1), (0, 1), (1, 0), (-1, 0), (0, -1), (-1, 1), (1, -1)]
        for possible in possible_cells:
            if -1 < x + possible[0] < 10 and -1 < y + possible[1] < 10:
                if self.field[y + possible[1]][x + possible[0]] == 1:
                    count += 1

        if (count < 2 and not first_cell) or (first_cell and count == 0):
            return True
        return False

    # Метод расстановки кораблей на поле
    def place_ships(self):
        for ship in SHIPS:
            while True:
                new_field = deepcopy(self.field)
                intersection = False
                direction = choice([True, False])

                if direction:  # по горизонтали
                    random_coors = (randint(0, 10 - ship), randint(0, 9))
                    for x in range(random_coors[0], random_coors[0] + ship):
                        if x == random_coors[0]:
                            passed_cell = self.check_cell((x, random_coors[1]), True)
                        else:
                            passed_cell = self.check_cell((x, random_coors[1]), False)

                        if not passed_cell:
                            intersection = True
                            break
                        else:
                            new_field[random_coors[1]][x] = 1

                else:  # по вертикали
                    random_coors = (randint(0, 9), randint(0, 10 - ship))
                    for y in range(random_coors[1], random_coors[1] + ship):
                        if y == random_coors[1]:
                            passed_cell = self.check_cell((random_coors[0], y), True)
                        else:
                            passed_cell = self.check_cell((random_coors[0], y), False)

                        if not passed_cell:
                            intersection = True
                            break
                        else:
                            new_field[y][random_coors[0]] = 1

                if not intersection:
                    self.field = deepcopy(new_field)
                    break

    def save_to_map_json(self):
        with open('map.json', 'w', encoding='utf8') as file:
            dump({"maps": self.field}, file)


SHIPS = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
LIFE = sum(SHIPS)
ALPHABET = ['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'к']

KILLED_WORDS = ['убила', 'убил', 'потопила', 'потоплен', 'потопил']
INJURED_WORDS = ['попала', 'попал', 'попадание', 'ранил', 'ранила', 'ранен']
MISSED_WORDS = ['мимо', 'промах', 'промазала', 'промазал']
CANCEL_WORD = ['отмена', 'отменить', 'отменитьход', 'назад']
ENDING_WORDS = ['новаяигра', 'выход', 'начатьновуюигру', 'начать']

ALL_WORDS = KILLED_WORDS+INJURED_WORDS+MISSED_WORDS+CANCEL_WORD+ENDING_WORDS

PHRASES_FOR_ALICES_TURN = ['Пожалуйста, не жульничайте, я контролирую игру.', 'Помоему, сейчас не ваш ход.',
                           'Со мной такое не прокатит. Сейчас мой ход.', 'Может вы не будете меня обманывать?',
                           'Давайте я забуду это, а вы ответите еще раз.']

PHRASES_FOR_USERS_TURN = ['Сейчас ваш ход, не надо поддаваться.',
                          'Может вы что-то перепутали? Сейчас вы атакуете.',
                          'Я конечно не против, но давайте играть по правилам', 'Не люблю лёгкие победы...']

GAME_RULES = '''Каждая клетка игрового поля обозначается алфавитной буквой по горизонтали 
(от "А" до "К", исключая "Ё" и "Й", слева направо) и цифрой по вертикали (от 1 до 10 сверху вниз). 
Мои корабли уже расставлены. По вашей готовности атакуйте. 
Чтобы провести атаку скажите или введите координаты.
Для отмены действия скажите "Отменить"
Для начала новой игры скажите "Новая игра" или "Выход"'''

# кнопки помощи
#Все кнопки
BUTTONS = [
    {"title": "Мимо"},
    {"title": "Ранила"},
    {"title": "Потопила"},
    {"title": "Показать поле"},
    {"title": "Новая игра"},
    {"title": "Отменить ход"}
]
# Кнопки после хода Алисы!
BUTTONS_AFTER_ALICE_TURN = [
    {"title": "Мимо"},
    {"title": "Ранила"},
    {"title": "Потопила"},
]
#Стандартные кнопки меню
BUTTONS_MENU = [
    {"title": "Показать поле"},
    {"title": "Новая игра"},
   # {"title": "Отменить ход"}
]


# Функция для непосредственной обработки диалога.
def handle_dialog(request, response, user_storage):
    #Задаем дефолтный набор кнопок сразу, поменяем его в течение кода
    response.set_buttons(BUTTONS)
    # response.user_id
    if request.is_new_session or user_storage is None:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        ship_battle = ShipBattle()
        ship_battle.place_ships()

        user_storage = {
            "user_id": request.user_id,
            "users_turn": True,
            "alice_life": LIFE,
            "users_ships": [4, 3, 3, 2, 2, 2, 1, 1, 1, 1],
            "users_life": LIFE,
            "Target": [],  # список с координатами подбитых клеток текущего корабля
            "alices_matrix": ship_battle.field,
            "users_matrix": [[0 for _ in range(10)] for _ in range(10)],
            "cheating_stage": 0,
            "last_turn": None,
            "last_turn_field": [],
            "directions": [[0, 1], [1, 0], [-1, 0], [0, -1]],
            "to_log": False
        }

        global backup_turn

        backup_turn = user_storage

        # Приветствие
        response.set_buttons(BUTTONS_MENU)
        response.set_text('Привет! Играем в морской бой. '+GAME_RULES)
        # Выходим из функции и ждем ответа
        return response, user_storage

    # Флаг добавления в логи/чтоб не мусорить ping
    user_storage['to_log'] = True

    # Обрабатываем ответ пользователя.
    user_message = request.command.lower().strip().replace(' ', '')
    # ответ яндекс боту
    if user_message == 'ping':
        response.set_text('pong')
        user_storage['to_log'] = False
        return response, user_storage

    # вывод поля юзера
    if user_message == 'показатьполе':
        str_num = 1
        resp = '  '+' '.join([s.upper() for s in ALPHABET]) + '\n'
        for row in user_storage["alices_matrix"]:
            resp += str(str_num).rjust(2)+' '.join([str(elem).replace('3', 'X').replace('2', 'O').replace('1', '~').replace('0', '~') for elem in row]) + '\n'
            str_num += 1
        response.set_text(resp)
        response.set_buttons(BUTTONS_MENU)
        return response, user_storage

    # Пробуем перевести в координаты (между if и elif нельзя)
    try_to_make_coor = ''.join(findall(r'\w+', user_message))
    matched = match(r'\w\d0*', try_to_make_coor)

    try:
        # Проверка слова в допустимых словах
        if user_message in ALL_WORDS:


            # Проверка наличия слова в словах об отемене хода
            if user_message in CANCEL_WORD:
                try:
                    user_storage = backup_turn
                    user_storage["users_turn"] = False
                    # user_storage["alices_matrix"] = user_storage["last_turn_field"][0]
                    # user_storage["users_matrix"] = user_storage["last_turn_field"][1]
                    response.set_text('Предыдущий ваш ход и ход Алисы отменены.')
                except Exception as e:
                    print(e)
                    response.set_text('Невозможно отменить ход')

            # Проверка наличия слова в словах о начале игры
            elif user_message in ENDING_WORDS:
                user_storage = end(request, response)

            # Если ходит Алиса
            elif not user_storage["users_turn"]:
                response.set_buttons(BUTTONS_AFTER_ALICE_TURN)
                backup_turn = user_storage


                # Проверка наличия слова в словах о потоплении
                if user_message in KILLED_WORDS:
                    alice_answer = alice_fires(user_storage, "убил")
                    response.set_buttons(BUTTONS_AFTER_ALICE_TURN)
                    response.set_text(alice_answer)

                # Проверка наличия слова в словах о попадании
                elif user_message in INJURED_WORDS:
                    alice_answer = alice_fires(user_storage, "ранил")
                    response.set_buttons(BUTTONS_AFTER_ALICE_TURN)
                    response.set_text(alice_answer)

                # Проверка наличия слова в словах о промахе
                elif user_message in MISSED_WORDS:
                    alice_answer = alice_fires(user_storage, "мимо")
                    response.set_buttons(BUTTONS_MENU)
                    response.set_text(alice_answer)

            # Если игрок сказал не в свой ход
            else:
                response.set_buttons(BUTTONS_AFTER_ALICE_TURN)
                response.set_text(choice(PHRASES_FOR_USERS_TURN))

        # Проверка на присутствие шаблона re
        elif matched is not None:

            # Проверка, что сейчас ход игрока
            if user_storage["users_turn"]:
                letter = matched.group(0)[0]
                number = int(matched.group(0)[1:])

                # Проверка корректности шаблона
                if 0 < number < 11 and letter in ALPHABET:

                    # user_storage["last_turn_field"] = [user_storage["alices_matrix"], user_storage["users_matrix"]]

                    result_of_fire = user_fires(user_storage["alices_matrix"], (ALPHABET.index(letter), number - 1))

                    # Анализ результата выстрела
                    if result_of_fire == 'Мимо':
                        user_storage["users_turn"] = False
                        alice_answer = alice_fires(user_storage, "remember")
                        response.set_buttons(BUTTONS_AFTER_ALICE_TURN)
                        response.set_text('Мимо. Я хожу. ' + alice_answer)
                    else:
                        user_storage["alice_life"] -= 1
                        if user_storage["alice_life"] < 1:
                            response.set_buttons(BUTTONS_MENU)
                            response.set_text("Вы победили меня, поздравляю! Спасибо за игру!")
                            user_storage = end(request, response)
                        else:
                            response.set_buttons(BUTTONS_MENU)
                            response.set_text(result_of_fire)

                # Если не корректный ввод
                else:
                    response.set_text(
                        "Координаты клетки обозначаются буквой (от А до К, исключая Ё и Й) "
                        "и числом (от 1 до 10) для поля 10 на 10 клеток. Пример - А1.")

            # Если ход Алисы
            else:
                response.set_buttons(BUTTONS_AFTER_ALICE_TURN)
                response.set_text(choice(PHRASES_FOR_ALICES_TURN))

        # Если ничему не соответствует
        else:
            response.set_text("Простите, но я вас не поняла.")

    # Выходы из рекурсии
    except NoCellsError:
        response.set_text("Я простреляла все клетки, так что считайте, что я победила.")
        user_storage = end(request, response)

    except WinnerError:
        response.set_text("Я выиграла, спасибо за игру!")
        user_storage = end(request, response)

    # ----В любом случае-----
    #Не в любом, надо использовать разные наборы кнопок в разных случаях, в начале функции зададим так, потом помняем (если сработает)
    #response.set_buttons(BUTTONS)
    return response, user_storage


# Функция, отвечающая за стрельбу Алисы
def alice_fires(user_data, happened):

    # Рандомный выстрел
    def random_fire():
        cells_for_fire = []  # Список доступных клеток
        for _y in range(10):  # Поле 10 на 10
            for _x in range(10):
                # Пустая ли клетка
                if user_data["users_matrix"][_y][_x] == 0:
                    cells_for_fire.append((_x, _y))  # Добавляем в список возможных клеток
        # Проверка, на то, что еще остались пустые клетки
        if len(cells_for_fire) == 0:
            raise NoCellsError

        turn = choice(cells_for_fire)  # Рандомно берем
        # Сохраняем поля Алисы и пользователя до обработки выстрела

        # user_data["last_turn_field"][0] = user_data["alices_matrix"]

        user_data["last_turn"] = turn

        return "{}{}".format(ALPHABET[turn[0]].upper(), turn[1] + 1)  # Формируем ответ

    # Умный выстрел (с учетом предыдущих выстрелов для подбитого корабля)
    def clever_fire():

        # Если корабль поранен дважды, определяем положение корабля (горизонатльное/вертикальное)
        if len(user_data["Target"]) > 1:
            cell_1 = user_data["Target"][0]
            cell_2 = user_data["Target"][1]

            cells_to_del = []
            # Если горизнтальное
            if cell_1[0] == cell_2[0]:
                for direction in user_data["directions"]:
                    if direction in [[1, 0], [-1, 0]]:

                        cells_to_del.append(direction)

            # Если вертикальное
            elif cell_1[1] == cell_2[1]:
                for direction in user_data["directions"]:
                    if direction in [[0, 1], [0, -1]]:

                        cells_to_del.append(direction)

            for cell_to_del in cells_to_del:
                user_data["directions"].remove(cell_to_del)

        chosen = False
        # Выбираем клетку в которую будем стрелять
        directions_to_del = []
        cells_to_check = {}
        for possible_direction in user_data["directions"]:
            for _cell in user_data["Target"]:
                _x = possible_direction[0] + _cell[0]
                _y = possible_direction[1] + _cell[1]

                # Проверка на попадание в поле
                if 0 <= _x <= 9 and 0 <= _y <= 9:
                    # Если клетка не стрелянная стреляем
                    if user_data["users_matrix"][_y][_x] == 0:
                        cells_to_check[(_x, _y)] = possible_direction
                        chosen = True
                        break
                    # Иначе удаляем напрвление из возможных в конце цикла
                    else:
                        directions_to_del.append(possible_direction)
                # Если клетка не попадает в поле удаляем из возможных в конце цикла
                else:
                    directions_to_del.append(possible_direction)

            # Цикл для удаления возможных клеток
            for direction in directions_to_del:
                try:
                    user_data["directions"].remove(direction)
                except ValueError:
                    pass

        if chosen:
            for _cell in cells_to_check:
                if cells_to_check[_cell] in user_data["directions"]:
                    x, y = _cell
                    user_data['last_turn'] = _cell

                    user_data["last_turn_alice"] = [_cell, 0]
                    return "{}{}".format(ALPHABET[_cell[0]].upper(), _cell[1] + 1)

        elif not chosen and not user_data["directions"]:
            user_data["directions"] = [[0, 1], [1, 0], [-1, 0], [0, -1]]
            try_fire = random_fire()
            return "Судя по всему, корабль уже потоплен. " + try_fire

    def delete_ship():
        for cell in user_data["Target"]:  # Проходим по клеткам корабля и отмечаем клетки в округе
            x, y = cell  # Достаем координаты
            # Возможные клетки
            possible_cells = [(1, 1), (-1, -1), (0, 1), (1, 0), (-1, 0), (0, -1), (-1, 1), (1, -1), (0, 0)]
            for possible in possible_cells:
                # Проверка на вхождение в поле
                if -1 < x + possible[0] < 10 and -1 < y + possible[1] < 10:
                    # Отмечаем данную клетку
                    user_data["users_matrix"][y + possible[1]][x + possible[0]] = 2

        user_data["users_ships"].remove(len(user_data["Target"]))
        user_data["Target"] = []
        user_data["directions"] = [[0, 1], [1, 0], [-1, 0], [0, -1]]  # Обновляем возможные направления

    if happened == "убил" or happened == "ранил":
        # Проверка на жульничество. Если у пользователя корабль больше 4-х палубного или количество кораблей
        # определённой длины больше фиксированного
        if not (len(user_data["Target"]) + 1 in user_data["users_ships"]):
            delete_ship()
            return "Максимальный размер корабля на данный момент {} клетки. ".format(max(user_data["users_ships"]))

        user_data["users_life"] -= 1
        user_data["cheating_stage"] = 0  # Обнуляем уровень жулика

        if user_data["users_life"] < 1:
            raise WinnerError

    if happened == "убил":
        user_data["last_turn_field"] = [user_data["alices_matrix"], user_data["users_matrix"]]
        user_data["Target"].append(user_data["last_turn"])  # Добавим клетку, чтобы в цикле она тоже отметилась
        delete_ship()
        answer = random_fire()

    elif happened == "ранил":
        # Добаляем клетку в список корабля
        user_data["Target"].append(user_data["last_turn"])

        # Отмечаем прошлый выстрел в матрице
        x, y = user_data["last_turn"]
        user_data["users_matrix"][y][x] = 3

        answer = clever_fire()

    elif happened == "remember":
        if user_data["Target"]:  # Если есть раненый корабль
            answer = clever_fire()
        else:
            answer = random_fire()
    else:
        # Переключаем на ход игрока

        # user_data["last_turn_field"][1] = user_data["users_matrix"]

        user_data["users_turn"] = True

        # Выставление стрелянной клетки на поле
        x, y = user_data["last_turn"]
        user_data["users_matrix"][y][x] = 2

        # Инкримент к жульничеству
        user_data["cheating_stage"] += 1
        answer = 'Ваш ход.'

        # Замечания для жуликов
        if user_data["cheating_stage"] == 10:
            answer = 'Что-то мне не везет. Ваш ход.'
        elif user_data["cheating_stage"] == 20:
            answer = 'По теории вероятности я уже должна была попасть хотя бы раз. Ваш ход.'
        elif user_data["cheating_stage"] == 40:
            answer = 'Мне кажется, что вы играете не совсем честно.'
        elif user_data["cheating_stage"] == 60:
            answer = 'Моя гипотеза подтверждается с каждым моим промахом.'
        elif user_data["cheating_stage"] == 80:
            answer = 'Роботы в отличае от людей не умеют обманывать.'
        elif user_data["cheating_stage"] == 97:
            answer = 'Надеюсь, такая простая победа принесет вам хотя бы каплю удовольствия, ' \
                     'ведь моя задача заключается в том чтобы радовать людей и упрощать их жизнь'

    return answer


# Обработка огня игрока
# 1 - клетки кораблей, 2 - клетки, куда стреляли, 3 - подбитые клетки корабля
def user_fires(matrix, coord):
    x, y = coord
    output = 'Вы уже стреляли сюда'

    if matrix[y][x] == 0:
        output = 'Мимо'
        matrix[y][x] = 2

    elif matrix[y][x] == 1:
        matrix[y][x] = 3

        # Волновой
        ship = [(x, y)]
        was = []

        while len(ship) > 0:
            sinking = True

            x, y = ship.pop(0)
            was.append((x, y))

            # Плюс, потому что корабли в виде линий
            possible_cells = [(0, 1), (1, 0), (-1, 0), (0, -1)]

            # Проходим по возможным клеткам
            for possible in possible_cells:
                # Попадают ли клетка в поле
                if -1 < x + possible[0] < 10 and -1 < y + possible[1] < 10:

                    # Проходилась ли клетка
                    if (x + possible[0], y + possible[1]) not in was:

                        # Если в клетке 3
                        if matrix[y + possible[1]][x + possible[0]] == 3:
                            ship.append((x + possible[0], y + possible[1]))

                        # Если в клетке 1
                        elif matrix[y + possible[1]][x + possible[0]] == 1:
                            sinking = False
                            break

            if sinking:
                output = 'Потоплен'
            else:
                output = 'Ранен'
    # обновляем поле для юзера
    user_storage["alices_matrix"] = matrix
    return output

# Начало новой игры
def end(request, response):
    ship_battle = ShipBattle()
    ship_battle.place_ships()

    user_storage = {
        "user_id": request.user_id,
        "users_turn": True,
        "alice_life": LIFE,
        "users_ships": [4, 3, 3, 2, 2, 2, 1, 1, 1, 1],
        "users_life": LIFE,
        "Target": [],
        "alices_matrix": ship_battle.field,
        "users_matrix": [[0 for _ in range(10)] for _ in range(10)],
        "cheating_stage": 0,
        "last_turn": None,

        # "last_turn_field": [],
        "directions": [(0, 1), (1, 0), (-1, 0), (0, -1)],
        "to_log": True
    }

    backup_turn = user_storage


    response.set_text('Новая игра! Напомню правила. '+GAME_RULES)
    response.set_buttons(BUTTONS_MENU)

    return user_storage
