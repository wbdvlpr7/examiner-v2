from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from app.infrastructure.services.ai_service import ai_service

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
<b>🤖 Language Expert Bot - Help Guide</b>

<b>📋 Available Commands:</b>

🚀 <b>/start</b> - Main menu and bot introduction

📚 <b>/vocab [word]</b> - Get detailed word information
Example: /vocab hello

🔄 <b>/paraphrase</b> - Paraphrase text in 4 styles
Send text after command

🎓 <b>Exam Preparation:</b>
Use /start → Exam Preparation for detailed feedback on:
• IELTS Writing/Speaking
• TOEFL Writing/Speaking
• PTE Writing/Speaking
    """
    await update.message.reply_text(help_text, parse_mode="HTML")

async def vocab_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a word: /vocab hello")
        return
    
    word = " ".join(context.args)
    await update.message.reply_text(f"Looking up: {word}")
    
    prompt = f"Provide dictionary entry for: {word}"
    response = await ai_service.generate_feedback(prompt, temperature=0.1)
    await update.message.reply_text(response, parse_mode="HTML")

async def paraphrase_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Send text to paraphrase")
        return
    
    text = " ".join(context.args)
    prompt = f"Paraphrase in 4 styles (academic, formal, casual, creative): {text}"
    response = await ai_service.generate_feedback(prompt)
    await update.message.reply_text(response, parse_mode="HTML")

# Handler instances
help_handler = CommandHandler("help", help_command)
vocab_handler = CommandHandler("vocab", vocab_command)
paraphrase_handler = CommandHandler("paraphrase", paraphrase_command)