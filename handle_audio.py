import tempfile
import subprocess


def handle_message_audio_or_voice(bot, openai, body):
    file_id = body["file_id"]
    file_url = bot.get_file_url(file_id)
    chat_dest = body["chat_dest"]

    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate a temporary file name in the temporary directory
        temp_file = tempfile.NamedTemporaryFile(
            dir=temp_dir, delete=False, suffix=".mp3"
        )
        # Get the name of the temporary file
        temp_file_name = temp_file.name
        print("temp_file_name", temp_file_name)

        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    file_url,
                    "-vn",
                    "-y",
                    "-ar",
                    "44100",
                    "-ac",
                    "2",
                    "-b:a",
                    "192k",
                    temp_file_name,
                ]
            )
        except Exception as exc:
            print(f"Error converting audio file: {exc}")
            bot.send_message(chat_dest, "Error converting audio file")
            return ""

        audio_file = open(temp_file_name, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        print("transcript: ", transcript["text"])
        bot.send_message(chat_dest, transcript["text"])

    # with urllib.request.urlopen(file_url) as response:
    #     with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
    #         tmp_file.write(response.read())
    #         segment = AudioSegment.from_file(tmp_file.name)
    #         with tempfile.NamedTemporaryFile(delete=False) as tmp_file_dest:
    #             segment.export(tmp_file_dest.name, format='wav')
    #             audio_file = open(tmp_file_dest.name, "rb")

    #             transcript = openai.Audio.transcribe("whisper-1", audio_file)
    #             print('transcript: ', transcript)
    #             bot.send_message(chat_dest, transcript)
    return "OK"