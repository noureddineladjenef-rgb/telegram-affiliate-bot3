import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
import hashlib
import time
import urllib.parse

# -----------------------------------------
#   🔐 بياناتك الخاصة (تم إدخالها كما طلبت)
# -----------------------------------------
TELEGRAM_TOKEN = "8548245901:AAHtOUGOZfXFvANxFzxgaGBUP34bS6cNAiQ"
APP_KEY = "503368"  
APP_SECRET = "OMIS6a8bKcWrUsu5Bsr34NooT9yYwB3q"
AFFILIATE_ID = "503368"
# -----------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_affiliate_link(original_url: str) -> str:
    """Generate AliExpress affiliate deep link"""

    encoded_url = urllib.parse.quote(original_url, safe='')
    timestamp = str(int(time.time() * 1000))

    raw = f"app_key={APP_KEY}&link={encoded_url}&timestamp={timestamp}{APP_SECRET}"
    sign = hashlib.md5(raw.encode('utf-8')).hexdigest()

    affiliate_url = (
        f"https://api.aliexpress.com/link/generate?"
        f"app_key={APP_KEY}&timestamp={timestamp}&sign={sign}"
        f"&link={encoded_url}&tracking_id={AFFILIATE_ID}"
    )

    return affiliate_url


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل رابط AliExpress وسأحوله لرابط أفليت 🔥")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "aliexpress" not in text.lower():
        await update.message.reply_text("❗ الرجاء إرسال رابط من AliExpress فقط.")
        return

    affiliate_link = generate_affiliate_link(text)
    await update.message.reply_text(f"🔗 رابط الأفليت الخاص بك:\n{affiliate_link}")


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()


if __name__ == "__main__":
    main()