import random
from data import user_load, user_save, locations_load, items_load, states_load


def up_time(user_id: str, time_to: list):
    users = user_load()

    # time_to: [0] - hrs, [1] - mins
    hrs_num = users[user_id]['time']['hrs'] + time_to[0]
    mins_num = users[user_id]['time']['mins'] + time_to[1]
    days_num = users[user_id]['time']['days_num']

    if mins_num >= 60:
        mins_num -= 60
        hrs_num += 1

    if hrs_num >= 24:
        hrs_num -= 24
        days_num += 1

    users[user_id]['time']['mins'] = mins_num
    users[user_id]['time']['hrs'] = hrs_num
    users[user_id]['time']['days_num'] = days_num
    user_save(users)
    new_temperature(user_id)


def new_temperature(user_id):
    users = user_load()
    items = items_load()
    locations = locations_load()
    random_temp = random.randrange(-50, 0) / 10

    equiped_head = users[user_id]['equipment']['head']
    equiped_body = users[user_id]['equipment']['body']
    equiped_legs = users[user_id]['equipment']['legs']
    equiped_feet = users[user_id]['equipment']['feet']

    def count_koef(equip):
        koef_equip = 1
        for i in equip:
            item = items[i]['item_temp_koef']
            koef_equip += item
        return koef_equip

    koef_head = count_koef(equiped_head)
    koef_body = count_koef(equiped_body)
    koef_legs = count_koef(equiped_legs)
    koef_feet = count_koef(equiped_feet)

    sum_koef = koef_head * koef_body * koef_legs * koef_feet
    user_total_temp = users[user_id]['temp']['self_temp'] * sum_koef
    total_world_temp = random_temp + locations[users[user_id]['location']]['loc_temp'] + users[user_id]['temp']['world_temp']
    total_temp = user_total_temp + total_world_temp

    users[user_id]['temperature'] = total_world_temp

    if total_temp > 10:
        user_save(users)
    elif 10 < total_temp < 20:
        if 'гипотермия' not in users[user_id]['state']:
            users[user_id]['state']['гипотермия'] = 0
        elif 'гипотермия' in users[user_id]['state']:
            check_status(user_id, 'гипотермия')



def check_status(user_id, state):
    users = user_load()
    states = states_load()
    if users[user_id]['state'][state] == states[state]['max_sate_streak']:
        users[user_id]['status'] = states[state]['effect_1']
        users[user_id]['state'][states[state]['effect_2']] = 0
        users[user_id]['state'].remove(state)
    else:
        users[user_id]['state'][state] += 1
    user_save(users)



# todo: механика состояний
# todo: механика сна
# todo: концовки игры
# todo: инвентарь
# todo: механика боя
