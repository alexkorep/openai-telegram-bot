import os
from flask import Flask, request, abort
import telebot
import boto3
import json
from dotenv import load_dotenv
import openai

from handle_audio import handle_message_audio_or_voice
from handle_text import handle_message_text

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")

TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY")

WEBHOOK_HOST = os.environ.get("WEBHOOK_HOST")
WEBHOOK_URL = "https://{}/{}".format(WEBHOOK_HOST, TELEGRAM_API_KEY)

SQS_QUEUE_NAME = os.environ.get(
    "SQS_QUEUE_NAME"
)  # should be the same as in Zappa settings
USE_SQS = os.environ.get("USE_SQS", "True").lower() == "true"

bot = telebot.TeleBot(TELEGRAM_API_KEY, threaded=False)
app = Flask(__name__)
sqs = boto3.resource("sqs")


@app.route("/", methods=["GET", "HEAD"])
def index():
    return "OK" if TELEGRAM_API_KEY and WEBHOOK_HOST else "Not OK"


@app.route("/{}".format(TELEGRAM_API_KEY), methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ""
    else:
        abort(403)


@bot.message_handler(content_types=["text", "audio", "voice"])
def handle_text(message):
    # print("message: ", message)
    chat_dest = message.chat.id
    content_type = message.content_type
    user_username = message.from_user.username
    if not is_allowed_username(user_username):
        bot.send_message(chat_dest, "Sorry, you are not allowed to use this bot.")
        return "", 200

    bot.send_chat_action(chat_id=chat_dest, action="typing", timeout=10)

    body = {
        "content_type": content_type,
        "chat_dest": chat_dest,
    }
    if content_type == "text":
        body["text"] = message.text
    if content_type == "audio":
        body["file_id"] = message.audio.file_id
    elif content_type == "voice":
        body["file_id"] = message.voice.file_id

    if USE_SQS:
        send_message_to_queue(body, SQS_QUEUE_NAME)
    else:
        handle_message(body)

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
    for record in event["Records"]:
        body = json.loads(record["body"])
        handle_message(body)


def handle_message(body):
    content_type = body["content_type"]
    if content_type == "text":
        handle_message_text(bot, openai, body)
    elif content_type == "audio" or content_type == "voice":
        handle_message_audio_or_voice(bot, openai, body)



if TELEGRAM_API_KEY and WEBHOOK_HOST:
    # Set webhook
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
