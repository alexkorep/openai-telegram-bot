import os
from telebot import TeleBot
import openai

bot = TeleBot(__name__)

def is_allowed_username(username):
    username_list = os.environ.get('ALLOWED_USERNAMES', '').split(',')
    return username in username_list


@bot.route('(?!/).+')
def echo_message(message):
    chat_dest = message['chat']['id']
    user_msg = message['text']
    user_username = message['from']['username']
    print(user_username)
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


if __name__ == '__main__':
    bot.config['api_key'] = os.environ.get('TELEGRAM_API_KEY')
    bot.poll(debug=True)
