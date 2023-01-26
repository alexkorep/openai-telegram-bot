import os
from flask import Flask, request, abort
import telebot
import openai


TELEGRAM_API_KEY = os.environ.get('TELEGRAM_API_KEY')

WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST')

bot = telebot.TeleBot(TELEGRAM_API_KEY)
app = Flask(__name__)


@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'OK' if TELEGRAM_API_KEY and WEBHOOK_HOST else 'Not OK'


@app.route('/{}'.format(TELEGRAM_API_KEY), methods=["POST"])
def telegram_webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "", 200

def is_allowed_username(username):
    username_list = os.environ.get('ALLOWED_USERNAMES', '').split(',')
    return username in username_list

@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    chat_dest = message.chat.id
    user_msg = message.text
    user_username = message.from_user.username
    if not is_allowed_username(user_username):
        bot.send_message(chat_dest, 'Sorry, you are not allowed to use this bot.')
        return

    openai.api_key = os.environ.get('OPENAI_API_KEY')
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=user_msg,
        temperature=0.7,
        max_tokens=1751,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    text = response.choices[0].text
    bot.send_message(chat_dest, text)

if TELEGRAM_API_KEY and WEBHOOK_HOST:
    # Set webhook
    bot.remove_webhook()
    bot.set_webhook(url='https://{}/{}'.format(WEBHOOK_HOST, TELEGRAM_API_KEY))
