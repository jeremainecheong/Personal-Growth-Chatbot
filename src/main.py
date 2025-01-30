import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters, 
    ConversationHandler
)
from bot.handlers import (
    start, help_command, cancel, error_handler,
    handle_menu_selection, handle_topic, handle_situation,
    handle_desired_outcome, handle_emotion_selection,
    handle_mood_rating, handle_situation_confirmation,
    handle_advice_rating, handle_journal_entry,
    handle_journal_mood, handle_journal_tags
)
from bot.states import ConversationState
from database.connection import connect_to_mongodb

# Load environment variables
load_dotenv()

# Configure logging
# In production (Render), we only use StreamHandler
# In development, we use both file and stream handlers
if os.getenv('RENDER'):
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=os.getenv('LOG_LEVEL', 'INFO'),
        handlers=[logging.StreamHandler()]
    )
else:
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=os.getenv('LOG_LEVEL', 'INFO'),
        handlers=[
            logging.FileHandler("logs/bot.log"),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

def main():
    """Start the bot."""
    # Connect to MongoDB
    try:
        # Connect to MongoDB
        connect_to_mongodb()

        # Create the Application and pass it your bot's token
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            raise ValueError("Telegram bot token not found in environment variables")
        
        application = Application.builder().token(token).build()

        # Add conversation handler with states
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                ConversationState.SELECTING_ACTION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        handle_menu_selection
                    )
                ],
                ConversationState.RECORDING_TOPIC: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        handle_topic
                    )
                ],
                ConversationState.RECORDING_SITUATION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        handle_situation
                    )
                ],
                ConversationState.RECORDING_DESIRED_OUTCOME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        handle_desired_outcome
                    )
                ],
                ConversationState.SELECTING_EMOTIONS: [
                    CallbackQueryHandler(handle_emotion_selection)
                ],
                ConversationState.RATING_MOOD: [
                    CallbackQueryHandler(handle_mood_rating)
                ],
                ConversationState.CONFIRMING_SITUATION: [
                    CallbackQueryHandler(handle_situation_confirmation)
                ],
                ConversationState.RATING_ADVICE: [
                    CallbackQueryHandler(handle_advice_rating)
                ],
                ConversationState.WRITING_JOURNAL: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        handle_journal_entry
                    )
                ],
                ConversationState.TAGGING_ENTRY: [
                    CallbackQueryHandler(handle_journal_tags)
                ]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_message=False
        )

        # Add handlers
        application.add_handler(conv_handler)
        application.add_handler(CommandHandler('help', help_command))
        
        # Error handler
        application.add_error_handler(error_handler)

        # Start the Bot
        logger.info("Starting Personal Growth Assistant bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()
