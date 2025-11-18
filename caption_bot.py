import os
<<<<<<< HEAD
import threading
import telebot
from flask import Flask

# توکن را از متغیر محیطی می‌خوانیم
BOT_TOKEN = os.environ.get("BOT_TOKEN")
=======
import telebot

# توکن را از متغیر محیطی می‌خوانیم
BOT_TOKEN = os.environ.get("BOT_TOKEN")

>>>>>>> 8d3bad0a72a7ae956fb235c2ffa7418da11d1721
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

<<<<<<< HEAD
# برای هر چت کپشن جدا
caption_by_chat = {}

# ----- هندلرهای ربات -----
=======
# برای هر چت، کپشن جدا نگه می‌داریم
caption_by_chat = {}

>>>>>>> 8d3bad0a72a7ae956fb235c2ffa7418da11d1721

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "سلام! 👋\n"
        "من یه ربات ساده‌ام که زیر متن‌هات یه کپشن ثابت می‌ذارم.\n\n"
<<<<<<< HEAD
        "برای تنظیم کپشن:\n"
        "/setcaption متن کپشن\n\n"
        "بعد از تنظیم، هر متنی بفرستی، همون متن + کپشن رو می‌فرستم. 😊"
=======
        "برای تنظیم کپشن از این دستور استفاده کن:\n"
        "/setcaption متن کپشن\n\n"
        "بعد از تنظیم کپشن، هر متنی بفرستی، همون متن + کپشن رو برات برمی‌گردونم. 😊"
>>>>>>> 8d3bad0a72a7ae956fb235c2ffa7418da11d1721
    )


@bot.message_handler(commands=['setcaption'])
def set_caption(message):
    chat_id = message.chat.id

    parts = message.text.split(' ', 1)
    if len(parts) < 2 or not parts[1].strip():
        bot.reply_to(
            message,
<<<<<<< HEAD
            "❗ لطفاً بعد از /setcaption متن کپشن را بنویسید.\n"
=======
            "❗ لطفاً بعد از دستور /setcaption متن کپشن را بنویسید.\n"
>>>>>>> 8d3bad0a72a7ae956fb235c2ffa7418da11d1721
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

<<<<<<< HEAD
# ----- وب‌سرور ساده برای رندر -----

app = Flask(__name__)

@app.route("/")
def index():
    return "Caption bot is running ✅", 200


def run_bot():
    # ربات تلگرام در یک ترد جداگانه
    bot.infinity_polling()


if __name__ == "__main__":
    print("Starting bot & web server on Render...")

    # اجرای ربات در بک‌گراند
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()

    # پورت مورد انتظار Render
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
=======

if __name__ == "__main__":
    print("Bot is running on Render...")
    bot.infinity_polling()
>>>>>>> 8d3bad0a72a7ae956fb235c2ffa7418da11d1721
