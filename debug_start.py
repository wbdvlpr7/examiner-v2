import sys

sys.path.insert(0, ".")

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# فعال کردن لاگ‌های کامل
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)


async def debug_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تابع start ساده برای دیباگ"""
    print("🎯 DEBUG: start command received!")

    # ایجاد دکمه‌های تست
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = [
        [InlineKeyboardButton("TEST IELTS", callback_data="exam_ielts")],
        [InlineKeyboardButton("TEST TOEFL", callback_data="exam_toefl")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    print("🎯 DEBUG: Sending message with keyboard...")

    # ارسال پیام
    await update.message.reply_text("Click a button below:", reply_markup=reply_markup)

    print("✅ DEBUG: Message sent successfully!")


async def debug_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر ساده برای callback"""
    query = update.callback_query
    await query.answer()

    print(f"🎉 CALLBACK RECEIVED! Data: {query.data}")

    await query.edit_message_text(f"You clicked: {query.data}")


def main():
    TOKEN = "8064007393:AAEUSrl9Fw42F3DB3LGfcb3-g4fH6mxqaQw"

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", debug_start))
    app.add_handler(CallbackQueryHandler(debug_callback))

    print("🚀 Starting debug bot...")
    print("📱 Send /start to the bot")
    print("👆 Click the buttons that appear")
    print("-" * 50)

    app.run_polling()


if __name__ == "__main__":
    main()
