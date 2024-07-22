import telebot
import json
import schedule
import time
import threading
from datetime import date, datetime

tok = '7182262233:AAGZxzFazer_Xu03SkjPMdQT5G1p_IbaQ64'
# Необходимо вставить ID чата, обязательно с тире перед числовым значением
chat_id = '-'

bot = telebot.TeleBot(tok)
dezhurstva_config = {}


def load_config():
    global dezhurstva_config
    with open('dezhurstva_config.json', 'r', encoding='utf-8') as file:
        dezhurstva_config = json.load(file)


load_config()  # Загружаем конфигурацию при старте бота


def send_duty():
    current_date = date.today().strftime("%Y-%m-%d")
    if current_date in dezhurstva_config:
        dezhurny = dezhurstva_config[current_date]['watch']
        message = f"Сегодня дежурный - {dezhurny}"
    else:
        message = "На сегодня дежурный не назначен"
    bot.send_message(chat_id, message)


schedule.every().day.at("09:00").do(send_duty)


@bot.message_handler(commands=['say'])
def send_duty_now(message):
    # load_config()
    current_date = date.today().strftime("%Y-%m-%d")
    if current_date in dezhurstva_config:
        dezhurny = dezhurstva_config[current_date]['watch']
        msg = f"Сегодня дежурный - {dezhurny}"
    else:
        msg = "На сегодня дежурный не назначен"
    bot.send_message(chat_id, msg)


@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.document.mime_type == 'application/json':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Сохраним загруженный файл на сервере
        with open('dezhurstva_config.json', 'wb') as new_file:
            new_file.write(downloaded_file)

        load_config()  # Перезагружаем конфигурацию после загрузки нового файла
        bot.reply_to(message, "Конфигурация успешно обновлена!")
    else:
        bot.reply_to(message, "Пожалуйста, загрузите файл в формате JSON.")


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


threading.Thread(target=run_scheduler, daemon=True).start()

bot.polling()