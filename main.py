# Импортируем необходимые классы.
import itertools
from random import randint

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
import sqlite3
from telegram.ext import CallbackContext, CommandHandler


def echo(update, context):
    id = update.message.from_user.id
    player = get_players(id)
    print(player)
    if player:
        pass
    else:
        pass
    update.message.reply_text('я получил смс  ' + update.message.text)


def start(update, context):
    id = update.message.from_user.id
    player = get_players(id)

    if player:
        pass
    else:
        update.message.reply_text(
            "Похоже вы тут впервые, как к вам обращаться?")
    return 1


def first_response(update, context):
    id = update.message.from_user.id
    player = get_players(id)

    text = update.message.text

    if player:
        if text == 'Создать':
            update.message.reply_text("введите название события", reply_markup=excup)
            return 2
        update.message.reply_text("Главное меню", reply_markup=markup)
        if text == "Мои события":
            rooms1 = get_rooms(id)
            rooms = [[str(i[0]) + " " + i[2]] for i in rooms1]
            rooms.append(['Отмена'])
            rooms = ReplyKeyboardMarkup(rooms, one_time_keyboard=True)
            update.message.reply_text('Ваши события', reply_markup=rooms)
            return 3
        if text == 'Присоединиться':
            update.message.reply_text('Для присоединения введите код события', reply_markup=excup)
            return 7
    else:
        if text == '/start':
            update.message.reply_text(
                "Похоже вы тут впервые, как к вам обращаться?")
        else:
            new_user(id, text)

            update.message.reply_text("Вы успешно зарегестрировались")
            update.message.reply_text("Главное меню", reply_markup=markup)
    return 1


def second_response(update, context):
    text = update.message.text
    if text == 'Отмена':
        update.message.reply_text("Главное меню", reply_markup=markup)
        return 1
    update.message.reply_text("Событие " + text + " успешно создано")
    new_room(update.message.from_user.id, text)
    update.message.reply_text("Главное меню", reply_markup=markup)
    return 1


def in_room(update, context):
    global users_online
    text = update.message.text
    id = update.message.from_user.id
    users_online[str(id)] = {'code': 'edit', 'id': text.split()[0]}

    con = sqlite3.connect('db.db')
    cor = con.cursor()
    print(str(users_online[str(id)]['id']))
    if text == 'Отмена':
        update.message.reply_text("Главное меню", reply_markup=markup)
        return 1
    admin = cor.execute(f"select admin from rooms where id = {str(users_online[str(id)]['id'])}").fetchone()[0]
    print(admin, id)
    if str(id) != str(admin):
        edit = [['Покинуть событие'],  ['Пригласить'], ['Назад']]
    else:
        edit = [['Изменить'], ['Покинуть событие'], ['Назад'], ['Пригласить']]
    edit = ReplyKeyboardMarkup(edit, one_time_keyboard=True)


    vir = get_room_data(text.split()[0])
    title = vir['title']
    des = vir['des']
    if not des:
        des = ""
    date = vir['date'][0]
    if not date:
        date = ""
    place = [vir['place']][0][0]
    if not place:
        place = ""
    print(vir['players'])
    players = [get_players(x)[0] for x in vir['players'][0].split()]

    stroka = title + '\n\nОписание:\n' + des + '\n\nВремя проведения:\n' \
             + date + '\n\nАдрес:\n' + place + '\n\nУчастники:\n' + "\n".join(players)
    update.message.reply_text(stroka, reply_markup=edit)

    return 4


def edit0(update, context):
    global users_online
    text = update.message.text
    id = update.message.from_user.id
    if text == 'Назад':
        update.message.reply_text("Главное меню", reply_markup=markup)
        return 1
    if text == 'Покинуть событие':
        leave(id, users_online[str(id)]['id'])
        update.message.reply_text("Главное меню", reply_markup=markup)
        return 1
    if text == 'Пригласить':
        key = get_key(users_online[str(id)]['id'])
        update.message.reply_text("Скопируйте код для приглашения участников")
        update.message.reply_text(key, reply_markup=markup)
        return 1
    con = sqlite3.connect('db.db')
    cor = con.cursor()
    admin = cor.execute(f"select admin from rooms where id = {str(users_online[str(id)]['id'])}").fetchone()[0]
    if str(id) != str(admin):
        update.message.reply_text("Главное меню", reply_markup=markup)
        return 1
    edit = [['Изменить название'], ['Изменить описание'], ['Изменить место проведения'],
            ['Изменить дату проведения'],
            ['Назад']]
    edit = ReplyKeyboardMarkup(edit, one_time_keyboard=True)
    update.message.reply_text("Изменить", reply_markup=edit)
    return 5


def edit(update, context):
    global users_online
    text = update.message.text
    id = update.message.from_user.id
    room = users_online[str(id)]['id']
    if text == 'Изменить название':
        update.message.reply_text("введите новое название", reply_markup=excup)
        users_online[str(id)] = {'code': 'title', 'id': room}
        return 6
    if text == 'Изменить описание':
        update.message.reply_text("Введите новое описание", reply_markup=excup)
        users_online[str(id)] = {'code': 'des', 'id': room}
        return 6
    if text == 'Изменить место проведения':
        update.message.reply_text("Введите новое место проведения", reply_markup=excup)
        users_online[str(id)] = {'code': 'place', 'id': room}
        return 6
    if text == 'Изменить дату проведения':
        update.message.reply_text("введите новую дату и время", reply_markup=excup)
        users_online[str(id)] = {'code': 'date', 'id': room}
        return 6
    if text == 'Удалить событие':
        update.message.reply_text("введите новую дату и время", reply_markup=excup)
        users_online[str(id)] = {'code': 'del', 'id': room}
        return 6
    update.message.reply_text("Главное меню", reply_markup=markup)
    return 1


def join(update, context):
    text = update.message.text
    con = sqlite3.connect('db.db')
    cor = con.cursor()
    room = cor.execute(f"select id from rooms where key = '{text}'").fetchone()
    if room:
        av = cor.execute("select users from rooms where id =" + (str(room[0]))).fetchone()
        av = str(av[0])
        id = update.message.from_user.id
        if str(id) in av:
            update.message.reply_text("Вы уже учавствуете в этом событии", reply_markup=markup)
            return 1
        av = av + ' ' + str(id)
        print(av, id)
        cor.execute(f"update rooms set users = '{av}' where id = '{str(room[0])}'")
        con.commit()
        update.message.reply_text("Вы присоединились успешно", reply_markup=markup)
        return 1
    else:
        con.close()
        update.message.reply_text("Неверный код", reply_markup=markup)
        return 1
    con.commit()
    return a


def efine(update, context):
    global users_online
    text = update.message.text
    id = update.message.from_user.id
    con = sqlite3.connect('db.db')
    cor = con.cursor()
    sos = users_online[str(id)]['code']
    room = users_online[str(id)]['id']

    if text == 'Отмена' or text == 'Назад':
        update.message.reply_text("Главное меню", reply_markup=markup)
        return 1
    if sos == 'title':
        cor.execute(f"update rooms set title = '{text}' where id = {str(room)}")
        update.message.reply_text("Изменения успешны")
        update.message.reply_text("Главное меню", reply_markup=markup)

    if sos == 'des':
        cor.execute(f"update rooms set description = '{text}' where id = {str(room)}")
        update.message.reply_text("Изменения успешны")
        update.message.reply_text("Главное меню", reply_markup=markup)

    if sos == 'place':
        cor.execute(f"update rooms set place = '{text}' where id = {str(room)}")
        update.message.reply_text("Изменения успешны")
        update.message.reply_text("Главное меню", reply_markup=markup)

    if sos == 'date':
        cor.execute(f"update rooms set date = '{text}' where id = {str(room)}")
        update.message.reply_text("Изменения успешны")
        update.message.reply_text("Главное меню", reply_markup=markup)

    if sos == 'del':
        cor.execute(f"delete from rooms where id = {str(room)}")
        update.message.reply_text("событие удалено")
        update.message.reply_text("Главное меню", reply_markup=markup)
    con.commit()
    con.close()
    return 1


def leave(id, room):
    con = sqlite3.connect('db.db')
    cor = con.cursor()
    a = cor.execute("select users from rooms where id =" + (str(room))).fetchone()
    a = str(a[0])

    a = a.replace(str(id), 'a')
    cor.execute(f"update rooms set users = '{a}' where id = {str(room)}")
    con.commit()
    con.close()
    return a


def stop(update, context):
    return conv_handler.END


def get_key(id):
    con = sqlite3.connect('db.db')
    cor = con.cursor()
    a = cor.execute(f"select key from rooms where id = '{id}'").fetchone()[0]
    con.commit()
    con.close()
    return a


def get_players(id):
    con = sqlite3.connect('db.db')
    cor = con.cursor()
    a = cor.execute(f"select name from users where id_teegram = '{id}'").fetchone()

    con.commit()
    con.close()
    return a


def get_room_data(id):
    con = sqlite3.connect('db.db')
    cor = con.cursor()
    ans = {}
    a = cor.execute(f"select title from rooms where id ={id}").fetchone()[0]
    ans['title'] = a
    a = cor.execute(f"select description from rooms where id ={id}").fetchone()[0]
    ans['des'] = a
    a = cor.execute(f"select users from rooms where id ={id}").fetchone()
    ans['players'] = a
    a = cor.execute(f"select date from rooms where id ={id}").fetchone()
    ans['date'] = a
    a = cor.execute(f"select place from rooms where id ={id}").fetchone()
    ans['place'] = a
    con.commit()
    con.close()
    return ans


def get_rooms(id):
    con = sqlite3.connect('db.db')
    cor = con.cursor()
    a = cor.execute(f"select * from rooms where users like '%{id}%'").fetchall()
    con.commit()
    con.close()
    return a


def new_user(id, name):
    con = sqlite3.connect('db.db')
    cor = con.cursor()
    a = cor.execute("INSERT INTO users (id_teegram, name) VALUES (?, ?)", (id, name))
    con.commit()
    con.close()
    return a


def new_room(id, title):
    con = sqlite3.connect('db.db')
    cor = con.cursor()
    key1 = itertools.permutations('QFS01LVmOPZ4G', 5)
    rand = randint(1, 154440)
    a = [i for i in key1]
    key1 = "".join(a[rand])
    a = cor.execute("INSERT INTO rooms (users, admin, title, key) VALUES (?, ?, ?, ?)", (id, id, title, key1))
    con.commit()
    con.close()
    return a


users_online = {}
reply_keyboard = [['Мои события'], ['Присоединиться'], ['Создать']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
reply_keyboard = [['Отмена']]
excup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

updater = Updater('1735414929:AAEFfxgh8c7HOPEeq45mLsyoOPR9YuGUIZ4', use_context=True)
dp = updater.dispatcher
text_handler = MessageHandler(Filters.text, echo)
# dp.add_handler(text_handler)
conv_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.text, first_response)],
    states={
        1: [MessageHandler(Filters.text, first_response)],
        2: [MessageHandler(Filters.text, second_response)],
        3: [MessageHandler(Filters.text, in_room)],
        4: [MessageHandler(Filters.text, edit0)],
        5: [MessageHandler(Filters.text, edit)],
        6: [MessageHandler(Filters.text, efine)],
        7: [MessageHandler(Filters.text, join)]
    },
    fallbacks=[CommandHandler('stop', stop)]
)
dp.add_handler(conv_handler)
updater.start_polling()
updater.idle()
