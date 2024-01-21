import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from os import getenv
from data import user_load, user_save, locations_load, location_save, items_load,  items_2
from game import up_time
import time

load_dotenv()
token = getenv('TOKEN')
bot = telebot.TeleBot(token=token)

# todo: еда, концовки, картинки, лут в бд игрока, ключевые  предметы

actions_markup = InlineKeyboardMarkup()
button_1 = InlineKeyboardButton('смена локации', callback_data='change_location')
button_2 = InlineKeyboardButton('спать', callback_data='sleep')
button_3 = InlineKeyboardButton('открыть инвентарь', callback_data='show_inv')
button_4 = InlineKeyboardButton('исследовать локацию', callback_data='scouting')
button_5 = InlineKeyboardButton('экипировка', callback_data='check_equip')

actions_markup.add(button_1, button_2, button_3, button_4,  row_width=1)


@bot.message_handler(commands=['help'])
def help_message(message: Message):
    """
    Функция отправки сообщения в ответ на /help
    """
    bot.send_message(chat_id=message.chat.id,
                     text="""
/start - бот представится и поприветствует вас
/help - бот пришлет список доступных действий
/restart - игра начнется заново
                     """)


@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    """
    Функция отправки сообщения в ответ на /start

    во время выполнения этой команды происходит регистрация пользователя
    :param message: команда /start
    :return:
    """
    items = items_load()
    users = user_load()
    user_id = str(message.chat.id)
    if user_id not in users:
        users[user_id] = {
            'location': 'дом',
            'time': {'hrs': 0, 'mins': 0, 'days_num': 1},
            'temp': {'self_temp': 36.6,
                     'world_temp': -10.0
                     },
            'equipment': {'head': {'шапки нет': items['clothes']['шапки нет']['durability']},
                          'body': {'курток нет':  items['clothes']['курток нет']['durability']},
                          'legs': {'трусы':  items['clothes']['трусы']['durability']},
                          'feet': {'носки':  items['clothes']['носки']['durability']}
                          },
            'inv': [],
            'max_weight': 50,
            'weight': 0,
            'state': {'в норме': {'streak': 1, 'is_true': True},
                      'усталость': {'streak': 0, 'is_true': False, 'no_sleep_steak': 0},
                      'истощение': {'streak': 0, 'is_true': False},
                      'гипотермия': {'streak': 0, 'is_true': False},
                      'голод': {'streak': 0, 'is_true': False, 'no_eat_streak': 0},
                      'сильный голод': {'streak': 0, 'is_true': False},
                      'жажда': {'streak': 0, 'is_true': False, 'no_drink_streak': 0},
                      'обезвоживание': {'streak': 0, 'is_true': False}
                      },
            'stt': {'стамина': 100, 'сытость': 100, 'жажда': 100},
            'status': 'жив',
            'temperature': -20.0
        }
        user_save(users)
        bot.send_message(chat_id=message.chat.id, text='Ваша цель - протянуть 30 дней. Игра начинается!')
    else:
        bot.send_message(chat_id=message.chat.id, text='Вы уже начали игру')

    game_actions(message.chat.id)


def game_actions(m_id) -> None:
    users = user_load()
    user_id = str(m_id)

    state_list_1 = []
    for state in users[user_id]['state']:
        if users[user_id]['state'][state]['is_true']:
            state_list_1.append(state)
    stt_txt = ''
    state_list_2 = ', '.join(state_list_1)
    for stat in users[user_id]['stt']:
        if users[user_id]['stt'][stat] >= 75:
            stt_txt += f'{stat}: в норме\n'

    txt = f"""день {users[user_id]['time']["days_num"]},     
время:  {users[user_id]['time']['hrs']:02}:{users[user_id]['time']['mins']:02}
состояние: {state_list_2[:]}
статус: {users[user_id]['status']}
температура: {users[user_id]['temperature']}
стамина: {users[user_id]['stt']['стамина']}
"""

    bot.send_message(m_id, text=txt)
    if users[user_id]['status'] == 'мертв':
        bot.send_message(m_id, text='вы погибли, для начала новой игры используйте /restart')
    else:
        bot.send_message(m_id, text='выберите действие', reply_markup=actions_markup)


@bot.message_handler(commands=['restart'])
def restart(message: Message) -> None:
    items = items_load()
    users = user_load()
    user_id = str(message.chat.id)

    if user_id in users:
        users[user_id] = {
            'location': 'дом',
            'time': {'hrs': 0, 'mins': 0, 'days_num': 1},
            'temp': {'self_temp': 36.6,
                     'world_temp': -10.0
                     },
            'equipment': {'head': {'шапки нет': items['clothes']['шапки нет']['durability']},
                          'body': {'курток нет': items['clothes']['курток нет']['durability']},
                          'legs': {'трусы': items['clothes']['трусы']['durability']},
                          'feet': {'носки': items['clothes']['носки']['durability']}
                          },
            'inv': [],
            'max_weight': 50,
            'weight': 0,
            'state': {'в норме': {'streak': 1, 'is_true': True},
                      'усталость': {'streak': 0, 'is_true': False},
                      'истощение': {'streak': 0, 'is_true': False},
                      'гипотермия': {'streak': 0, 'is_true': False},
                      'голод': {'streak': 0, 'is_true': False},
                      'сильный голод': {'streak': 0, 'is_true': False},
                      'жажда': {'streak': 0, 'is_true': False},
                      'обезвоживание': {'streak': 0, 'is_true': False}
                      },
            'stt': {'стамина': 100, 'сытость': 100, 'жажда': 100},
            'status': 'жив',
            'temperature': -20.0
        }
        user_save(users)
        bot.send_message(chat_id=message.chat.id, text='новая попытка, gl hf!')
        game_actions(message.chat.id)
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text='у вас еще нет начатой игры чтобы использовать эту команду. Чтобы начать, используйте /start')


@bot.callback_query_handler(func=lambda call: call.data.endswith('inv'))
def inv(call) -> None:
    m_id = call.message.chat.id
    user_id = str(m_id)
    users = user_load()

    pages_list = users[user_id]['inv']
    pages_num = len(users[user_id]['inv'])
    page = 0
    cur_page = page + 1
    if pages_num == 0:
        inv_markup = InlineKeyboardMarkup()
        button_1_1 = InlineKeyboardButton('скрыть', callback_data=f'unseen_{page}_{pages_num}_nav')
        inv_markup.add(button_1_1)
        bot.send_message(m_id, text='инвентарь пуст', reply_markup=inv_markup)
    else:
        inv_markup = InlineKeyboardMarkup()
        button_1_2 = InlineKeyboardButton('<-', callback_data=f'back_{page}_{pages_num}_nav')
        button_1_1 = InlineKeyboardButton('скрыть', callback_data=f'unseen_{page}_{pages_num}_nav')
        button_1_3 = InlineKeyboardButton('->', callback_data=f'forward_{page}_{pages_num}_nav')
        button_1_4 = InlineKeyboardButton(f'{cur_page}/{pages_num}', callback_data='  ')
        button_1_5 = InlineKeyboardButton(f'использовать', callback_data=f'use_{page}_{pages_num}_nav')
        inv_markup.add(button_1_5)
        inv_markup.add(button_1_2, button_1_4, button_1_3)
        inv_markup.add(button_1_1)

        bot.send_message(chat_id=m_id, text=pages_list[page], reply_markup=inv_markup)


@bot.callback_query_handler(func=lambda call: call.data.endswith('nav'))
def inv_navigation(call) -> None:
    req = call.data.split('_')
    m_id = call.message.chat.id
    user_id = str(m_id)
    users = user_load()
    pages_list = users[user_id]['inv']
    page = int(req[1])

    pages_num = len(users[user_id]['inv'])
    if req[0] == 'unseen':
        try:
            bot.delete_message(m_id, call.message.message_id)
        except TimeoutError:
            pass

    elif req[0] == 'forward':
        page += 1
        if page == pages_num:
            page = 0

    elif req[0] == 'back':
        page -= 1
        if page < 0:
            page = pages_num - 1

    elif req[0] == 'use':
        for item in items_2:
            if pages_list[page] == item.name:
                if item.use(user_id):
                    bot.send_message(m_id, text='вы использовали предмет')
                    game_actions(m_id)
                else:
                    bot.send_message(m_id, text='вы не можете использовать этот предмет')

    cur_page = page + 1
    inv_markup = InlineKeyboardMarkup()
    button_1_2 = InlineKeyboardButton('<-', callback_data=f'back_{page}_{pages_num}_nav')
    button_1_1 = InlineKeyboardButton('скрыть', callback_data=f'unseen_{page}_{pages_num}_nav')
    button_1_3 = InlineKeyboardButton('->', callback_data=f'forward_{page}_{pages_num}_nav')
    button_1_4 = InlineKeyboardButton(f'{cur_page}/{pages_num}', callback_data=f'  ')
    button_1_5 = InlineKeyboardButton(f'использовать', callback_data=f'use_{page}_{pages_num}_nav')
    inv_markup.add(button_1_5)
    inv_markup.add(button_1_2, button_1_4, button_1_3)
    inv_markup.add(button_1_1)
    try:
        bot.edit_message_text(chat_id=m_id, message_id=call.message.message_id,
                        text=pages_list[page], reply_markup=inv_markup)
    except Exception:
        pass


@bot.callback_query_handler(func=lambda call: call.data == 'sleep')
def sleep(call) -> None:
    m_id = call.message.chat.id
    msg = bot.send_message(m_id, text='введите время сна  формате "9:00" (максимум - 10 часов)')
    bot.register_next_step_handler(msg, sleep_answer)


def sleep_answer(message):
    users = user_load()
    user_id = str(message.chat.id)
    try:
        time = message.text.split(':')
        if len(time) <= 1:
            msg = bot.send_message(message.chat.id, text='вы забыли указать часы или минуты')
            bot.register_next_step_handler(msg, sleep_answer)
            return None

        hrs = int(time[0])
        mins = int(time[1])

        if (hrs == 10 and mins == 0) or (0 <= hrs < 10 and 0 <= mins < 60):
            if hrs >= 7 and mins >= 30:
                users[user_id]['state']['усталость']['is_true'] = False
                users[user_id]['state']['усталость']['streak'] = 0
                users[user_id]['state']['усталость']['no_sleep_steak'] = 0
            up_time(user_id, [hrs, mins])
            game_actions(message.chat.id)

        elif 0 > mins >= 60:
            msg = bot.send_message(message.chat.id, text='сколько в часе минут? подсказка: 1 - 59')
            bot.register_next_step_handler(msg, sleep_answer)
        else:
            msg = bot.send_message(message.chat.id, text='вы можете ввести часы только в диапазоне от 0 до 10')
            bot.register_next_step_handler(msg, sleep_answer)
    except ValueError:
        msg = bot.send_message(message.chat.id, text='введите время цифрами в указанном формате')
        bot.register_next_step_handler(msg, sleep_answer)


@bot.callback_query_handler(func=lambda call: call.data == 'change_location')
def change_location(call) -> None:
    m_id = call.message.chat.id
    user_id = str(m_id)
    users = user_load()

    locations = locations_load()
    location_name = users[user_id]['location']
    list_len = len(locations[location_name]['ways'])

    ways_markup = InlineKeyboardMarkup()
    ways_markup.row_width = list_len
    buttons = (InlineKeyboardButton(locations[location_name]['ways'][i],
                                    callback_data=locations[location_name]['ways'][i]) for i in range(list_len))
    for button in buttons:
        ways_markup.add(button, row_width=list_len)

    bot.send_message(chat_id=m_id, text='куда вы хотите пройти?', reply_markup=ways_markup)


@bot.callback_query_handler(func=lambda call: call.data in locations_load())
def change_location(call) -> None:

    m_id = call.message.chat.id

    i = 1
    txt = 'подождите' + '.' * i
    loading_message = bot.send_message(m_id, text=txt)

    locations = locations_load()
    new_loc = call.data

    user_id = str(m_id)
    users = user_load()
    users[user_id]['location'] = new_loc

    i = 2
    txt = 'подождите' + '.' * i
    bot.edit_message_text(chat_id=loading_message.chat.id, message_id=loading_message.id, text=txt)

    up_time(user_id, locations[new_loc]['time_to_move'])

    i = 3
    txt = 'подождите' + '.' * i
    bot.edit_message_text(chat_id=loading_message.chat.id, message_id=loading_message.id, text=txt)
    bot.delete_message(m_id, loading_message.id)

    bot.send_message(m_id, text=f'сейчас вы находитесь в локации "{users[user_id]["location"]}"')
    game_actions(m_id)


@bot.callback_query_handler(func=lambda call: call.data == 'scouting')
def scouting(call) -> None:
    users = user_load()
    locations = locations_load()

    m_id = call.message.chat.id
    user_id = str(m_id)
    location = users[user_id]['location']

    up_time(user_id, [1, 0])

    txt = 'вы исследуете локацию'
    load_message = bot.send_message(m_id, text=txt)
    for i in range(1):
        for count in range(4):
            time.sleep(0.7)
            txt = 'вы исследуете локацию' + '.' * count
            try:
                bot.edit_message_text(chat_id=load_message.chat.id, message_id=load_message.id, text=txt)
            except Exception:
                pass

    bot.delete_message(m_id, load_message.id)

    found_items_list = locations[location]['loot']

    if len(locations[location]['loot']) == 1:
        txt_2 = f'вы что-то нашли: {", ".join(found_items_list)}'
        bot.send_message(chat_id=m_id, text=txt_2)
        scouting_2(call, 0)

    elif len(locations[location]['loot']) > 1:
        txt_2 = f'вы нашли несколько предметов: {", ".join(found_items_list)}'
        bot.send_message(chat_id=m_id, text=txt_2)
        scouting_2(call, 0)

    else:
        txt_2 = 'вы ничего не нашли'
        bot.send_message(chat_id=m_id, text=txt_2)
        game_actions(m_id)


def scouting_2(call, x):
    m_id = call.message.chat.id
    locations = locations_load()
    user_id = str(m_id)
    users = user_load()
    location = users[user_id]['location']
    loot = locations[location]['loot']

    loot_markup = InlineKeyboardMarkup()
    button_2_1 = InlineKeyboardButton('подобрать', callback_data=f'{x}_pick-up')
    button_2_2 = InlineKeyboardButton('оcтавить', callback_data=f'{x}_drop')
    loot_markup.add(button_2_1, button_2_2)

    if x < len(loot):
        item_name = loot[x]
        bot.send_message(m_id, text=item_name, reply_markup=loot_markup)
    else:
        game_actions(m_id)
        return None


@bot.callback_query_handler(func=lambda call: call.data.endswith('pick-up') or call.data.endswith('drop'))
def pick_or_drop(call):
    m_id = call.message.chat.id
    req = call.data.split('_')
    x = int(req[0])
    choice = req[1]

    user_id = str(m_id)
    users = user_load()
    locations = locations_load()
    location = users[user_id]['location']
    loot = locations[location]['loot']
    item_name = loot[x]

    if choice == 'pick-up':
        for item in items_2:
            if item.name == item_name:
                if item.pick_up(user_id):
                    item.pick_up(user_id)
                    bot.send_message(m_id, text='вы подобрали предмет')
                    loot.pop(x)
                    location_save(locations)

                    scouting_2(call, x)
                else:
                    loot_markup = InlineKeyboardMarkup()
                    button_2_2 = InlineKeyboardButton('оcтавить', callback_data=f'{x}_drop')
                    loot_markup.add(button_2_2)
                    bot.send_message(m_id, text='вы не можете взять предмет', reply_markup=loot_markup)

    else:
        x += 1
        bot.send_message(m_id, text='вы оставили предмет')
        scouting_2(call, x)


@bot.message_handler(content_types=['text'])
def echo(message: Message) -> None:
    """Функция ответа на некорректное сообщение от пользователя

    Функция отправляет сообщение с некорректным ответом от пользователя в формате
    'Вы напечатали: *сообщение пользователя*.что?'
    :param message: некорректное сообщение пользователя"""
    bot.send_message(chat_id=message.chat.id, text=f'Вы напечатали: {message.text}. Что?')


bot.polling()


#  опус магнум?
