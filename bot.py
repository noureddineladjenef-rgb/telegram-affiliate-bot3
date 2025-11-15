import logging
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# إعداد بسيط
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# التوكن والمعرف
BOT_TOKEN = "8548245901:AAHtOUGOZfXFvANxFzxgaGBUP34bS6cNAiQ"
AFFILIATE_ID = "WXwrOePAXsTmqIRPvlxtfTAg45jDFtxC"

def start(update: Update, context: CallbackContext):
    update.message.reply_text("🛍️ أرسل رابط منتج من AliExpress وسأحوله لرابط أفليت")

def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text.strip()
    
    if 'aliexpress.com' in user_message and 'item' in user_message:
        try:
            # تحويل الرابط
            encoded_url = requests.utils.quote(user_message)
            affiliate_link = f"https://s.click.aliexpress.com/e/{AFFILIATE_ID}?url={encoded_url}"
            
            # إرسال النتيجة
            update.message.reply_text(f"✅ تم التحويل:\n{affiliate_link}")
            
        except Exception as e:
            update.message.reply_text("❌ حدث خطأ في التحويل")
    else:
        update.message.reply_text("❌ أرسل رابط منتج صالح من AliExpress")

def main():
    try:
        logger.info("بدء البوت...")
        updater = Updater(BOT_TOKEN, use_context=True)
        dp = updater.dispatcher
        
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
        
        logger.info("البوت يعمل...")
        updater.start_polling()
        updater.idle()
        
    except Exception as e:
        logger.error(f"خطأ: {e}")

if __name__ == '__main__':
    main()