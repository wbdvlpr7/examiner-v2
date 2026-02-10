from datetime import datetime
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from app.core.states import ConversationState
from app.infrastructure.services.ai_service import ai_service
from app.infrastructure.services.stt_service import stt_service
from app.infrastructure.services.prompt_service import prompt_service
from app.infrastructure.database.repositories import UserRepository
from app.infrastructure.database.database import AsyncSessionLocal
from app.infrastructure.database.models import User
from app.presentation.telegram.keyboards.factory import KeyboardFactory
import html


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input with improved error handling"""
    if update.message is None:
        return ConversationState.AWAITING_INPUT

    user_id = update.effective_user.id if update.effective_user else None
    if user_id is None:
        return ConversationState.AWAITING_INPUT

    user_text = update.message.text.strip() if update.message.text else ""

    if len(user_text.split()) > 1000:
        await update.message.reply_text("⚠️ Text too long. Maximum 1000 words.")
        return ConversationState.AWAITING_INPUT

    await update.message.reply_text("✅ Processing...")

    try:
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user: Optional[User] = await repo.get_user(user_id)

            if (
                user is None
                or user.exam_type is None
                or user.skill_type is None
                or user.mode is None
            ):
                await update.message.reply_text("Please use /start to begin.")
                return ConversationState.SELECTING_EXAM

            # Get user settings as strings
            exam_type = str(user.exam_type)
            skill_type = str(user.skill_type)
            mode = str(user.mode)

            # Process based on skill
            if skill_type == "writing":
                prompt = prompt_service.get_writing_prompt(exam_type, mode, user_text)
                feedback = await ai_service.generate_feedback(prompt)

            elif skill_type == "speaking":
                # For speaking skill with text input (simulated speaking)
                prompt = prompt_service.get_speaking_prompt(exam_type, mode, user_text)
                feedback = await ai_service.generate_feedback(prompt)

            elif skill_type == "paraphrase":
                prompt = prompt_service.get_paraphrase_prompt(
                    exam_type, mode, user_text
                )
                feedback = await ai_service.generate_feedback(prompt)

            else:
                feedback = "This skill is not yet implemented."

            # Escape HTML in user text for safety
            feedback = html.escape(feedback)

            # Send feedback
            await send_feedback_in_chunks(
                update, feedback, KeyboardFactory.create_post_feedback_keyboard()
            )

            # Log interaction
            await repo.update_user_state(
                telegram_id=user_id,
                state=str(ConversationState.AWAITING_INPUT.value),
                last_interaction=datetime.utcnow(),
            )

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:200]}")

    return ConversationState.AWAITING_INPUT


async def handle_voice_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice input with transcription"""
    if update.message is None or update.message.voice is None:
        return ConversationState.AWAITING_INPUT

    voice = update.message.voice

    # Validate duration
    if voice.duration > 120:  # 2 minutes max
        await update.message.reply_text("⚠️ Audio too long. Maximum 2 minutes.")
        return ConversationState.AWAITING_INPUT

    await update.message.reply_text("🎤 Processing audio...")

    try:
        # Get audio file
        voice_file = await voice.get_file()
        audio_bytes = await voice_file.download_as_bytearray()

        # Validate audio quality
        if not await stt_service.validate_audio_quality(audio_bytes):
            await update.message.reply_text(
                "⚠️ Audio quality too low. Please try again."
            )
            return ConversationState.AWAITING_INPUT

        # Transcribe
        transcript, confidence = await stt_service.transcribe_audio(audio_bytes)

        if confidence < 0.3:
            await update.message.reply_text(
                f"⚠️ Low confidence transcription ({confidence:.1%}). "
                f"Transcription: {transcript}"
            )
            return ConversationState.AWAITING_INPUT

        # Get user settings
        user_id = update.effective_user.id if update.effective_user else None
        if user_id is None:
            return ConversationState.AWAITING_INPUT

        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user: Optional[User] = await repo.get_user(user_id)

            if user is None or user.skill_type != "speaking":
                await update.message.reply_text("Please select speaking skill first.")
                return ConversationState.AWAITING_INPUT

            # Show transcription
            transcription_msg = (
                f"📝 <b>Transcription (confidence: {confidence:.1%}):</b>\n"
                f"{transcript}\n\n"
                f"⏱️ Duration: {voice.duration} seconds\n"
                f"📊 Analyzing speaking skills..."
            )

            await update.message.reply_text(transcription_msg, parse_mode="HTML")

            # Generate feedback
            prompt = prompt_service.get_speaking_prompt(
                str(user.exam_type), str(user.mode), transcript, voice.duration
            )

            feedback = await ai_service.generate_feedback(prompt)
            feedback = html.escape(feedback)

            # Send feedback
            await send_feedback_in_chunks(
                update, feedback, KeyboardFactory.create_post_feedback_keyboard()
            )

    except Exception as e:
        await update.message.reply_text(f"❌ Error processing audio: {str(e)[:200]}")

    return ConversationState.AWAITING_INPUT


async def submit_another(update, context):
    """Handle submit_another callback"""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "✅ Ready for another submission!\n\nPlease send your text or voice message.",
        parse_mode="HTML",
    )

    return ConversationState.AWAITING_INPUT


async def send_feedback_in_chunks(update: Update, text: str, reply_markup=None):
    """Send long text in chunks with proper formatting"""
    max_length = 4000

    if len(text) <= max_length:
        if update.callback_query and update.callback_query.message:
            await update.callback_query.message.reply_text(
                text, parse_mode="HTML", reply_markup=reply_markup
            )
        elif update.message:
            await update.message.reply_text(
                text, parse_mode="HTML", reply_markup=reply_markup
            )
        return

    # Split into chunks
    chunks = []
    current_chunk = ""

    for line in text.split("\n"):
        if len(current_chunk) + len(line) + 1 < max_length:
            current_chunk += line + "\n"
        else:
            chunks.append(current_chunk)
            current_chunk = line + "\n"

    if current_chunk:
        chunks.append(current_chunk)

    # Send chunks
    for i, chunk in enumerate(chunks):
        is_last = i == len(chunks) - 1

        if update.callback_query and update.callback_query.message and i == 0:
            await update.callback_query.message.reply_text(
                chunk, parse_mode="HTML", reply_markup=reply_markup if is_last else None
            )
        elif update.callback_query and update.callback_query.message:
            await update.callback_query.message.reply_text(chunk, parse_mode="HTML")
        elif update.message:
            await update.message.reply_text(
                chunk, parse_mode="HTML", reply_markup=reply_markup if is_last else None
            )
