import telebot
from DB import DB
import configparser
from datetime import datetime
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
    user_tgid = message.from_user.id
    user_request = message.text
    user_response = ""
    user_sql = ""
    now = datetime.now()
    user_datetime = now.strftime("%d/%m/%Y %H:%M:%S")
    user_money = DB().execute(f"SELECT money FROM roof_users WHERE tgid='{user_tgid}'")[0][0]

    if message.text == "/start":
        result = DB().execute(f"SELECT * FROM roof_users WHERE tgid='{user_tgid}'")
        if not result:
            DB().execute(f"INSERT INTO roof_users VALUES ('{user_tgid}', 50, 0)")
            user_response = "Добро пожаловать, вам начислено 50 бонусных рублей"
            bot.send_message(message.from_user.id, user_response)
        else:
            user_response = "Вы уже зарегистрированы"
            bot.send_message(message.from_user.id, user_response)

    elif message.text == "/info":
        result = DB().execute(f"SELECT money FROM roof_users WHERE tgid='{user_tgid}'")
        user_response = f"Ваш баланс: {result[0][0]} рублей"
        bot.send_message(message.from_user.id, user_response)

    elif message.text == "/pay":
        bot.send_invoice(chat_id=user_tgid, title="Пополнение баланса бота", description='Пополним баланс на 100 рублей',
                         invoice_payload=user_tgid,
                         provider_token=config["tg"]["pay_token"], currency="RUB",
                         prices=[LabeledPrice(label='100 рублей', amount=100 * 100)], start_parameter="bot_pay")

    else:
        if user_money >= 5:
            input_text = message.text
            user_sql = f"SELECT * FROM table_drcd_final WHERE full_address='{input_text.replace(',', '')}'"
            address = DB().execute(user_sql)
            if address:
                if len(address) < 10:
                    for row in address:
                        bot.send_message(message.from_user.id,
                                         f"Мы в гости к {row[0]} в {row[3]} подьезд на {row[5]} этаж в {row[4]} квартиру. {row[6]}")
                else:
                    for i in range(10):
                        bot.send_message(message.from_user.id,
                                         f"Мы в гости к {address[i][0]} в {address[i][3]} подьезд на {address[i][5]} этаж в {address[i][4]} квартиру. {address[i][6]}")
                DB().execute(f"UPDATE roof_users SET money = money - 5 WHERE tgid = '{user_tgid}'")
            else:
                user_response = "Мы не смогли найти этот адрес, для поиска - копируйте адрес с яндекс карт, тогда бот обязательно найдет :) Так же бот работает только по Москве"
                bot.send_message(message.from_user.id, user_response)

        else:
            user_response = "Пополните баланс"
            bot.send_message(message.from_user.id, user_response)
    print(f"INSERT INTO logs VALUES ('{user_tgid}', '{user_datetime}', '{user_money}', '{user_request}', '{user_response}', '{user_sql}')")
    DB().execute(f"INSERT INTO logs VALUES ('{user_tgid}', '{user_datetime}', '{user_money}', '{user_request}', '{user_response}', \"{user_sql}\")")

bot.polling(none_stop=True, interval=0)
