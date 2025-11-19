import os
from flask import Flask, request
import telebot

# ----------------- تنظیمات پایه -----------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # مثلا: https://your-service.onrender.com/webhook

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL environment variable is not set")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

# برای هر چت کپشن جدا
caption_by_chat = {}

# ----------------- هندلرهای ربات -----------------


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "سلام! 👋\n"
        "من یه ربات ساده‌ام که زیر متن‌هات یه کپشن ثابت می‌ذارم.\n\n"
        "برای تنظیم کپشن:\n"
        "/setcaption متن کپشن\n\n"
        "بعد از تنظیم، هر متنی بفرستی، همون متن + کپشن رو می‌فرستم. 😊"
    )


@bot.message_handler(commands=['setcaption'])
def set_caption(message):
    chat_id = message.chat.id

    parts = message.text.split(' ', 1)
    if len(parts) < 2 or not parts[1].strip():
        bot.reply_to(
            message,
            "❗ لطفاً بعد از /setcaption متن کپشن را بنویسید.\n"
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


# ----------------- Flask Webhook App -----------------

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return "Caption bot (webhook mode) is running ✅", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    # بدنه‌ی JSON که تلگرام می‌فرسته
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200


def setup_webhook():
    # هنگام بالا آمدن برنامه، وبهوک را ست می‌کنیم
    bot.delete_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    print("Webhook set to:", WEBHOOK_URL)


if __name__ == "__main__":
    # یک بار موقع استارت، وبهوک ست می‌شود
    setup_webhook()

    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
