import os
import requests
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# FastAPI endpoint URL
FASTAPI_URL = "https://saeedzou-nemo-asr.hf.space/transcribe"

# Telegram bot token (replace with your bot token)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def start(update: Update, context: CallbackContext):
    logger.info("Received /start command from user %s", update.effective_user.id)
    # Add a menu with options
    menu = [["Help", "About"]]
    reply_markup = ReplyKeyboardMarkup(menu, resize_keyboard=True)
    update.message.reply_text(
        "👋 Welcome! Send me an audio file, and I'll transcribe it for you!",
        reply_markup=reply_markup,
    )

def help_command(update: Update, context: CallbackContext):
    logger.info("Received /help command from user %s", update.effective_user.id)
    update.message.reply_text(
        "📖 *Help Menu*\n\n"
        "1. Send me an audio file in any format (e.g., mp3, wav, flac).\n"
        "2. I'll transcribe it and send you the text.\n\n"
        "Use the menu below for more options.",
        parse_mode="Markdown",
    )

def about_command(update: Update, context: CallbackContext):
    logger.info("Received /about command from user %s", update.effective_user.id)
    update.message.reply_text(
        "🤖 *About This Bot*\n\n"
        "This app is created under the supervision of FAIM Lab, Sharif University of Technology. "
        "This is the NeMo ASR Hybrid Large fine-tuned from the English version. "
        "It is trained on more than 800 hours of audio (Common Voice, YouTube, Naslemana, in-house datasets).\n\n"
        "For more information, email at saeedzou2012@gmail.com.",
        parse_mode="Markdown",
    )

def transcribe_audio(update: Update, context: CallbackContext):
    logger.info("Received audio file from user %s", update.effective_user.id)
    # Handle all audio file types
    audio_file = None

    if update.message.audio:
        audio_file = update.message.audio.get_file()
    elif update.message.voice:
        audio_file = update.message.voice.get_file()
    elif update.message.document and update.message.document.file_name.lower().endswith(('.mp3', '.wav', '.ogg')):
        audio_file = update.message.document.get_file()

    if not audio_file:
        logger.warning("No valid audio file received from user %s", update.effective_user.id)
        update.message.reply_text("❌ Please send a valid audio file.")
        return

    file_extension = audio_file.file_path.split('.')[-1].lower()
    audio_path = f"temp_audio.{file_extension}"
    audio_file.download(audio_path)

    try:
        with open(audio_path, "rb") as file:
            response = requests.post(FASTAPI_URL, files={"file": file})
        if response.status_code == 200:
            transcription = response.json().get("transcription", "No transcription found.")
            logger.info("Transcription successful for user %s", update.effective_user.id)
            update.message.reply_text(f"📝 *Transcription:*\n\n{transcription}", parse_mode="Markdown")
        else:
            logger.error("Error transcribing audio for user %s: %s", update.effective_user.id, response.text)
            update.message.reply_text("❌ Error transcribing the audio.")
    except Exception as e:
        logger.exception("Exception occurred while processing audio for user %s", update.effective_user.id)
    finally:
        os.remove(audio_path)
        logger.info("Temporary audio file deleted for user %s", update.effective_user.id)

def handle_menu_selection(update: Update, context: CallbackContext):
    logger.info("Received menu selection '%s' from user %s", update.message.text, update.effective_user.id)
    text = update.message.text
    if text == "Help":
        help_command(update, context)
    elif text == "About":
        about_command(update, context)

def main():
    logger.info("Starting Telegram bot")
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher

    # Add handlers for commands and messages
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("about", about_command))
    dp.add_handler(
        MessageHandler(
            Filters.voice | Filters.audio | (Filters.document.file_extension("mp3") | Filters.document.file_extension("wav") | Filters.document.file_extension("ogg")),
            transcribe_audio
        )
    )
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_menu_selection))  # Handle menu text

    updater.start_polling()
    logger.info("Bot is polling for updates")
    updater.idle()
    logger.info("Bot stopped")

if __name__ == "__main__":
    main()
