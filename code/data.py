import json

filename_1 = '../data/users_data.json'


# todo: статы предметов и их механики
# todo: инфа о локациях, картинки
# todo: инфа о врагах, их статы

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

