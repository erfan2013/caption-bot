import os
from flask import Flask, request
import telebot

# ----------------- تنظیمات پایه -----------------

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # مثلا: https://caption-bot-v8jr.onrender.com/webhook
TEST_CHAT_ID = os.environ.get("TEST_CHAT_ID")  # برای تست دستی ارسال پیام

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL environment variable is not set")

print("BOT_TOKEN starts with:", BOT_TOKEN[:10])
print("WEBHOOK_URL is:", WEBHOOK_URL)
if TEST_CHAT_ID:
    print("TEST_CHAT_ID is set")
else:
    print("TEST_CHAT_ID is NOT set (optional)")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

# ذخیره کپشن برای هر کاربر (در حافظه)
caption_by_chat = {}

# ----------------- هندلرهای ربات -----------------


@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(f"[/start] from chat_id={message.chat.id}")
    bot.reply_to(
        message,
        "سلام! 👋\n"
        "من یه ربات ساده‌ام که زیر متن‌هات یه کپشن ثابت می‌ذارم.\n\n"
        "برای تنظیم یا تغییر کپشن از این دستور استفاده کنید:\n"
        "/setcaption متن کپشن\n\n"
        "برای دیدن کپشن فعلی:\n"
        "/mycaption\n\n"
        "هر متنی ارسال کنید، نسخه کپشن‌دارش رو براتون می‌فرستم. 😊"
    )


@bot.message_handler(commands=['setcaption'])
def set_caption(message):
    chat_id = message.chat.id
    print(f"[/setcaption] from chat_id={chat_id}")

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


@bot.message_handler(commands=['mycaption'])
def show_caption(message):
    chat_id = message.chat.id
    print(f"[/mycaption] from chat_id={chat_id}")
    caption = caption_by_chat.get(chat_id, "🚀 هنوز هیچ کپشنی برای شما تنظیم نشده است.")
    bot.reply_to(message, f"کپشن فعلی شما:\n\n{caption}")


@bot.message_handler(func=lambda msg: True, content_types=['text'])
def echo_with_caption(message):
    chat_id = message.chat.id
    user_text = message.text
    print(f"[text] from chat_id={chat_id}: {user_text!r}")

    caption = caption_by_chat.get(chat_id, "🚀 کپشن پیش‌فرض")

    final_text = f"{user_text}\n\n{caption}"
    bot.reply_to(message, final_text)

# ----------------- Flask Webhook App -----------------

app = Flask(__name__)


@app.route("/", methods=["GET", "HEAD"])
def index():
    return "Caption bot (webhook mode) is running ✅", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        print("🔔 Webhook called!")
        print("Headers:", dict(request.headers))
        json_str = request.get_data().decode("utf-8")
        print("Payload:", json_str)
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        print("❌ Error in webhook:", e)
        return "ERROR", 500


@app.route("/test", methods=["GET"])
def test():
    """
    روت تست:
    اگر TEST_CHAT_ID در env ست شده باشد، یک پیام تست برای آن چت می‌فرستد.
    """
    if not TEST_CHAT_ID:
        return "TEST_CHAT_ID environment variable is not set", 500

    try:
        chat_id = int(TEST_CHAT_ID)
        bot.send_message(chat_id, "پیام تست از سرور Render ✅")
        print(f"[test] sent test message to chat_id={chat_id}")
        return "sent", 200
    except Exception as e:
        print("❌ Error in /test:", e)
        return "error", 500


def setup_webhook():
    print("Setting webhook...")
    bot.delete_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    print("Webhook set to:", WEBHOOK_URL)


if __name__ == "__main__":
    setup_webhook()
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Flask app on port {port} ...")
    app.run(host="0.0.0.0", port=port)
