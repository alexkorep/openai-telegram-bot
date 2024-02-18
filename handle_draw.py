from models.history import save_history

# Constants for DALL·E
DALLE_MODEL = "dalle-mini"

def generate_image_prompt(text):
    """Prepare the image generation prompt from the user's text request."""
    # Basic preprocessing or prompt engineering can be done here
    return text  # This can be more sophisticated based on the input

def call_dalle_api(openai, prompt):
    """Call the DALL·E API to generate an image based on the prompt."""
    try:
        response = openai.Image.create(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        return response
    except Exception as e:
        print(f"Error calling DALL·E API: {e}")
        return None

def handle_draw_request(bot, openai, body):
    text = body["text"]
    chat_dest = body["chat_dest"]
    text = text.replace("/draw", "").strip()
    
    # Generate the prompt for image creation
    prompt = generate_image_prompt(text)
    bot.send_message(chat_dest, f"Drawing {prompt}")
    
    # Call DALL·E API with the generated prompt
    response = call_dalle_api(openai, prompt)
    
    if response and response.data:
        # Assuming response.data contains the URL or data of the generated image
        image_url = response.data[0].url
        bot.send_message(chat_dest, image_url)
        return "OK"
    else:
        error_message = "Failed to generate image."
        bot.send_message(chat_dest, error_message)
        save_history(chat_dest, text, True)
        save_history(chat_dest, error_message, False)
        return "Error"
