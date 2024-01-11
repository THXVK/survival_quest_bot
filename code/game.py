import random
import time
from data import user_load, user_save, locations_load


# todo: механика времени

def up_time(user_id: str, time_to: list):
    users = user_load()
    # time_to: [0] - hrs, [1] - mins
    users[user_id]['time']['mins'] += time_to[1]
    users[user_id]['time']['hrs'] += time_to[0]

    if users[user_id]['time']['mins'] >= 60:
        users[user_id]['time']['mins'] -= 60
        users[user_id]['time']['hrs'] += 1

    if users[user_id]['time']['hrs'] >= 24:
        users[user_id]['time']['hrs'] -= 24
        users[user_id]['time']['days_num'] += 1

    user_save(users)



# todo: механика состояния
# todo: инвентарь
# todo: механика боя
