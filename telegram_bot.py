import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# FastAPI endpoint URL
FASTAPI_URL = "https://saeedzou-nemo-asr.hf.space/transcribe"

# Telegram bot token (replace with your bot token)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Send me an audio file, and I'll transcribe it for you!")

def transcribe_audio(update: Update, context: CallbackContext):
    audio_file = update.message.voice.get_file()
    audio_path = "temp_audio.ogg"
    audio_file.download(audio_path)

    with open(audio_path, "rb") as file:
        response = requests.post(FASTAPI_URL, files={"file": file})

    if response.status_code == 200:
        transcription = response.json().get("transcription", "No transcription found.")
        update.message.reply_text(f"Transcription: {transcription}")
    else:
        update.message.reply_text("Error transcribing the audio.")

    os.remove(audio_path)

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.voice, transcribe_audio))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
