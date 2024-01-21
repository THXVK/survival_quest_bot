import json
import random
filename_1 = '../data/users_data.json'


def user_load() -> dict:
    try:
        with open(filename_1, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def user_save(data: dict):
    with open(filename_1, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


filename_2 = '../data/locations_data.json'


def locations_load():
    try:
        with open(filename_2, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def location_save(data):
    with open(filename_2, 'w', encoding='utf-8') as file:
        json.dump(data, file,  indent=2, ensure_ascii=False, default=class_to_dict)

filename_3 = '../data/items_data.json'


def items_load():
    try:
        with open(filename_3, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def items_save(data):
    with open(filename_3, 'w', encoding='utf-8') as file:
        json.dump(data, file,  indent=2, ensure_ascii=False, default=class_to_dict)


filename_4 = '../data/states_data.json'


def states_load():
    try:
        with open(filename_4, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


class LocationsClass:
    def __init__(self, name: str = 'undefined', ways: list = None, time_to_move: list = None, description: str = None, loc_temp: float = None, loot: list = None):
        self.name = name
        self.ways = ways
        self.time_to_move = time_to_move
        self.description = description
        self.loc_temp = loc_temp
        self.loot = loot

    def loot_generation(self):
        k = random.randrange(0, len(items_list) - 1)
        names = random.choices(items_list, k=k)
        for name in names:
            self.loot.append(name)


def class_to_dict(self):
    return self.__dict__




class ItemsClass:
    def __init__(self, name: str = 'undefined', weight: float = 1.0, durability: int = 1):
        self.name = name
        self.weight = weight
        self.durability = durability

    def pick_up(self, user_id):
        users = user_load()
        if (users[user_id]['weight'] + self.weight) <= users[user_id]['max_weight']:
            users[user_id]['inv'].append(self.name)
            users[user_id]['weight'] += self.weight
            user_save(users)
            return True
        else:
            return False


class ClothesClass(ItemsClass):
    def __init__(self, name, weight, durability, item_temp_koef, body_part):
        super().__init__(name, weight, durability)
        self.item_temp_koef = item_temp_koef
        self.body_part = body_part

    def use(self, user_id):
        users = user_load()
        users[user_id]['inv'].remove(self.name)
        users[user_id]['equipment'][self.body_part].append(self.name)
        if users[user_id]['equipment'][self.body_part][0].endswith('нет'):
            users[user_id]['equipment'][self.body_part].remove(users[user_id]['equipment'][self.body_part][0])
        user_save(users)
        return True


naked_head = ClothesClass('шапки нет', 0, 99999, 0.8, 'head')
naked_body = ClothesClass('курток нет', 0, 99999, 0.8,  'body')
naked_legs = ClothesClass('штанов нет', 0, 99999, 0.8,  'legs')
naked_feet = ClothesClass('ботинок нет', 0, 99999, 0.8,  'feet')

cap = ClothesClass('шапка', 0.4, 80, 1.0, 'head')
coat = ClothesClass('куртка', 3.0, 100, 1.3, 'body')
jeans = ClothesClass('джинсы', 1.5, 70, 1.2, 'legs')
underpants = ClothesClass('трусы', 0.2, 150, 0.9, 'legs')
drawers = ClothesClass('подштанники', 1.2, 100, 1.3, 'legs')
socks = ClothesClass('носки', 0.1, 50, 0.9, 'feet')
bots = ClothesClass('ботинки', 1.1, 50, 1.2, 'feet')

items_list = [cap.name, coat.name, jeans.name, underpants.name, underpants.name, drawers.name, socks.name, bots.name]


wood = LocationsClass('лес', ["темный лес", "магазин", "конец города"], [5, 0], "Лес. Здесь довольно холодно", -5.2, [])
darker_wood = LocationsClass('темный лес', ["лес", "черный лес"], [10, 0], "Темный лес. Здесь даже холоднее", -10.7, [])
darkest_wood = LocationsClass('черный лес', ["темный лес", "конец"], [5, 0], "Черный лес. Дальше носа не видно, пора разворачиваться ", -15.9, [])
beginning = LocationsClass('дом', ['руины', 'здания', 'девятый район'], [0, 30], 'Ваша квартира. Из полезного осталось лишь немного еды', -4.3, [])
buildings = LocationsClass('здания', ['дом', 'руины', 'девятый район', 'дорога'], [1, 0], 'Десяток порушеных зданий. Может в них еще что-то осталось?', -7.6, [])
road = LocationsClass('дорога', ['здания', '*табличку занесло снегом*'], [7, 0], 'Одна из немногих дорог из города, путь кажется вам знакомым. Деревня? Идти придется долго, да и холодно здесь', -8.1, [])
village = LocationsClass('деревня', ['дорога'], [7, 0], 'Маленькая деревушка. Когда-то вы здесь жили', -3.2, [])

beginning.loot_generation()
buildings.loot_generation()
village.loot_generation()

items_2 = {naked_head, naked_body, naked_legs, naked_legs, naked_feet, cap,
             coat, jeans, underpants, underpants, drawers, socks,  bots}

locations_list = [wood, darker_wood, darkest_wood, beginning, buildings, road, village]
for loc in locations_list:
    locations = locations_load()
    locations[loc.name] = loc
    location_save(locations)

for item in items_2:
    items = items_load()
    items['clothes'][item.name] = item
    items_save(items)

for item in items_2:
    if item.name == 'шапка':
        pass
