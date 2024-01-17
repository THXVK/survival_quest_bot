import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from os import getenv
from data import user_load, user_save, locations_load
from game import up_time

load_dotenv()
token = getenv('TOKEN')
bot = telebot.TeleBot(token=token)


actions_markup = InlineKeyboardMarkup()
button_1 = InlineKeyboardButton('смена локации', callback_data='change_location')
button_2 = InlineKeyboardButton('спать', callback_data='sleep')
button_3 = InlineKeyboardButton('открыть инвентарь', callback_data='show_inv')
button_4 = InlineKeyboardButton('исследовать локацию', callback_data='scouting')


actions_markup.add(button_1, button_2, button_3, button_4,  row_width=1)


@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    """
    Функция отправки сообщения в ответ на /start

    во время выполнения этой команды происходит регистрация пользователя
    :param message: команда /start
    :return:
    """

    users = user_load()
    user_id = str(message.chat.id)
    if user_id not in users:
        users[user_id] = {
            'location': 'начало',
            'time': {'hrs': 0, 'mins': 0, 'days_num': 1},
            'temp': {'self_temp': 36.6,
                     'world_temp': -30.0
                     },
            'equipment': {'head': ['naked'],
                          'body': ['naked'],
                          'legs': ['naked'],
                          'feet': ['socks']
                          },
            'inv': ['ukkt,', 'глеб', 'глоб'],
            'state': {'в норме': 1},
            'status': 'жив',
            'temperature': -20.0
        }
        user_save(users)

    bot.send_message(chat_id=message.chat.id, text='игра начинается!')
    game_actions(message.chat.id)


def game_actions(m_id) -> None:
    users = user_load()
    user_id = str(m_id)

    state_list = ', '.join(list(users[user_id]['state'].keys()))
    txt = f"""день {users[user_id]['time']["days_num"]},     
время:  {users[user_id]['time']['hrs']:02}:{users[user_id]['time']['mins']:02}
состояние: {state_list[:]}
статус: {users[user_id]['status']}
температура: {users[user_id]['temperature']}
"""

    bot.send_message(m_id, text=txt)
    if users[user_id]['status'] == 'мертв':
        bot.send_message(m_id, text='вы погибли, для начала новой игры используйте /restart')
    else:
        bot.send_message(m_id, text='выберите действие', reply_markup=actions_markup)


@bot.message_handler(commands=['restart'])
def restart(message: Message) -> None:

    users = user_load()
    user_id = str(message.chat.id)

    if user_id in users:
        users[user_id] = {
            'location': 'начало',
            'time': {'hrs': 0, 'mins': 0, 'days_num': 1},
            'temp': {'self_temp': 36.6,
                     'world_temp': -30.0
                     },
            'equipment': {'head': ['naked'],
                          'body': ['naked'],
                          'legs': ['naked'],
                          'feet': ['socks']
                          },
            'inv': ['ukkt,', 'глеб', 'глоб'],
            'state': {'в норме': 1},
            'status': 'жив',
            'temperature': -20.0
        }
        user_save(users)
        bot.send_message(chat_id=message.chat.id, text='новая попытка, gl hf!')
        game_actions(message.chat.id)
    else:
        bot.send_message(chat_id=message.chat.id, text='у вас еще нет начатой игры чтобы использовать эту команду. Чтобы начать, используйте /start')


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


@bot.callback_query_handler(func=lambda call: call.data.endswith('inv'))
def inv(call) -> None:
    m_id = call.message.chat.id
    user_id = str(m_id)
    users = user_load()

    pages_list = users[user_id]['inv']
    pages_num = len(users[user_id]['inv'])
    page = 0
    cur_page = page + 1
    inv_markup = InlineKeyboardMarkup()
    button_1_2 = InlineKeyboardButton('<-', callback_data=f'forward_{page}_{pages_num}_nav')
    button_1_1 = InlineKeyboardButton('скрыть', callback_data=f'unseen_{page}_{pages_num}_nav')
    button_1_3 = InlineKeyboardButton('->', callback_data=f'back_{page}_{pages_num}_nav')
    button_1_4 = InlineKeyboardButton(f'{cur_page}/{pages_num}', callback_data=f'  ')
    inv_markup.add(button_1_1)
    inv_markup.add(button_1_2, button_1_4, button_1_3)

    bot.send_message(chat_id=m_id, text=pages_list[page], reply_markup=inv_markup)


@bot.callback_query_handler(func=lambda call: call.data.endswith('nav'))
def inv_navigation(call) -> None:
    req = call.data.split('_')
    m_id = call.message.chat.id
    user_id = str(m_id)
    users = user_load()

    pages_list = users[user_id]['inv']
    page = int(req[1])
    pages_num = int(req[2])

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
    cur_page = page + 1

    inv_markup = InlineKeyboardMarkup()
    button_1_2 = InlineKeyboardButton('<-', callback_data=f'back_{page}_{pages_num}_nav')
    button_1_1 = InlineKeyboardButton('скрыть', callback_data=f'unseen_{page}_{pages_num}_nav')
    button_1_3 = InlineKeyboardButton('->', callback_data=f'forward_{page}_{pages_num}_nav')
    button_1_4 = InlineKeyboardButton(f'{cur_page}/{pages_num}', callback_data=f'  ')
    inv_markup.add(button_1_1)
    inv_markup.add(button_1_2, button_1_4, button_1_3)
    try:
        bot.edit_message_text(chat_id=m_id, message_id=call.message.message_id,
                        text=pages_list[page], reply_markup=inv_markup)
    except Exception:
        pass


@bot.callback_query_handler(func=lambda call: call.data == 'sleep')
def sleep(call) -> None:
    m_id = call.message.chat.id
    user_id = str(m_id)
    users = user_load()

    bot.answer_callback_query(call.id, text='введите время сна (максимум - 10 часов')








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

#  todo: коллбек хендлеры - обработчики действий из game_actions


@bot.message_handler(content_types=['text'])
def echo(message: Message) -> None:
    """Функция ответа на некорректное сообщение от пользователя

    Функция отправляет сообщение с некорректным ответом от пользователя в формате
    'Вы напечатали: *сообщение пользователя*.что?'
    :param message: некорректное сообщение пользователя"""
    bot.send_message(chat_id=message.chat.id, text=f'Вы напечатали: {message.text}. Что?')


bot.polling()
