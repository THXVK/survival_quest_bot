import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
from dotenv import load_dotenv
from os import getenv
from data import user_load, user_save, locations_load


load_dotenv()
token = getenv('TOKEN')
bot = telebot.TeleBot(token=token)





actions_markup = InlineKeyboardMarkup()
button_1 = InlineKeyboardButton('смена локации',callback_data='change_location')
button_2 = InlineKeyboardButton('спать', callback_data='sleep')
button_3 = InlineKeyboardButton('открыть инвентарь', callback_data='show_inv')


actions_markup.add(button_1, button_2, button_3, row_width=1)



@bot.message_handler(commands=['start'])
def start(message):
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
        }
        user_save(users)

    bot.send_message(chat_id=message.chat.id, text='игра начинается!')
    game_actions(message.chat.id)


def game_actions(m_id):

    #  todo: сообщения с временем и состоянием

    bot.send_message(m_id, text='выберите действие', reply_markup=actions_markup)



@bot.callback_query_handler(func=lambda call: call.data == 'change_location')
def change_location(call):
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
def change_location(call):
    m_id = call.message.chat.id
    user_id = str(m_id)
    users = user_load()
    users[user_id]['location'] = call.data
    bot.send_message(m_id, text=f'сейчас вы находитесь в локации "{users[user_id]["location"]}"')
    game_actions(m_id)


bot.polling()