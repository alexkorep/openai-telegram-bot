import os
from flask import Flask, request
import telebot
import openai
import boto3
import json

TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY")

WEBHOOK_HOST = os.environ.get("WEBHOOK_HOST")
WEBHOOK_URL = "https://{}/{}".format(WEBHOOK_HOST, TELEGRAM_API_KEY)

SQS_QUEUE_NAME = os.environ.get(
    "SQS_QUEUE_NAME"
)  # should be the same as in Zappa settings

bot = telebot.TeleBot(TELEGRAM_API_KEY)
app = Flask(__name__)
sqs = boto3.resource("sqs")


@app.route("/", methods=["GET", "HEAD"])
def index():
    return "OK" if TELEGRAM_API_KEY and WEBHOOK_HOST else "Not OK"


@app.route("/{}".format(TELEGRAM_API_KEY), methods=["POST"])
def telegram_webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    message = update.message
    if not message:
        return "", 200

    chat_dest = message.chat.id
    user_msg = message.text
    user_username = message.from_user.username
    if not is_allowed_username(user_username):
        bot.send_message(chat_dest, "Sorry, you are not allowed to use this bot.")
        return "", 200

    bot.send_chat_action(chat_id=chat_dest, action="typing", timeout=10)

    send_message_to_queue(
        {
            "chat_dest": chat_dest,
            "user_msg": user_msg,
        },
        SQS_QUEUE_NAME,
    )

    return "", 200


def is_allowed_username(username):
    username_list = os.environ.get("ALLOWED_USERNAMES", "").split(",")
    return username in username_list


def send_message_to_queue(msg, queue_name):
    """
    Put a message on the queue
    :param msg: Message object
    :param queue_name: name of sqs quue
    :return: MessageId, MD5 hash of Message body
    """
    # Get the queue. This returns an SQS.Queue instance
    try:
        queue = sqs.get_queue_by_name(QueueName=queue_name)
        msg_txt = json.dumps(msg)
        response = queue.send_message(MessageBody=msg_txt)
        return response.get("MessageId"), response.get("MD5OfMessageBody")
    except Exception as exc:
        print(f"Error sending message to queue: {queue_name}.  Exc: {exc}")


def process_messages(event, context):
    body = json.loads(event["Records"][0]["body"])
    user_msg = body["user_msg"]
    chat_dest = body["chat_dest"]

    openai.api_key = os.environ.get("OPENAI_API_KEY")
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=user_msg,
        temperature=0.7,
        max_tokens=1751,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    text = response.choices[0].text
    bot.send_message(chat_dest, text)

    return "OK"


if TELEGRAM_API_KEY and WEBHOOK_HOST:
    # Set webhook
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
