# openai-telegram-bot

OpenAI Chat Telegram Bot

# Configuration

1. Obtain Open AI key at https://beta.openai.com/account/api-keys, put it to
   OPENAI_API_KEY environment variable
2. Create a new bot, get its API key and put to
   TELEGRAM_API_KEY environment variable
3. Put comma-separated list of Telegram usernames for people who's
   allowed to use the bot to ALLOWED_USERNAMES environment variable

# Running locally

1. Setup ngrok: `ngrok http 5001`

2. Run the app:

```
export OPENAI_API_KEY=...
export TELEGRAM_API_KEY=...
export ALLOWED_USERNAMES=user1,user2
export WEBHOOK_HOST=<ngrok url>
flask run --host=0.0.0.0 --port 5001
```
