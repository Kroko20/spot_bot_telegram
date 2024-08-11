import telebot
import random
import traceback
import sqlite3
from datetime import *
import colorama
import random
import threading
import re
import os

colorama.init() # инициализация библиотеки колорама (чтобы красиво текст можно было сделать)
dt_now = str(datetime.today().strftime('%d.%m.%Y')) # сегодняшняя дата
bot = telebot.TeleBot('6248526153:AAHBgRXYfupvtARLuVyIaUUxP7y9VwQOpqU') # инициализируем токен бота
print(colorama.Fore.CYAN + "[INFO] " + colorama.Fore.WHITE + f"Бот включен\nДата: {dt_now}") # сообщение о работе бота
db = sqlite3.connect('database.db', check_same_thread=False) # подключаем базу данных
sql = db.cursor() # база данных
cooldown = datetime.now()

lock = threading.Lock()

sql.execute("""CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY,
    login TEXT,
    fname TEXT,
    datereg TEXT,
    status INT,
    score INT,
    cooldown TEXT
)""")

markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True) # делаем клавиатуру
markup_admin = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True) # делаем клавиатуру админов

card_keyboard = telebot.types.KeyboardButton('Получить карту 🧀') # добавляем кнопку
profile = telebot.types.KeyboardButton("Профиль 👤")
top = telebot.types.KeyboardButton("Топ 🏆")
games = telebot.types.KeyboardButton("Игры 🎮")
admin_panel = telebot.types.KeyboardButton("Панель админа 💎")

markup.add(card_keyboard, profile, games, top) # добавляем кнопочку к клавиатуре
markup_admin.add(card_keyboard, profile, games, top, admin_panel)

def get_id_adm():
    try:
        lock.acquire(True)
        sql.execute(f"SELECT id from users WHERE status = 1")
    finally:
        lock.release()
    listadms = sql.fetchall()
    global statusadms
    statusadms = []
    global idlistadms
    for idlistworkers in listadms:
        idlistworkers = ''.join(map(str, idlistworkers))
        idlistworkers = re.sub(r"[,]", "", idlistworkers)
        statusadms.append(int(idlistworkers))

def get_id():
    try:
        lock.acquire(True)
        sql.execute(f"SELECT id from users")
    finally:
        lock.release()
    listids = sql.fetchall()
    global idlist
    idlist = []
    for idlistworkers in listids:
        idlistworkers = ''.join(map(str, idlistworkers))
        idlistworkers = re.sub(r"[,]", "", idlistworkers)
        idlist.append(int(idlistworkers))

@bot.message_handler(commands=['start'])
def start(message):
    if str(sql.fetchall()) == '[]':
            sql.execute(f"INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", (message.chat.id, message.from_user.username, message.from_user.first_name, dt_now, 0, 0, cooldown)) # добавляем человека в базу
            try:
                lock.acquire(True)
                sql.execute(f"UPDATE users SET login = '{message.from_user.username}' WHERE id = {message.chat.id}")
                sql.execute(f"UPDATE users SET fname = '{message.from_user.first_name}' WHERE id = {message.chat.id}")
            finally:
                lock.release()
            db.commit()

    get_id_adm()
    if message.chat.id in statusadms:
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}', reply_markup = markup_admin) # отправляем сообщение приветствие и добавляем клавиатуру
    else:
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}', reply_markup = markup) # отправляем сообщение приветствие и добавляем клавиатуру

@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.text == 'Получить карту 🧀':
        try:
            lock.acquire(True)
            sql.execute(f"SELECT cooldown FROM users WHERE id = {message.chat.id}")
        finally:
            lock.release()
        cooldown = sql.fetchall()
        get_cooldown = cooldown[0]
        get_cooldown = get_cooldown[0]
        cooldown = datetime.strptime(get_cooldown, "%Y-%m-%d %H:%M:%S.%f")
        now_cooldown = datetime.now().replace(microsecond=0)
        if now_cooldown > cooldown:
            rarity = random.randint(0, 104) # рандом редкости
            if rarity >= 0 and rarity <= 44:
                rarity = "говно"
                files_count = os.listdir(path="cards/shit")
                file = random.choice(files_count)
                card = open(f"cards/shit/{file}", 'rb')
                score = 100
            elif rarity >= 45 and rarity <= 69:
                rarity = "редкая"
                files_count = os.listdir(path="cards/rare")
                file = random.choice(files_count)
                card = open(f"cards/rare/{file}", 'rb')
                score = 250
            elif rarity >= 70 and rarity <= 85:
                rarity = "эпическая"
                files_count = os.listdir(path="cards/epic")
                file = random.choice(files_count)
                card = open(f"cards/epic/{file}", 'rb')
                score = 500
            elif rarity >= 86 and rarity <= 96:
                rarity = "мифическая"
                files_count = os.listdir(path="cards/mythical")
                file = random.choice(files_count)
                card = open(f"cards/mythical/{file}", 'rb')
                score = 1000
            elif rarity >= 97 and rarity <= 102:
                rarity = "легендарная"
                files_count = os.listdir(path="cards/legendary")
                file = random.choice(files_count)
                card = open(f"cards/legendary/{file}", 'rb')
                score = 5000
            elif rarity >= 103 and rarity <= 104:
                rarity = "роспись"
                files_count = os.listdir(path="cards/painting")
                file = random.choice(files_count)
                card = open(f"cards/painting/{file}", 'rb')
                score = 10000

            bot.send_photo(message.chat.id, card, caption=f"редкость: {rarity}\nочки: {score}") # отправляем карточку
            sql.execute(f"SELECT score FROM users WHERE id = {message.chat.id}")
            try:
                lock.acquire(True)
            finally:
                lock.release()
            old_score = sql.fetchall()
            old_score = ''.join(map(str, old_score))
            old_score = re.sub(r"[(),']", "", old_score)
            new_score = int(old_score) + int(score)
            sql.execute(f"UPDATE users SET score = '{int(new_score)}' WHERE id = {message.chat.id}")
            cooldown = datetime.now() + timedelta(seconds=7200)
            sql.execute(f"UPDATE users SET cooldown = '{cooldown}' WHERE id = {message.chat.id}")
            db.commit()
        else:
            left_time = cooldown - now_cooldown
            bot.send_message(message.chat.id, "Извини, ты еще не можешь взять новую карточку! Приходи через: {}".format(str(left_time).split('.')[0]))

    if message.text == "Профиль 👤":
        try:
            lock.acquire(True)
            sql.execute(f"SELECT score from users WHERE id = {message.chat.id}")
        finally:
            lock.release()
        score = sql.fetchall()
        score = ''.join(map(str, score))
        score = re.sub(r"[(),']", "", score)
        sql.execute(f"SELECT id from users WHERE id = {message.chat.id}")
        id = sql.fetchall()
        id = ''.join(map(str, id))
        id = re.sub(r"[(),']", "", id)
        get_id_adm()
        if message.chat.id in statusadms:
            bot.send_message(message.chat.id, f"Имя: **{message.from_user.first_name}**\nID: {id}\nОчки: {score}", reply_markup=markup_admin, parse_mode="MarkdownV2")
        else:
            bot.send_message(message.chat.id, f"Имя: **{message.from_user.first_name}**\nID: {id}\nОчки: {score}", reply_markup=markup, parse_mode="MarkdownV2")
    
    if message.text == "Игры 🎮":
        key = telebot.types.InlineKeyboardMarkup()
        duel = telebot.types.InlineKeyboardButton(text="Дуэль ⚔️", callback_data = "duel")
        key.add(duel)
        bot.send_message(message.chat.id, "Режимы игр:", reply_markup=key)

    if message.text == "Топ 🏆":
        top_scores = ""
        try:
            lock.acquire(True)
            users = sql.execute("SELECT * FROM `users` ORDER BY `score` DESC LIMIT 10").fetchall()
        finally:
            lock.release()
        num = 1
        for user in users:
            top_scores += f"<b>{num}. @{user[1]}</b> - <b>{user[5]}</b>\n"
            num = num+1
        bot.send_message(message.chat.id, '<b>🏆 Топ 10:</b>\n\n'+top_scores, parse_mode='HTML')

    if message.text == "Панель админа 💎":
        get_id_adm()
        if message.chat.id in statusadms:
            sql.execute(f"SELECT id FROM users")
            alluserslist = sql.fetchall()
            global allusers
            allusers = []
            i = 0
            for idlist in alluserslist:
                idlist = ''.join(map(str, idlist))
                idlist = re.sub(r"[,]", "", idlist)
                allusers.append(int(idlist))
                i += 1
            key = telebot.types.InlineKeyboardMarkup()
            workers_msg = telebot.types.InlineKeyboardButton(text="Рассылка ✉️", callback_data = "workers_msg")
            get_db = telebot.types.InlineKeyboardButton(text="Получить базу данных 📚", callback_data = "getdb")
            check_user_id = telebot.types.InlineKeyboardButton(text="Чек чела (ID)", callback_data = "check_user_id")
            key.add(workers_msg, get_db, check_user_id)
            bot.send_message(message.chat.id, f"Всего пользователей в боте: {i}\nАдмин функции:", reply_markup=key)
        else:
            bot.send_message(message.chat.id, "Доступ запрещен.")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global db
    global id_0
    global id_1
    global id_2
# начало для админов
    if call.data == "workers_msg":
        a = bot.send_message(call.message.chat.id, "Введите текст рассылки:")
        bot.register_next_step_handler(a, workers_msg)
    elif call.data == "getdb":
        db = open("database.db", "rb")
        bot.send_document(call.message.chat.id, db)
        bot.send_message(call.message.chat.id, f"Backup {datetime.today().strftime('%d.%m.%Y')}")
        db.close()
    elif call.data == "check_user_id":
        a = bot.send_message(call.message.chat.id, "Введите ID пользователя:")
        bot.register_next_step_handler(a, check_user_id)
# конец для админов
        
# начало для игроков
    elif call.data == "duel":
        a = bot.send_message(call.message.chat.id, "Введите ID пользователя:")
        bot.register_next_step_handler(a, duel_id)
    elif call.data == "yes_duel":
        score = sql.execute(f"SELECT score FROM users WHERE id = {call.message.chat.id}").fetchone()
        a = bot.send_message(call.message.chat.id, f"Введите сумму ставки (у вас {int(score[0])} очков):")
        id_0 = call.message.chat.id
        bot.register_next_step_handler(a, duel)
    elif call.data == "no_duel":
        return
    elif call.data == "accept_duel":
        number = random.randint(1, 100) # рандом редкости
        if number >= 1 and number <= 50:
            id_1 = sql.execute(f"SELECT * FROM users WHERE id = {id_0}").fetchone()
            id_2 = sql.execute(f"SELECT * FROM users WHERE id = {id}").fetchone()
            bot.send_message(id_1[0], f"Выиграл {id_1[2]}! Выпало число {number}.")
            bot.send_message(id_2[0], f"Выиграл {id_1[2]}! Выпало число {number}.")
            one_score = sql.execute(f"SELECT score FROM users WHERE id = {id_1[0]}").fetchone()
            one_score_int = int(one_score[0])
            two_score = sql.execute(f"SELECT score FROM users WHERE id = {id_2[0]}").fetchone()
            two_score_int = int(two_score[0])
            one_score_int += int(bet)
            two_score_int -= int(bet)
            sql.execute(f"UPDATE users SET score = {one_score_int} WHERE id = {id_1[0]}")
            sql.execute(f"UPDATE users SET score = {two_score_int} WHERE id = {id_2[0]}")
            db.commit()
            messageId = call.message.message_id
            bot.delete_message(chat_id=call.message.chat.id, message_id=messageId)
            return
        elif number >= 51 and number <= 100:
            id_1 = sql.execute(f"SELECT * FROM users WHERE id = {id_0}").fetchone()
            id_2 = sql.execute(f"SELECT * FROM users WHERE id = {id}").fetchone()
            bot.send_message(id_1[0], f"Выиграл {id_2[2]}! Выпало число {number}.")
            bot.send_message(id_2[0], f"Выиграл {id_2[2]}! Выпало число {number}.")
            one_score = sql.execute(f"SELECT score FROM users WHERE id = {call.message.chat.id}").fetchone()
            one_score_int = int(one_score[0])
            two_score = sql.execute(f"SELECT score FROM users WHERE id = {id}").fetchone()
            two_score_int = int(two_score[0])
            one_score_int -= int(bet)
            two_score_int += int(bet)
            sql.execute(f"UPDATE users SET score = {one_score_int} WHERE id = {id_1[0]}")
            sql.execute(f"UPDATE users SET score = {two_score_int} WHERE id = {id_2[0]}")
            db.commit()
            messageId = call.message.message_id
            bot.delete_message(chat_id=call.message.chat.id, message_id=messageId)
            
    elif call.data == "reject_duel":
        bot.send_message(id_1[0], "Дуэль отклонена!")
        bot.send_message(id_2[0], "Дуэль отклонена!")
        return
# конец для игроков

def workers_msg(message):
    get_id()
    text_msg = message.text
    for ids in idlist:
        bot.send_message(ids, text_msg)
    bot.send_message(message.chat.id, "Рассылка завершена!")

def check_user_id(message):
    id = message.text
    try:
        user = sql.execute(f"SELECT * FROM users WHERE id = {id}").fetchone()
    except:
        bot.send_message(message.chat.id, "Произошла ошибка! Возможно ошибка в ID")
    bot.send_message(message.chat.id, f"Имя: {user[2]}\nID: {id}\nОчки: {user[5]}\nЮзернейм: @{user[1]}\nСтатус человека: {user[4]}")

def duel_id(message):
    global id
    id = message.text
    try:
        user = sql.execute(f"SELECT * FROM users WHERE id = {id}").fetchone()
    except:
        bot.send_message(message.chat.id, "Произошла ошибка! Возможно ошибка в ID")
    key = telebot.types.InlineKeyboardMarkup()
    yes = telebot.types.InlineKeyboardButton(text="Да ✅", callback_data = "yes_duel")
    no = telebot.types.InlineKeyboardButton(text="Нет ❌", callback_data = "no_duel")
    key.add(yes, no)
    try:
        bot.send_message(message.chat.id, f"Игрок: {user[2]}\nВы уверены что хотите сыграть с ним?", reply_markup=key)
    except:
        bot.send_message(message.chat.id, "Произошла ошибка! Возможно ошибка в ID")

def duel(message):
    global bet
    bet = message.text
    score = sql.execute(f"SELECT score FROM users WHERE id = {message.chat.id}").fetchall()
    score = ''.join(map(str, score))
    score = re.sub(r"[(),']", "", score)
    score_enemy = sql.execute(f"SELECT score FROM users WHERE id = {id}").fetchall()
    score_enemy = ''.join(map(str, score_enemy))
    score_enemy = re.sub(r"[(),']", "", score_enemy)
    try:
        score_itog = int(score) - int(bet)
        if score == 0:
            bot.send_message(message.chat.id, "У вас нет очков.")
            return
        elif score_itog <= -1:
            bot.send_message(message.chat.id, "Неправильная сумма.")
            return
        elif int(score_enemy) < int(bet):
            bot.send_message(message.chat.id, "У противника нет очков.")
            return
        elif int(bet) > int(score):
            bot.send_message(message.chat.id, "У вас не хватает очков.")
            return
        else:
            key = telebot.types.InlineKeyboardMarkup()
            accept = telebot.types.InlineKeyboardButton(text="Принять ✅", callback_data = "accept_duel")
            reject = telebot.types.InlineKeyboardButton(text="Отклонить ❌", callback_data = "reject_duel")
            key.add(accept, reject)
            bot.send_message(message.chat.id, "Дуэль отправлена")
            bot.send_message(id, f"Вам пришла дуэль от игрока {message.from_user.first_name} | {message.chat.id} на сумму {bet} очков!", reply_markup=key)
    except:
        bot.send_message(message.chat.id, "Произошла ошибка! Попробуйте снова.")
        return

if __name__ == '__main__': 
    while True: # чтобы бот не умирал при каждой ошибке, это делает возможным постоянную работу бота
        try:
            bot.polling()
        except Exception as ex:
            print(traceback.format_exc())
