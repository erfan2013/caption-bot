import os
from flask import Flask, request
import telebot

# ----------------- تنظیمات -----------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # مثل: https://caption-bot-v8jr.onrender.com/webhook

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL environment variable is not set")

print("BOT_TOKEN starts with:", BOT_TOKEN[:10])
print("WEBHOOK_URL:", WEBHOOK_URL)

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
caption_by_chat = {}

# ----------------- هندلرهای ربات -----------------

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.reply_to(
        message,
        "سلام! 👋\n"
        "من ربات کپشن‌ساز هستم.\n"
        "از این دستور استفاده کن:\n\n"
        "/setcaption کپشن شما\n"
        "/mycaption دیدن کپشن فعلی"
    )

@bot.message_handler(commands=['setcaption'])
def setcaption_handler(message):
    chat_id = message.chat.id
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        bot.reply_to(message, "❗ لطفاً کپشن را بنویسید.\nمثال: /setcaption سلام")
        return

    caption_by_chat[chat_id] = parts[1].strip()
    bot.reply_to(message, "کپشن ذخیره شد! ✅")

@bot.message_handler(commands=['mycaption'])
def mycaption_handler(message):
    chat_id = message.chat.id
    caption = caption_by_chat.get(chat_id, "🚀 هنوز کپشنی تنظیم نشده.")
    bot.reply_to(message, f"کپشن شما:\n\n{caption}")

@bot.message_handler(func=lambda msg: True)
def main_handler(message):
    chat_id = message.chat.id
    user_text = message.text
    caption = caption_by_chat.get(chat_id, "🚀 کپشن پیش‌فرض")
    bot.reply_to(message, f"{user_text}\n\n{caption}")

# ----------------- Flask (Webhook Server) -----------------

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Bot is running (Webhook)", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        json_data = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        print("❌ WEBHOOK ERROR:", e)
        return "ERROR", 500

def setup_webhook():
    bot.delete_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    print("Webhook set to:", WEBHOOK_URL)

if __name__ == "__main__":
    setup_webhook()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
