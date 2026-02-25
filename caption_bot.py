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

# ذخیره کپشن‌ها (در RAM) — با ریست سرور پاک می‌شود
caption_by_chat = {}

# ✅ اضافه کردن Command ها برای نمایش در منوی /
bot.set_my_commands([
    telebot.types.BotCommand("setcaption", "تنظیم/تغییر کپشن"),
    telebot.types.BotCommand("caption", "نمایش کپشن فعلی"),
    telebot.types.BotCommand("use", "استفاده از کپشن روی متن"),
    telebot.types.BotCommand("del", "حذف کپشن"),
])

# ----------------- هندلرهای ربات -----------------

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.reply_to(
        message,
        "سلام! 👋\n"
        "من ربات کپشن‌ساز هستم.\n\n"
        "دستورها:\n"
        "/setcaption کپشن شما (یا فقط /setcaption بزن و بعد کپشن رو بفرست)\n"
        "/caption دیدن کپشن فعلی\n"
        "/use متن (چسباندن کپشن به متن)\n"
        "/del حذف کپشن"
    )

# --- setcaption: هم با متن در همان پیام، هم مرحله‌ای ---

@bot.message_handler(commands=['setcaption'])
def setcaption_handler(message):
    chat_id = message.chat.id
    parts = message.text.split(" ", 1)

    # حالت 1: کاربر کپشن را در همان پیام داده
    if len(parts) >= 2 and parts[1].strip():
        caption_by_chat[chat_id] = parts[1].strip()
        bot.reply_to(message, "کپشن ذخیره شد! ✅")
        return

    # حالت 2: کاربر فقط /setcaption زده → پیام بعدی کپشن باشد
    msg = bot.reply_to(message, "خب، کپشن جدید رو همینجا بفرست 👇")
    bot.register_next_step_handler(msg, _save_caption_next)

def _save_caption_next(message):
    chat_id = message.chat.id

    # اگر پیام بعدی خودش دستور بود، ذخیره نکن
    if getattr(message, "text", None) and message.text.startswith("/"):
        bot.reply_to(message, "❗ کپشن باید متن معمولی باشه (با / شروع نشه). دوباره /setcaption رو بزن.")
        return

    # اگر متن خالی/غیرمتنی بود
    if not getattr(message, "text", None) or not message.text.strip():
        bot.reply_to(message, "❗ کپشن معتبر نیست. دوباره /setcaption رو بزن و کپشن رو بفرست.")
        return

    caption_by_chat[chat_id] = message.text.strip()
    bot.reply_to(message, "کپشن ذخیره شد! ✅")

# --- caption: نمایش کپشن فعلی ---

@bot.message_handler(commands=['caption'])
def caption_handler(message):
    chat_id = message.chat.id
    caption = caption_by_chat.get(chat_id, "🚀 هنوز کپشنی تنظیم نشده.")
    bot.reply_to(message, f"کپشن شما:\n\n{caption}")

# --- del: حذف کپشن ---

@bot.message_handler(commands=['del'])
def del_handler(message):
    chat_id = message.chat.id
    if chat_id in caption_by_chat:
        del caption_by_chat[chat_id]
        bot.reply_to(message, "کپشن حذف شد ✅")
    else:
        bot.reply_to(message, "کپشنی برای حذف وجود نداره.")

# --- use: اعمال کپشن روی متن (فقط وقتی با دستور صدا زده می‌شود) ---

@bot.message_handler(commands=['use'])
def use_handler(message):
    chat_id = message.chat.id
    parts = message.text.split(" ", 1)

    if len(parts) < 2 or not parts[1].strip():
        bot.reply_to(message, "❗ لطفاً متن را بعد از دستور بنویسید.\nمثال: /use متن من")
        return

    user_text = parts[1].strip()
    caption = caption_by_chat.get(chat_id, "🚀 کپشن پیش‌فرض")
    bot.reply_to(message, f"{user_text}\n\n{caption}")

# ✅ هندل پیام‌های معمولی (نه دستورها)
@bot.message_handler(func=lambda msg: getattr(msg, "text", None) and not msg.text.startswith("/"))
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



# import os
# from flask import Flask, request
# import telebot

# # ----------------- تنظیمات -----------------

# BOT_TOKEN = os.environ.get("BOT_TOKEN")
# WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # مثل: https://caption-bot-v8jr.onrender.com/webhook

# if not BOT_TOKEN:
#     raise ValueError("BOT_TOKEN environment variable is not set")

# if not WEBHOOK_URL:
#     raise ValueError("WEBHOOK_URL environment variable is not set")

# print("BOT_TOKEN starts with:", BOT_TOKEN[:10])
# print("WEBHOOK_URL:", WEBHOOK_URL)

# bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
# caption_by_chat = {}

# # ----------------- هندلرهای ربات -----------------

# @bot.message_handler(commands=['start'])
# def start_handler(message):
#     bot.reply_to(
#         message,
#         "سلام! 👋\n"
#         "من ربات کپشن‌ساز هستم.\n"
#         "از این دستور استفاده کن:\n\n"
#         "/setcaption کپشن شما\n"
#         "/mycaption دیدن کپشن فعلی"
#     )

# @bot.message_handler(commands=['setcaption'])
# def setcaption_handler(message):
#     chat_id = message.chat.id
#     parts = message.text.split(" ", 1)
#     if len(parts) < 2:
#         bot.reply_to(message, "❗ لطفاً کپشن را بنویسید.\nمثال: /setcaption سلام")
#         return

#     caption_by_chat[chat_id] = parts[1].strip()
#     bot.reply_to(message, "کپشن ذخیره شد! ✅")

# @bot.message_handler(commands=['mycaption'])
# def mycaption_handler(message):
#     chat_id = message.chat.id
#     caption = caption_by_chat.get(chat_id, "🚀 هنوز کپشنی تنظیم نشده.")
#     bot.reply_to(message, f"کپشن شما:\n\n{caption}")

# @bot.message_handler(func=lambda msg: True)
# def main_handler(message):
#     chat_id = message.chat.id
#     user_text = message.text
#     caption = caption_by_chat.get(chat_id, "🚀 کپشن پیش‌فرض")
#     bot.reply_to(message, f"{user_text}\n\n{caption}")

# # ----------------- Flask (Webhook Server) -----------------

# app = Flask(__name__)

# @app.route("/", methods=["GET"])
# def index():
#     return "Bot is running (Webhook)", 200

# @app.route("/webhook", methods=["POST"])
# def webhook():
#     try:
#         json_data = request.get_data().decode("utf-8")
#         update = telebot.types.Update.de_json(json_data)
#         bot.process_new_updates([update])
#         return "OK", 200
#     except Exception as e:
#         print("❌ WEBHOOK ERROR:", e)
#         return "ERROR", 500

# def setup_webhook():
#     bot.delete_webhook()
#     bot.set_webhook(url=WEBHOOK_URL)
#     print("Webhook set to:", WEBHOOK_URL)

# if __name__ == "__main__":
#     setup_webhook()
#     port = int(os.environ.get("PORT", 10000))
#     app.run(host="0.0.0.0", port=port)
