from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from app.core.states import ConversationState
from app.presentation.telegram.keyboards.factory import KeyboardFactory

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    await update.message.reply_text(
        "🎓 Welcome to Examiner Bot v2!\n\n"
        "Select exam type:",
        reply_markup=KeyboardFactory.create_exam_keyboard()
    )
    return ConversationState.SELECTING_EXAM