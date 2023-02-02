import telebot
from telebot import types
import time
import sqlite3
import asyncio


#chislitznam = 'Числитель' #ИЗМЕНИТЬ ЭТУ ПАРАШУ

bot = telebot.TeleBot('5654743331:AAGg14yIENs3F3c47AjCtNGcKcEF5wkakgM')

messageFromMe = ''

with sqlite3.connect('.\\Vedomost.db', check_same_thread=False) as db:
    cur = db.cursor()
    cur.execute(" CREATE TABLE IF NOT EXISTS Vedomost\
        (user_id INTEGER, one INTEGER, two INTEGER, three INTEGER,\
         four INTEGER, five INTEGER, six INTEGER, seven INTEGER,\
          eight INTEGER, nine INTEGER, ten INTEGER)")
    db.commit()

#############################кнопки#############################
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.add(types.KeyboardButton("Расчет ведомости"))
#markup.add(types.KeyboardButton("Расписание преподавателей"))
markup.add(types.KeyboardButton("Расписание звонков"))
#markup.add(types.KeyboardButton("Расписание студентов"))
markup.add(types.KeyboardButton('Сообщение разработчикам'))
################################################################

################################################################
###########################START################################
@bot.message_handler(commands=['start'])
def start(message):

    print("new session test")
    messageChatId = int(message.chat.id)
    print(f"user_id: {messageChatId}")

    with sqlite3.connect('.\\Vedomost.db') as db:
        cur = db.cursor()
        cur.execute("SELECT user_id FROM Vedomost WHERE user_id LIKE ?", (messageChatId,))
        check = cur.fetchone()
        if check == None:
            cur.execute("INSERT INTO Vedomost VALUES(?,?,?,?,?,?,?,?,?,?,?)",(messageChatId,0,0,0,0,0,0,0,0,0,0))
            print("create new user line\n")
        elif check != None:
            cur.execute("UPDATE Vedomost SET one=?, two=?, three=?, four=?, five=?, six=?, seven=?, eight=?, nine=?, ten=?, user_id=?\
             WHERE user_id = ?", (0,0,0,0,0,0,0,0,0,0, messageChatId, messageChatId,))
            print("edit old user line\n")
        else:
            print("Ошибка")
        db.commit()
    start = bot.send_message(message.chat.id, 'Если я вдруг сломался, нажмите: /start',reply_markup=markup)
    bot.register_next_step_handler(start, main)

    # СДЕЛАТЬ РЕГИСТРАЦИЮ CHAT_ID В БД

#Распредкоробка
@bot.message_handler(content_types=['text'])
def main(message):

    if message.text == "Расчет ведомости":
        main1 = bot.send_message(message.chat.id, \
            'Напиши мне количество аттестованных студентов в группе.',reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(main1, vedomost)


    elif message.text == 'Расписание звонков':
        bot.send_message(message.chat.id, 'Расписание звонков:')
        bot.send_photo(message.chat.id, 'https://imgur.com/a/HmkrVEK')

    elif message.text == 'Сообщение разработчикам':

        main2 = bot.send_message(message.chat.id, \
            'Напиши мне сообщение с пожеланием, замечанием :)(Только текст) ', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(main2, feedback)

    elif message.text == 'mes':

        main3 = bot.send_message(message.chat.id, 'Введи id пользователя')
        bot.register_next_step_handler(main3, messageForUser)

    elif message.text == "mesall":
        
        main4 = bot.send_message(message.chat.id, "Какое сообщение вы хотите отправить?")
        bot.register_next_step_handler(main4, messageall)
    
    else:
        main5 = bot.send_message(message.chat.id, 'Следуйте по кнопкам!', reply_markup=markup)
        bot.register_next_step_handler(main5, main)

def messageall(message):
    if message.text != None:
        with sqlite3.connect('.\\Vedomost.db') as db:
            cur = db.cursor()
            cur.execute("SELECT user_id FROM Vedomost ")
            for userId in cur.execute("SELECT user_id FROM Vedomost "):
                print(f"select user: {userId[0]}")
                bot.send_message(userId[0], message.text)
        messageall1 = bot.send_message(message.chat.id, "сообщение успешно отправленно!")
        bot.register_next_step_handler(messageall1, main)
    else:
        messageall2 = bot.send_message(message.chat.id, "Сообщение пустое")
        bot.register_next_step_handler(messageall2, main)


#Отправка сообщений пользователю
def messageForUser(message):

    global messageFromMe
    messageFromMe = (message.text)
    forme = bot.send_message(message.chat.id, 'Введи сообщение для пользователя')
    bot.register_next_step_handler(forme, messageForMe)


def messageForMe(message):

    global messageFromMe
    message = (message.text)
    bot.send_message(messageFromMe, ('Сообщение от администратора: ' + message))
    bot.send_message(message.chat.id, 'Сообщение отправлено :)')

#Обратная связь
def feedback(message):

    bot.send_message(716599711, "user_id: " + str(message.chat.id)\
     + ' ' + "\nuser_name: "+ message.chat.username + '\nuser_message: ' + message.text)
    bot.send_message(1010471042, "user_id: " + str(message.chat.id)\
     + ' ' + "user_name: "+ message.chat.username + '\nuser_message: ' + message.text)
    feedback = bot.send_message(message.chat.id, 'Ваше сообщение принято 😊', reply_markup=markup)
    bot.register_next_step_handler(feedback, main)
#########################VEDOMOST#######################################

def vedomost(message):
    messageChatId = int(message.chat.id)

    if message.text == "0":
        vedomost1 = bot.send_message(message.chat.id, 'Данное значение не может быть равно нулю')
        bot.register_next_step_handler(vedomost1, vedomost)

    elif message.text.isdigit():

        with sqlite3.connect('.\\Vedomost.db') as db:
            cur = db.cursor()
            cur.execute("UPDATE Vedomost SET one=? WHERE user_id = ?", (message.text, messageChatId,))
            db.commit()

        vedomost2 = bot.send_message(message.chat.id, 'Напиши мне количество студентов в группе.')
        bot.register_next_step_handler(vedomost2, nomber_two)

    elif message.text.isalpha():

        vedomost3 = bot.send_message(message.chat.id, 'Введите число!')
        bot.register_next_step_handler(vedomost3, vedomost)
    else:
        vedomost4 = bot.send_message(message.chat.id, 'Произошла ошибка')
        bot.register_next_step_handler(vedomost4, main)


def nomber_two(message):
    messageChatId = int(message.chat.id)

    if message.text == "0":
        send = bot.send_message(message.chat.id, 'Данное значение не может быть равно нулю')
        bot.register_next_step_handler(send, nomber_two)

    elif message.text.isdigit():

        with sqlite3.connect('.\\Vedomost.db') as db:
            cur = db.cursor()
            cur.execute("UPDATE Vedomost SET two=? WHERE user_id = ?", (message.text, messageChatId,))
            db.commit()

        number = bot.send_message(message.chat.id, 'Напиши мне количество рабочих дней включая субботу.')
        bot.register_next_step_handler(number, nomber_three)

    elif message.text.isalpha():

        number1 = bot.send_message(message.chat.id, 'Введите число!')
        bot.register_next_step_handler(number1, nomber_two)
    else:
        number2 = bot.send_message(message.chat.id, 'Произошла ошибка')
        bot.register_next_step_handler(number2, main)


def nomber_three(message):
    messageChatId = int(message.chat.id)

    if message.text == "0":
        three = bot.send_message(message.chat.id, 'Данное значение не может быть равно нулю')
        bot.register_next_step_handler(three, nomber_three)
    elif message.text.isdigit():

        with sqlite3.connect('.\\Vedomost.db') as db:
            cur = db.cursor()
            cur.execute("UPDATE Vedomost SET three=? WHERE user_id = ?", (message.text, messageChatId,))
            db.commit()

        three1 = bot.send_message(message.chat.id, 'Напиши мне всего часов пропусков занятий.')
        bot.register_next_step_handler(three1, nomber_four)

    elif message.text.isalpha():

        three2 = bot.send_message(message.chat.id, 'Введите число!')
        bot.register_next_step_handler(three2, nomber_three)
    else:
        bot.send_message(message.chat.id, 'Произошла ошибка')


def nomber_four(message):
    messageChatId = int(message.chat.id)

    if message.text.isdigit():

        with sqlite3.connect('.\\Vedomost.db') as db:
            cur = db.cursor()
            cur.execute("UPDATE Vedomost SET four=? WHERE user_id = ?", (message.text, messageChatId,))
            db.commit()

        four = bot.send_message(message.chat.id,'Напиши мне количество часов пропусков без уважительной причины.')
        bot.register_next_step_handler(four, nomber_five)

    elif message.text.isalpha():
        four1 = bot.send_message(message.chat.id, 'Введите число!')
        bot.register_next_step_handler(four1, nomber_four)

    else:
        bot.send_message(message.chat.id, 'Произошла ошибка')


def nomber_five(message):
    messageChatId = int(message.chat.id)

    if message.text.isdigit():

        with sqlite3.connect('.\\Vedomost.db') as db:
            cur = db.cursor()
            cur.execute("UPDATE Vedomost SET five=? WHERE user_id = ?", (message.text, messageChatId,))
            db.commit()

        five = bot.send_message(message.chat.id,'Напиши мне количество студентов аттестованных на оценки четыре и пять.')
        bot.register_next_step_handler(five, otvet)

    elif message.text.isalpha():
        five1 = bot.send_message(message.chat.id, 'Введите число!')
        bot.register_next_step_handler(five1, nomber_five)

    else:
        bot.send_message(message.chat.id, 'Произошла ошибка')


def otvet(message):
    messageChatId = int(message.chat.id)

    if message.text.isdigit():
        with sqlite3.connect('.\\Vedomost.db') as db:
            cur = db.cursor()
            cur.execute("UPDATE Vedomost SET six=? WHERE user_id = ?", (message.text, messageChatId,))
            cur.execute("SELECT one, two, three, four, five, six FROM Vedomost WHERE user_id = ?", (messageChatId,))
            check = cur.fetchall()
            newcheck = list(check[0])

        db.commit()
        bot.send_message(message.chat.id, 'Расчет ведомости...')

        a = round((newcheck[0] * 100) / newcheck[1], 2)
        newcheck.append(a)
        b = round((newcheck[1] * 6 * newcheck[2]), 2)
        newcheck.append(b)
        s = round(100 - ((newcheck[3] * 100) / newcheck[7]), 2)
        newcheck.append(s)
        d = round((newcheck[4] * 100) / newcheck[7], 2)
        newcheck.append(d)
        e = round((newcheck[5] * 100) / newcheck[1], 2)
        newcheck.append(e)


        bot.send_message(message.chat.id,\
         f"Процент качесва: {e}\nПроцент посещаемости: {s}\nПроцент прогулов: {d}\nПроцент успеваемости: {a}\nФУВ: {b}")

        otvet = bot.send_message(message.chat.id,'Что-нибудь еще?', reply_markup=markup)
        bot.register_next_step_handler(otvet, main)

    elif message.text.isalpha():
        otvet1 = bot.send_message(message.chat.id, 'Введите число!')
        bot.register_next_step_handler(otvet1, otvet)

    else:
        otvet2 = bot.send_message(message.chat.id, 'Произошла ошибка')
        bot.register_next_step_handler(otvet2, main)


################STARTING################
async def startpoling():

    try:
        print("started")
        bot.polling(non_stop=True)
    except Exception as exept:
        print("!!!crashed!!!")
        print(exept)
        sleep(15)
    finally:
        print("stopped")
        bot.stop_polling()


if __name__ == "__main__":
    asyncio.run(startpoling())
