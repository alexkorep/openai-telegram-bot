# openai-telegram-bot

OpenAI Chat Telegram Bot

## Configuration

### Zappa configuration

Rename `zappa_settings.template.json` to `zappa_settings.json` and update the parameters like
`arn`, `s3_bucket`, `aws_region`.

In order to process the audio messages, you need to add a Lambd layer with the `ffmpeg` binary.
Go to https://serverlessrepo.aws.amazon.com/applications/us-east-1/145266761615/ffmpeg-lambda-layer,
click on `Deploy` and follow the instructions. You will get an ARN like `arn:aws:lambda:us-east-1:123456789101:layer:ffmpeg:1`. Put it to `layers` array in `zappa_settings.json`.

### Bot configuration

1. Obtain Open AI key at https://beta.openai.com/account/api-keys, put it to
   OPENAI_API_KEY environment variable
2. Create a new bot, get its API key and put to
   TELEGRAM_API_KEY environment variable
3. Put comma-separated list of Telegram usernames for people who's
   allowed to use the bot to ALLOWED_USERNAMES environment variable

## Running locally

1. Setup ngrok: `ngrok http 5001`

2. Run the app:

```
export OPENAI_API_KEY=...
export TELEGRAM_API_KEY=...
export ALLOWED_USERNAMES=user1,user2
export WEBHOOK_HOST=<ngrok url>
flask run --host=0.0.0.0 --port 5001
```

## Security considerations

The bot keeps the history of the messages in the plain text in DynamoDB. 
Please make sure your users are aware and are OK with that.