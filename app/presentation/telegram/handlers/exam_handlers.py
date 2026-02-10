from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from app.core.states import ConversationState
from app.presentation.telegram.keyboards.factory import KeyboardFactory
from app.core.constants import EXAMS, SKILLS, MODES
from app.infrastructure.database.repositories import UserRepository
from app.infrastructure.database.database import AsyncSessionLocal

async def select_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    exam_id = query.data.split("_")[1]
    context.user_data["exam_type"] = exam_id
    
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        await repo.update_user_state(
            telegram_id=query.from_user.id,
            state=ConversationState.SELECTING_SKILL.value,
            exam_type=exam_id
        )
    
    exam_name = EXAMS[exam_id]["name"]
    await query.edit_message_text(
        f"Selected: {exam_name}\n\nNow select skill:",
        reply_markup=KeyboardFactory.create_skill_keyboard(exam_id)
    )
    return ConversationState.SELECTING_SKILL

async def select_skill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    skill_id = query.data.split("_")[1]
    context.user_data["skill_type"] = skill_id
    
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        await repo.update_user_state(
            telegram_id=query.from_user.id,
            state=ConversationState.SELECTING_MODE.value,
            skill_type=skill_id
        )
    
    skill_name = SKILLS[skill_id]["name"]
    await query.edit_message_text(
        f"Selected: {skill_name}\n\nNow select evaluation mode:",
        reply_markup=KeyboardFactory.create_mode_keyboard()
    )
    return ConversationState.SELECTING_MODE

async def select_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    mode_id = query.data.split("_")[1]
    context.user_data["mode"] = mode_id
    
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        await repo.update_user_state(
            telegram_id=query.from_user.id,
            state=ConversationState.AWAITING_INPUT.value,
            mode=mode_id
        )
    
    exam_name = EXAMS[context.user_data["exam_type"]]["name"]
    skill_name = SKILLS[context.user_data["skill_type"]]["name"]
    mode_name = MODES[mode_id]["name"]
    
    message = f"""
📍 <b>{exam_name} | {skill_name} | {mode_name}</b>
➖➖➖➖➖➖
🚀 <b>Ready!</b> Please send your text.
"""
    
    await query.edit_message_text(
        text=message,
        parse_mode="HTML"
    )
    return ConversationState.AWAITING_INPUT