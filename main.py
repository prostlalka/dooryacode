import telebot
import DB
import configparser
from telebot.types import LabeledPrice

config = configparser.ConfigParser()
config.read("settings.ini")

bot = telebot.TeleBot(config["tg"]["token"])


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Оплата не прошла - попробуйте, пожалуйста, еще раз,"
                                                "или свяжитесь с администратором бота.")


# при корректной оплате
@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):

    # здесь подключение к базе данных и внесение данных в таблицу
    bot.send_message(message.chat.id, 'Ваш заказ был успешным❤')
    DB().execute(f"UPDATE roof_users SET money = money + 100 WHERE tgid = '{message.chat.id}'")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    print(message.text)
    user = message.from_user.id

    if message.text == "/start":
        result = DB().execute(f"SELECT * FROM roof_users WHERE tgid='{user}'")
        if result == []:
            DB().execute(f"INSERT INTO roof_users VALUES ('{user}', 50, 0)")
            bot.send_message(message.from_user.id, "Welcome")
        else:
            bot.send_message(message.from_user.id, "Already on")



    elif message.text == "/info":
        result = DB.execute(f"SELECT money FROM roof_users WHERE tgid='{user}'")
        bot.send_message(message.from_user.id, f"Ваш баланс: {result[0][0]} рублей")
    elif message.text == "/pay":
        bot.send_invoice(chat_id=user, title="Пополнение баланса бота", description='Пополним баланс на 100 рублей',
                         invoice_payload=user,
                         provider_token=config["tg"]["pay_token"], currency="RUB",
                         prices=[LabeledPrice(label='100 рублей', amount=100*100)], start_parameter="bot_pay")

    else:
        money = DB().execute(f"SELECT money FROM roof_users WHERE tgid='{user}'")
        if money[0][0] >= 5:
            address = DB().execute(f"SELECT * FROM table_drcd_final WHERE full_address='{message.text}'")
            if address != []:
                for row in address:
                    print(row);
                    bot.send_message(message.from_user.id,
                                     f"Мы в гости к {row[0]} в {row[3]} подьезд на {row[5]} этаж в {row[4]} квартиру")
                    bot.send_message(message.from_user.id, row[6])
                DB().execute(f"UPDATE roof_users SET money = money - 5 WHERE tgid = '{user}'")
            else:
                bot.send_message(message.from_user.id, "Мы не смогли найти этот адрес")
        else:
            bot.send_message(message.from_user.id, "Пополните баланс")


bot.polling(none_stop=True, interval=0)
