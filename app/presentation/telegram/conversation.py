from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from app.core.states import ConversationState

# Avoid circular imports by importing inside functions


def create_conversation_handler():
    """Create conversation handler with local imports"""

    # Import handlers locally to avoid circular imports
    from app.presentation.telegram.handlers.start import start
    from app.presentation.telegram.handlers.exam_handlers import (
        select_exam,
        select_skill,
        select_mode,
    )
    from app.presentation.telegram.handlers.input_handlers import (
        handle_text_input,
        handle_voice_input,
        submit_another,
    )

    # Define callback functions locally
    async def start_over_callback(update, context):
        """Handle start_over callback"""
        query = update.callback_query
        await query.answer()
        return await start(update, context)

    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ConversationState.SELECTING_EXAM: [
                CallbackQueryHandler(select_exam, pattern="^exam_")
            ],
            ConversationState.SELECTING_SKILL: [
                CallbackQueryHandler(select_skill, pattern="^skill_")
            ],
            ConversationState.SELECTING_MODE: [
                CallbackQueryHandler(select_mode, pattern="^mode_")
            ],
            ConversationState.AWAITING_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input),
                MessageHandler(filters.VOICE, handle_voice_input),
                CallbackQueryHandler(submit_another, pattern="^submit_another$"),
                CallbackQueryHandler(start_over_callback, pattern="^start_over$"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True,
        per_message=False,
    )
