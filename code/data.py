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
    def __init__(self, name: str = 'undefined', ways: list = None, time_to_move: list = None, description: str = None, loc_temp: float = None, path: str = None):
        self.name = name
        self.ways = ways
        self.time_to_move = time_to_move
        self.description = description
        self.loc_temp = loc_temp
        self.path = path

wood = LocationsClass('лес', ['дорога'],
                      [5, 0], "Лес. Здесь довольно холодно", -5.2, '../pictures/img_1.png')
beginning = LocationsClass('дом', ['здания'], [1, 30],
                           'Ваша квартира. Из полезного осталось лишь немного еды', -4.3, '\../pictures/img_2.png')
buildings = LocationsClass('здания', ['торговый центр', 'дом', 'дорога'], [1, 0]
                           , 'Десяток порушеных зданий. Может в них еще что-то осталось?', -7.6, '../pictures/img.png')
road = LocationsClass('дорога', ['здания', 'деревня', 'лес'], [7, 0],
                      'Одна из немногих дорог из города, путь кажется вам знакомым. Деревня? Идти придется долго, да и холодно здесь', -8.1, '../pictures/img_4.png')
village = LocationsClass('деревня', ['дорога'], [7, 0],
                         'Маленькая деревушка. Когда-то вы здесь жили', -3.2, '../pictures/img_3.png')
shop = LocationsClass('торговый центр', ['здания'], [2, 45],
                      'Ранее одно из самых популярных мест в городе. Сейчас здесь мало что осталось', -5.2, '../pictures/img_5.png')


def class_to_dict(self):
    return self.__dict__


def get_name(body_part):
    for item in items_2:
        if item.name.endswith(' нет') and item.body_part == body_part:
            return item


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
        users[user_id]['equipment'][self.body_part][self.name] = self.durability
        for elem in list(users[user_id]['equipment'][self.body_part]):
            if elem.endswith('нет'):
                users[user_id]['equipment'][self.body_part].pop(elem)
        user_save(users)
        return True


naked_head = ClothesClass('шапки нет', 0, 0, 0.8, 'head')
naked_body = ClothesClass('курток нет', 0, 0, 0.8,  'body')
naked_legs = ClothesClass('штанов нет', 0, 0, 0.8,  'legs')
naked_feet = ClothesClass('ботинок нет', 0, 0, 0.8,  'feet')

cap = ClothesClass('шапка', 0.4, 80, 1.0, 'head')
coat = ClothesClass('куртка', 3.0, 100, 1.3, 'body')
jeans = ClothesClass('джинсы', 1.5, 70, 1.2, 'legs')
drawers = ClothesClass('подштанники', 1.2, 100, 1.3, 'legs')
socks = ClothesClass('носки', 0.1, 50, 0.9, 'feet')
bots = ClothesClass('ботинки', 1.1, 50, 1.2, 'feet')


class FoodClass(ItemsClass):
    def __init__(self, name, weight, food_koef, drink_koef):
        super().__init__(name, weight)
        self.food_koef = food_koef
        self.drink_koef = drink_koef

    def use(self, user_id):
        users = user_load()
        if users[user_id]['stt']['сытость']['num'] < 100:
            users[user_id]['stt']['сытость']['num'] += self.food_koef
            users[user_id]['stt']['жажда']['num'] += self.drink_koef
            if self.name == 'суп из опилок':
                users[user_id]['temp']['self_temp'] += 0.4
            users[user_id]['inv'].remove(self.name)

            return True
        else:
            return False


soup = FoodClass('суп из опилок', 0.5, 20, 5)
steak = FoodClass('стейк', 0.7, 40, -5)
canned_beans = FoodClass('консервированные бобы', 1.0, 15, 15)
bread = FoodClass('хлеб', 0.4, 20, -2)
pasta = FoodClass('макароны', 0.6, 24, 3)


class DrinksClass(ItemsClass):
    def __init__(self, name, weight, drink_koef):
        super().__init__(name, weight)
        self.drink_koef = drink_koef

    def use(self, user_id):
        users = user_load()
        if users[user_id]['stt']['жажда']['num'] < 100:
            users[user_id]['stt']['жажда']['num'] += self.drink_koef
            if self.name == 'энергетик':
                users[user_id]['stt']['стамина']['num'] += 10
            users[user_id]['inv'].remove(self.name)
            user_save(users)

            return True
        else:
            return False


energetic = DrinksClass('энергетик', 2, 40)
water_small = DrinksClass('вода (0.5л)', 1, 15)
water_medium = DrinksClass('вода (1л)', 2, 30)
water_big = DrinksClass('вода (5л)', 6, 80)
cola = DrinksClass('кола', 1, 35)

items_2 = {naked_head, naked_body, naked_legs, naked_legs, naked_feet, cap, coat, jeans, drawers, socks, bots,
           soup, steak, canned_beans, bread, pasta,
           energetic, water_small, water_medium, water_big, cola}


items_list = [cap.name, coat.name, jeans.name, drawers.name, socks.name, bots.name,
              soup.name, steak.name, canned_beans.name, bread.name, pasta.name,
              energetic.name, water_small.name, water_medium.name, water_big.name, cola.name]


locations_list = [wood, beginning, buildings, road, village, shop]

for loc in locations_list:
    locations = locations_load()
    locations[loc.name] = loc
    location_save(locations)

for item in items_2:
    items = items_load()
    items['clothes'][item.name] = item
    items_save(items)


def loot_generation(user_id):
    users = user_load()
    for loc in users[user_id]['loot']:
        k = random.randrange(0, len(items_list) - 1)
        names = random.choices(items_list, k=k)
        users[user_id]['loot'][loc] += names
    user_save(users)
