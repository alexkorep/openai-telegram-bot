
def handle_message_text(bot, openai, body):
    text = body["text"]
    chat_dest = body["chat_dest"]

    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": text},
        ],
    )
    content = response.choices[0].message.content
    bot.send_message(chat_dest, content)
    return "OK"

