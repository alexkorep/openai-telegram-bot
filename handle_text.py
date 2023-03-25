from history import get_history, save_history
import tiktoken
import json

# Number of messages to pass to OpenAI (if it fits in the token limit)
HISTORY_LEN = 128
# Model to use
MODEL_NAME = "gpt-3.5-turbo"
# Token limit for the model
MODEL_TOKEN_LIMIT = 4096
# How many tokens we reserve for the history. That means that
# the model response will be cut to MODEL_TOKEN_LIMIT - MODEL_HISTORY_LIMIT tokens.
MODEL_HISTORY_LIMIT = MODEL_TOKEN_LIMIT/2

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
  """Returns the number of tokens used by a list of messages."""
  try:
      encoding = tiktoken.encoding_for_model(model)
  except KeyError:
      encoding = tiktoken.get_encoding("cl100k_base")
  if model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
      num_tokens = 0
      for message in messages:
          num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
          for key, value in message.items():
              num_tokens += len(encoding.encode(value))
              if key == "name":  # if there's a name, the role is omitted
                  num_tokens += -1  # role is always required and always 1 token
      num_tokens += 2  # every reply is primed with <im_start>assistant
      return num_tokens
  else:
      raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
  See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

def make_history(chat_dest, text):
    messages = []
    history = get_history(chat_dest, HISTORY_LEN)

    # Messages are in reverse order, so add the current message first
    messages.append({"role": "user", "content": text})
    print('history', history)
    # The history in reverse order so that the most recent message is first
    for message in history:
        if message["is_user"]:
            role = "user"
        else:
            role = "assistant"
        messages.append({"role": role, "content": message["message"]})
        tokens = num_tokens_from_messages(messages)
        if tokens > MODEL_TOKEN_LIMIT - MODEL_HISTORY_LIMIT:
            # Remove the last message if it puts us over the limit
            messages.pop()
            break
    return messages[::-1]

def handle_message_text(bot, openai, body):
    text = body["text"]
    chat_dest = body["chat_dest"]
    messages = make_history(chat_dest, text)
    print('messages', messages)
    
    response = openai.ChatCompletion.create(
        model=MODEL_NAME,
        messages=messages,
    )
    content = response.choices[0].message.content
    bot.send_message(chat_dest, content)

    # TODO rename, maybe make a single call
    save_history(chat_dest, text, True)
    save_history(chat_dest, content, False)

    return "OK"
