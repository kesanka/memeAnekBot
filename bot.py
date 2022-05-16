from subprocess import call
import telebot
import datetime
import random
from telebot import types
import io
import os
import sqlite3
import schedule
import time
from DBactions import db_addAneki, db_addMeme, db_addWatchedAnek, db_addWatchedMeme, db_table_val, updateNumberOfAneks, updateNumberOfMemes


adminMode = False
addTextAnek = False
addMeme = False
bot = telebot.TeleBot('5351857985:AAEOVJyKimwQZzNEcuY3kW7MOcyXAiApT4Q')
conn = sqlite3.connect('D:\\TelegramBotPython\\db\\database.db', check_same_thread=False)
cursor = conn.cursor()


#Настройки расписания
def job():
    chatid = 1982562845
    url = 'https://sun9-18.userapi.com/s/v1/ig2/dJwR5ERrz-iEUYZoDBMaSNLIf_E7PR8dfGRO3xIRBhEgYVH_AvzSt6xMbxKa-b5fPUXFfzycWbTEscTC0106OBfY.jpg?size=1001x1080&quality=95&type=album'
    bot.send_photo(chatid, url)

schedule.every().minute.at(":20").do(job)



#команды пользователя
@bot.message_handler(commands=['start'])
@bot.message_handler(func = lambda message: message.text == 'Начать')
def start(message):
    kb = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=False)
    btn1 = types.KeyboardButton(text = "Смотреть фотографии животных!")
    btn2 = types.KeyboardButton(text = 'Смотреть мемы!')
    btn3 = types.KeyboardButton(text = "Прочитать анекдот!")
    kb.add(btn1, btn2, btn3)
    date = message.date + 60 * 60 * 8
    text = ', сегодня ' + str(datetime.datetime.utcfromtimestamp(date))
    if message.from_user.first_name != None:
        bot.send_message(message.chat.id, 'Привет, ' + str(message.from_user.first_name)  + text + ". Чем займемся?", reply_markup=kb)
    elif message.from_user.last_name != None:
        bot.send_message(message.chat.id, 'Привет, '  + str(message.from_user.last_name) + text + ". Чем займемся?", reply_markup=kb)
    else:
        bot.send_message(message.chat.id, 'Привет, '  + str(message.from_user.username) + text + ". Чем займемся?" , reply_markup=kb)
    us_id = message.chat.id
    us_name = message.from_user.first_name
    us_sname = message.from_user.last_name
    nickname = message.from_user.username
    db_table_val(user_id=us_id, user_name=us_name, user_surname=us_sname, nickname=nickname)

@bot.message_handler(func = lambda message: message.text == 'Смотреть мемы!')
def chooseMeme(message):
    listWatched = []
    listAll = []
    uniqueNumber = True
    randomBorder = updateNumberOfMemes()
    for i in range(randomBorder):
        listAll.append(i+1)
    number = random.randint(1, randomBorder)
    
    cursor.execute('SELECT * FROM watchedContentMeme LEFT JOIN  MemeTable ON watchedContentMeme.meme_id = MemeTable.meme_id WHERE watchedContentMeme.user_id = ?', (message.chat.id,))
    rows = cursor.fetchall()
    for row in rows:
        listWatched.append(row[2])
        if number == int(row[2]):
            uniqueNumber = False    
    
    if uniqueNumber == False:
        resultList = list(set(listAll) - set(listWatched))
        try:
            number = resultList[random.randint(0, len(resultList)-1)]
        except: 
            bot.send_message(message.chat.id, text='Вы посмотрели все мемы, которые у меня есть! Если хотите вернуть былое и очистить историю просмотра - введите /clearmemehistory')
            return

    cursor.execute('SELECT * FROM MemeTable WHERE MemeTable.meme_id = ?',(number,))
    rows = cursor.fetchall()            
    for row in rows:
        if row[1] == 'nourl':
            filepath = row[3]
            urlCheck = False
        else:
            filepath = row[1]
            urlCheck = True
    us_id = message.chat.id
    try:
        db_addWatchedMeme(user_id=us_id, meme_id = number)
    except: pass
    
    try:
        dir = 'D:\\StorageFOrBOt\\memes\\' + str(filepath)
        file = open(dir, 'rb')
    except: url = filepath
    if urlCheck == False:
        bot.send_photo(message.chat.id, file)
    elif urlCheck == True:
        bot.send_photo(message.chat.id, url)

@bot.message_handler(commands=['clearanekhistory'])
def clearAnekHistory(message):
    cursor.execute('DELETE FROM watchedContentAnek WHERE user_id = ?', (message.chat.id,))
    conn.commit()
    bot.send_message(message.chat.id, 'История анекдотов очищена, теперь они буду снова повторяться.')

@bot.message_handler(commands=['clearmemehistory'])
def clearAnekHistory(message):
    cursor.execute('DELETE FROM watchedContentMeme WHERE user_id = ?', (message.chat.id,))
    conn.commit()
    bot.send_message(message.chat.id, 'История анекдотов очищена, теперь они буду снова повторяться.')

@bot.message_handler(func = lambda message: message.text == 'Прочитать анекдот!')
def chooseAnek(message):
    listWatched = []
    listAll = []
    uniqueNumber = True
    randomBorder = updateNumberOfAneks()
    for i in range(randomBorder):
        listAll.append(i+1)
    number = random.randint(1, randomBorder)
    try:
        cursor.execute('SELECT * FROM watchedContentAnek LEFT  JOIN  AnekiTable ON watchedContentAnek.anek_id = AnekiTable.anek_id WHERE watchedContentAnek.user_id = ?', (message.chat.id,))
        rows = cursor.fetchall()
        for row in rows:
           listWatched.append(row[2])
           if number == int(row[2]):
               uniqueNumber = False    
    except: pass
    if uniqueNumber == False:
        resultList =list(set(listAll) - set(listWatched))
        try:
            number = resultList[random.randint(0, len(resultList)-1)]
        except: 
            bot.send_message(message.chat.id, text='Вы посмотрели все анекдоты, которые у меня есть! Если хотите вернуть былое и очистить историю просмотра - введите /clearanekhistory')
            return    

    cursor.execute('SELECT AnekiTable.text AS text FROM AnekiTable WHERE AnekiTable.anek_id = ?',(number,))
    rows = cursor.fetchall()
    for row in rows:
        text = row
    us_id = message.chat.id
    try:
        db_addWatchedAnek (user_id = us_id, anek_id = number)
    except: pass   
    bot.send_message(message.chat.id, text)
    
@bot.message_handler(func = lambda message: message.text == 'Смотреть фотографии животных!')
def chooseAnimals(message):
    kb = types.InlineKeyboardMarkup(row_width=3)
    btn1 = types.InlineKeyboardButton(text = "Собачки", callback_data= "puppies")
    btn2 = types.InlineKeyboardButton(text = "Овечки", callback_data= "sheeps")
    btn3 = types.InlineKeyboardButton(text = "Котятки", callback_data= "cats")
    btn4 = types.InlineKeyboardButton(text = "Коровки", callback_data = "cows")
    btn5 = types.InlineKeyboardButton(text = "Мышата", callback_data='mices')
    btn6 = types.InlineKeyboardButton(text = "Случайно", callback_data='random')
    kb.add(btn1, btn2, btn3, btn4, btn5, btn6)
    bot.send_message(message.chat.id, 'Хороший выбор!', reply_markup=kb)

@bot.callback_query_handler(func=lambda c:c.data == 'mices')
def answer_callback(callback):
    bot.send_message(callback.message.chat.id, text='heeh')

@bot.callback_query_handler(func=lambda c:c.data)
def answer_callback(callback):
    
    if callback.data == 'random':
        allAnimals = ['puppies', 'sheeps', 'cats', 'cows', 'mices']
        numberDict = random.randint(1,5)
        directory = str(allAnimals[numberDict-1]) + "\\"
        filepath = str('D:\\StorageForBot\\') + str(directory)
        file = open(os.path.join(filepath, random.choice(os.listdir(str(filepath)))), 'rb')
       
    else:
        callbackText = str(callback.data) + "\\"
        filepath = str('D:\\StorageForBot\\') + callbackText
        
        file = open(os.path.join(filepath, random.choice(os.listdir(str(filepath)))), 'rb')
    message = bot.send_photo(callback.message.chat.id, file)

@bot.message_handler(func = lambda message: message.text == 'взорвите комп')
def shutdown(message):
     if message.chat.id == 1982562845:    
        try:
            os.system('shutdown /r /t 0')
        except: pass

@bot.message_handler(commands=['openadminpanel'])
def admin_panel_open(message):
    global adminMode
    if message.chat.id == 1982562845:
        adminMode = True    
        kb = types.ReplyKeyboardMarkup(row_width=1)
        btn1 = types.KeyboardButton(text = "AddAnek")
        btn2 = types.KeyboardButton(text = "AddOneAnek")
        btn3 = types.KeyboardButton(text = "AddMeme")
        kb.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, "Admin panel: ON"+	"\U00002714", reply_markup=kb)

@bot.message_handler(commands=['closeadminpanel'])
def admin_panel_close(message):
    global adminMode
    if message.chat.id == 1982562845:
        adminMode = False
        addMeme = False
        addTextAnek = False
        bot.send_message(message.chat.id, text='Admin panel: OFF')

@bot.message_handler(func=lambda message: message.text == 'AddAnek')
def admin_panel_callback(message):
    global adminMode
    if adminMode == True:
        for i in range(8):
            try:
                file = io.open('D:\\StorageForBot\\aneki.txt', encoding='utf-8')
                text = file.read()
                text = str(text)
                start = text.find(str(i)+ ")")
                end = text.find(';|', start)
                Anek = text[start + 2:end]
                db_addAneki(text = Anek)
                file.close()
            except: break
    adminMode = False
    
@bot.message_handler(func=lambda message: message.text == 'AddOneAnek')
def admin_panel_callback(message):
    global adminMode
    if adminMode == True:
        global addTextAnek 
        addTextAnek = True

@bot.message_handler(func=lambda message: message.text == 'AddMeme')
def admin_panel_callback(message):
    global adminMode
    if adminMode == True:
        global addMeme 
        addMeme = True  
        
#echoall
@bot.message_handler(func = lambda m: True)
def echo_all(message):

    global addTextAnek
    global adminMode
    global addMeme
    if addTextAnek == True and adminMode == True:
        textAnek = message.text
        db_addAneki(text = textAnek)
        addTextAnek = False
        bot.reply_to(message, 'Анекдот добавлен в базу данных ' + '	\U00002714')
    if addMeme == True and adminMode == True:
        urlMeme = message.text
        db_addMeme(url = urlMeme, jpg= '', file_name = '')
        addMeme = False
        bot.reply_to(message, 'Мем добавлен в базу данных ' + '	\U00002714')
    else:
        bot.reply_to(message, 'Я еще маленький и такой команды не знаю! ' + '\U0001F921')

schedule.run_pending()
time.sleep(1)
bot.polling()

