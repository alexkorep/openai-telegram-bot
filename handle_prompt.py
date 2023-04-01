from models.history import clear_history
from models.prompt import save_prompt, get_prompt, delete_prompt

def handle_message_prompt(bot, message):
    # Set the prompt in the database
    chat_dest = message.chat.id
    text = message.text
    text = text.replace("/prompt", "").strip()
    if text:
        save_prompt(chat_dest, text)
        clear_history(chat_dest)
        bot.send_message(chat_dest, "The new prompt: " + text)
    else:
        prompt = get_prompt(chat_dest)
        bot.send_message(chat_dest, "The prompt is: " + prompt)

def handle_message_prompt_delete(bot, message):
    # Delete the prompt from the database
    chat_dest = message.chat.id
    delete_prompt(chat_dest)
    bot.send_message(chat_dest, "The prompt has been deleted.")