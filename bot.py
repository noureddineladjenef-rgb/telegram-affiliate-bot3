import os
import logging
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# إعدادات البوت - استخدم التوكن الجديد
BOT_TOKEN = "8548245901:AAHtOUGOZfXFvANxFzxgaGBUP34bS6cNAiQ"
AFFILIATE_ID = "WXwrOePAXsTmqIRPvlxtfTAg45jDFtxC"

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    """رسالة الترحيب"""
    welcome_text = """
🛍️ *مرحباً بك في بوت تحويل روابط AliExpress* 🛍️

فقط أرسل لي رابط أي منتج من AliExpress وسأحوله لك إلى رابط أفليت!

📌 *مثال:*
https://www.aliexpress.com/item/xxxxxxxxx.html

🚀 ابدأ بإرسال الرابط الآن!
    """
    update.message.reply_text(welcome_text, parse_mode='Markdown')

def convert_to_affiliate(update: Update, context: CallbackContext):
    """دالة تحويل الروابط إلى أفليت"""
    user_message = update.message.text.strip()
    
    if 'aliexpress.com' in user_message and 'item' in user_message:
        try:
            # ترميز الرابط
            encoded_url = requests.utils.quote(user_message)
            # إنشاء رابط الأفليت
            affiliate_link = f"https://s.click.aliexpress.com/e/{AFFILIATE_ID}?url={encoded_url}"
            
            # رسالة النتيجة
            result_text = f"""
✅ *تم تحويل الرابط بنجاح!*

🎯 *رابط الأفليت الجديد:*
`{affiliate_link}`

📊 *يمكنك استخدام هذا الرابط للمشاركة والربح من العمولات!*
            """
            update.message.reply_text(result_text, parse_mode='Markdown')
            
        except Exception as e:
            update.message.reply_text("❌ حدث خطأ أثناء تحويل الرابط")
            logger.error(f"Error: {e}")
    else:
        update.message.reply_text("""
❌ *رابط غير مدعوم*

يرجى إرسال رابط منتج من AliExpress فقط.

📌 *مثال صحيح:*
https://www.aliexpress.com/item/1005006123456789.html
        """, parse_mode='Markdown')

def main():
    """الدالة الرئيسية"""
    try:
        # إنشاء Updater
        updater = Updater(BOT_TOKEN, use_context=True)
        
        # الحصول على الـ Dispatcher
        dp = updater.dispatcher
        
        # إضافة الـ Handlers
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, convert_to_affiliate))
        
        # بدء البوت
        logger.info("البوت يعمل الآن...")
        updater.start_polling()
        updater.idle()
        
    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {e}")

if __name__ == '__main__':
    main()