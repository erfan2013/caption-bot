import os
import telebot

# توکن را از متغیر محیطی می‌خوانیم
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

# برای هر چت، کپشن جدا نگه می‌داریم
caption_by_chat = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "سلام! 👋\n"
        "من یه ربات ساده‌ام که زیر متن‌هات یه کپشن ثابت می‌ذارم.\n\n"
        "برای تنظیم کپشن از این دستور استفاده کن:\n"
        "/setcaption متن کپشن\n\n"
        "بعد از تنظیم کپشن، هر متنی بفرستی، همون متن + کپشن رو برات برمی‌گردونم. 😊"
    )


@bot.message_handler(commands=['setcaption'])
def set_caption(message):
    chat_id = message.chat.id

    parts = message.text.split(' ', 1)
    if len(parts) < 2 or not parts[1].strip():
        bot.reply_to(
            message,
            "❗ لطفاً بعد از دستور /setcaption متن کپشن را بنویسید.\n"
            "مثال:\n"
            "/setcaption این کپشن من است 🌟"
        )
        return

    new_caption = parts[1].strip()
    caption_by_chat[chat_id] = new_caption

    bot.reply_to(
        message,
        f"✅ کپشن جدید تنظیم شد:\n\n{new_caption}"
    )


@bot.message_handler(func=lambda msg: True, content_types=['text'])
def echo_with_caption(message):
    chat_id = message.chat.id
    user_text = message.text

    caption = caption_by_chat.get(chat_id, "🚀 کپشن پیش‌فرض")

    final_text = f"{user_text}\n\n{caption}"
    bot.reply_to(message, final_text)


if __name__ == "__main__":
    print("Bot is running on Render...")
    bot.infinity_polling()
