import telebot
from mysql.connector import connect
import configparser

config = configparser.ConfigParser()
config.read("settings.ini")

bot = telebot.TeleBot(config["tg"]["token"])

connection = connect(user=config["mysql"]["user"], password=config["mysql"]["password"],
                     host='127.0.0.1',
                     database=config["mysql"]["database"])
print(connection)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    print(message.text)
    user = message.from_user.id

    if message.text == "/start":
        bot.send_message(message.from_user.id, "1")

    else:
        select_address = f"SELECT * FROM table_drcd_final WHERE full_address='{message.text}'"
        with connection.cursor() as cursor:
            cursor.execute(select_address)
            result = cursor.fetchall()
            for row in result:
                print(row);
                bot.send_message(message.from_user.id,
                                 f"Мы в гости к {row[0]} в {row[3]} подьезд на {row[5]} этаж в {row[4]} квартиру")
                bot.send_message(message.from_user.id, row[6])


bot.polling(none_stop=True, interval=0)