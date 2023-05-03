import telebot
from mysql.connector import connect
import configparser

config = configparser.ConfigParser()
config.read("settings.ini")

bot = telebot.TeleBot(config["tg"]["token"])

connection = connect(user=config["mysql"]["username"], password=config["mysql"]["password"],
                     host='127.0.0.1',
                     database=config["mysql"]["database"])
print(connection)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    print(message.text)
    user = message.from_user.id

    if message.text == "/start":
        check_user = f"SELECT * FROM roof_users WHERE tgid='{user}'"
        with connection.cursor() as cursor:
            cursor.execute(check_user)
            result = cursor.fetchall()
            if result == []:
                create_user = f"INSERT INTO roof_users VALUES ('{user}', 50, 0)"
                with connection.cursor() as cursor:
                    cursor.execute(create_user)
                    connection.commit()
                bot.send_message(message.from_user.id, "Welcome")
            else:
                bot.send_message(message.from_user.id, "Already on")



    elif message.text == "/info":
        check_account = f"SELECT money FROM roof_users WHERE tgid='{user}'"
        with connection.cursor() as cursor:
            cursor.execute(check_account)
            result = cursor.fetchall()
            bot.send_message(message.from_user.id, f"Ваш баланс: {result[0][0]} рублей")

    else:
        check_account = f"SELECT money FROM roof_users WHERE tgid='{user}'"
        with connection.cursor() as cursor:
            cursor.execute(check_account)
            result = cursor.fetchall()
            if result[0][0] >= 5:
                select_address = f"SELECT * FROM table_drcd_final WHERE full_address='{message.text}'"
                with connection.cursor() as cursor:
                    cursor.execute(select_address)
                    result = cursor.fetchall()
                    if result != []:
                        for row in result:
                            print(row);
                            bot.send_message(message.from_user.id,
                                             f"Мы в гости к {row[0]} в {row[3]} подьезд на {row[5]} этаж в {row[4]} квартиру")
                            bot.send_message(message.from_user.id, row[6])
                        update_account = f"UPDATE roof_users SET money = money - 5 WHERE tgid = '{user}'"
                        with connection.cursor() as cursor:
                            cursor.execute(update_account)
                            connection.commit()
                    else:
                        bot.send_message(message.from_user.id, "Мы не смогли найти этот адрес")
            else:
                bot.send_message(message.from_user.id, "Пополните баланс")


bot.polling(none_stop=True, interval=0)
