import os
import openai
import whisper
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Set up OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# Set up Telegram Bot API Token from environment variable
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')

# Load Whisper model for transcription
whisper_model = whisper.load_model("base")  # You can use "small", "medium", etc. based on your needs

# Remove only "um" and "uh" as filler words
def remove_filler_words(text):
    filler_words = ['um', 'uh']
    words = text.split()
    cleaned_words = [word for word in words if word.lower() not in filler_words]
    return " ".join(cleaned_words)

# Function to improve the clarity of the text using OpenAI
def improve_text(text):
    prompt = f"Rephrase the following text to make it clearer and more understandable while keeping the same meaning: '{text}'"
    
    response = openai.Completion.create(
        model="text-davinci-003",  # You can use gpt-4 or the latest model
        prompt=prompt,
        max_tokens=200,
        temperature=0.7,
    )
    
    return response.choices[0].text.strip()

# Function to handle voice messages
def handle_voice(update: Update, context: CallbackContext):
    # Get the voice file from the message
    voice_file = update.message.voice.get_file()
    file_path = voice_file.download()

    # Transcribe the audio using Whisper
    result = whisper_model.transcribe(file_path)
    transcription = result['text']

    # Clean up the transcription by removing only "um" and "uh"
    cleaned_text = remove_filler_words(transcription)

    # Improve the text to make it clearer using OpenAI while maintaining the meaning
    improved_text = improve_text(cleaned_text)

    # Send the improved transcription back to the user
    update.message.reply_text(improved_text)

# Function to start the bot
def start(update: Update, context: CallbackContext):
    update.message.reply_text('Send me a voice memo, and I will transcribe and clean it up for you!')

# Main function to start the bot
def main():
    # Set up the updater with your bot's token
    updater = Updater(TELEGRAM_API_TOKEN, use_context=True)

    dp = updater.dispatcher

    # Start command handler
    dp.add_handler(CommandHandler("start", start))

    # Voice message handler
    dp.add_handler(MessageHandler(Filters.voice, handle_voice))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
