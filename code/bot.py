import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from os import getenv
from data import user_load, user_save, locations_load
from game import up_time, new_temperature, check_status

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
                     'world_temp': -20.0
                     },
            'equipment': {'head': ['naked'],
                          'body': ['naked'],
                          'legs': ['naked'],
                          'feet': ['socks']
                          },
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

    txt = f"""день {users[user_id]['time']["days_num"]},     
время:  {users[user_id]['time']['hrs']:02}:{users[user_id]['time']['mins']:02}
состояние: {users[user_id]['state'].keys()}
статус: {users[user_id]['status']}
температура: {users[user_id]['temperature']}
"""

    bot.send_message(m_id, text=txt)
    bot.send_message(m_id, text='выберите действие', reply_markup=actions_markup)


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

    locations = locations_load()
    new_loc = call.data

    user_id = str(m_id)
    users = user_load()
    users[user_id]['location'] = new_loc

    up_time(user_id, locations[new_loc]['time_to_move'])

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
