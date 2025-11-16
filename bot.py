import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# -----------------------------------------
#   🔐 بيانات البوت والأفلييت
# -----------------------------------------
BOT_TOKEN = "8548245901:AAHtOUGOZfXFvANxFzxgaGBUP34bS6cNAiQ"
AFFILIATE_ID = "503368"
# -----------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_affiliate_link(url: str) -> str:
    """
    توليد رابط أفلييت بسيط بإضافة tracking ID
    """
    if "?" in url:
        return f"{url}&aff_trace_id={AFFILIATE_ID}"
    else:
        return f"{url}?aff_trace_id={AFFILIATE_ID}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛍️ مرحباً بك! أرسل لي رابط منتج من AliExpress وسأعطيك رابط أفلييت صالح."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_url = update.message.text.strip()

    # التحقق من صحة الرابط
    if "aliexpress" not in product_url.lower():
        await update.message.reply_text("❌ الرجاء إرسال رابط صحيح من AliExpress فقط.")
        return

    affiliate_link = generate_affiliate_link(product_url)
    await update.message.reply_text(f"🔗 رابط الأفلييت الخاص بك:\n{affiliate_link}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()