from models.history import clear_history
from models.prompt import save_prompt, get_prompt

def handle_message_prompt(bot, message):
    # Set the prompt in the database
    chat_dest = message.chat.id
    text = message.text
    text = text.replace("/prompt", "").strip()
    print("New prompt:", text)
    if text:
        save_prompt(chat_dest, text)
        clear_history(chat_dest)
        bot.send_message(chat_dest, "The new prompt: " + text)
    else:
        prompt = get_prompt(chat_dest)
        print("The prompt is: ", prompt)
        bot.send_message(chat_dest, "The prompt is: " + prompt)
