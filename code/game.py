import random
from data import user_load, user_save, locations_load, items_load, states_load


def up_time(user_id: str, time_to: list):
    users = user_load()

    # time_to: [0] - hrs, [1] - mins
    hrs_num = users[user_id]['time']['hrs'] + time_to[0]
    mins_num = users[user_id]['time']['mins'] + time_to[1]
    days_num = users[user_id]['time']['days_num']

    check_stt(user_id, time_to[0], time_to[1])

    for i in range(time_to[0]):
        for body_part in users[user_id]['equipment'].keys():
            for item in users[user_id]['equipment'][body_part]:
                if item.endswith('нет'):
                    users[user_id]['equipment'][body_part][item] += 1
                else:
                    users[user_id]['equipment'][body_part][item] -= 1
                    if users[user_id]['equipment'][body_part][item] < 0:
                        users[user_id]['equipment'][body_part].remove(item)

    if mins_num >= 60:
        mins_num -= 60
        hrs_num += 1

    if hrs_num >= 24:
        hrs_num -= 24
        days_num += 1
        for state in users[user_id]['state']:
            if users[user_id]['state'][state]['is_true']:
                users[user_id]['state'][state]['streak'] += 1

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

    if users[user_id]['time']['days_num'] in [5, 10, 20, 25, 27]:
        users[user_id]['temp']['world_temp'] -= 5.0

    equiped_head = users[user_id]['equipment']['head']
    equiped_body = users[user_id]['equipment']['body']
    equiped_legs = users[user_id]['equipment']['legs']
    equiped_feet = users[user_id]['equipment']['feet']

    def count_koef(equip):
        koef_equip = 1
        for i in equip:
            item = items['clothes'][i]['item_temp_koef']
            koef_equip *= item
        return koef_equip

    koef_head = count_koef(equiped_head)
    koef_body = count_koef(equiped_body)
    koef_legs = count_koef(equiped_legs)
    koef_feet = count_koef(equiped_feet)

    sum_koef = koef_head * koef_body * koef_legs * koef_feet
    user_total_temp = users[user_id]['temp']['self_temp'] * sum_koef
    total_world_temp = (random_temp +
                        locations[users[user_id]['location']]['loc_temp'] + users[user_id]['temp']['world_temp'])
    total_temp = user_total_temp + total_world_temp
    users[user_id]['temperature'] = total_world_temp
    if total_temp > 0:
        pass
    elif total_temp < 10:
        try:
            users[user_id]['state']['в норме']['is_true'] = False
        except KeyError:
            pass
        if not users[user_id]['state']['гипотермия']:
            users[user_id]['state']['гипотермия']['is_true'] = True

        else:
            check_status('гипотермия', user_id)

    else:
        users[user_id]['state']['гипотермия']['streak'] = 2

        check_status('гипотермия', user_id)
    user_save(users)

def check_status(state, user_id):
    users = user_load()
    states = states_load()

    if users[user_id]['state'][state]['streak'] == states[state]['max_state_streak']:
        users[user_id]['status'] = states[state]['effect_1']
        users[user_id]['state'][states[state]['effect_2']]['is_true'] = True
        users[user_id]['state'][state]['is_true'] = False
    else:
        users[user_id]['state'][state]['streak'] += 1

    if len(users[user_id]['state']) == 0 and users[user_id]['status'] != 'мертв':
        users[user_id]['state']['в норме']['is_true'] = True
    else:
        try:
            users[user_id]['state']['в норме']['is_true'] = True
        except KeyError:
            pass
    user_save(users)


def check_stt(user_id, hrs, mins):
    users = user_load()

    users[user_id]['stt']['стамина'] -= (3 * hrs)
    users[user_id]['stt']['стамина'] -= (1 * mins)

    user_save(users)
