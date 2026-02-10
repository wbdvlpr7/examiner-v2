import sys
import logging
import asyncio
from telegram.ext import Application
from app.core.config import settings

# Windows fix
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def initialize_database():
    """Initialize database"""
    try:
        from app.infrastructure.database.database import init_db

        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database init warning: {e}")


def main():
    # Initialize database
    asyncio.run(initialize_database())

    # Create application
    app = Application.builder().token(settings.BOT_TOKEN).build()

    # Import command handlers
    try:
        from app.presentation.telegram.handlers.quick_commands import (
            help_command,
            vocab_command,
            paraphrase_command,
        )
        from telegram.ext import CommandHandler

        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("vocab", vocab_command))
        app.add_handler(CommandHandler("paraphrase", paraphrase_command))

        logger.info("Quick commands loaded")
    except Exception as e:
        logger.warning(f"Quick commands not loaded: {e}")

    # Add conversation handler
    try:
        from app.presentation.telegram.conversation import create_conversation_handler

        conv_handler = create_conversation_handler()
        app.add_handler(conv_handler)
        logger.info("Conversation handler loaded")
    except Exception as e:
        logger.error(f"Failed to load conversation handler: {e}")
        # Fallback: simple start command
        from telegram.ext import CommandHandler

        async def simple_start(update, context):
            await update.message.reply_text("Bot is starting up...")

        app.add_handler(CommandHandler("start", simple_start))

    # Add error handler
    async def error_handler(update, context):
        logger.error(f"Update {update} caused error {context.error}", exc_info=True)

    app.add_error_handler(error_handler)

    logger.info(f"Bot starting in {settings.ENVIRONMENT} mode")
    app.run_polling(allowed_updates=[])


if __name__ == "__main__":
    main()
