import os
import logging
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# التوكن والمعرف
BOT_TOKEN = "8548245901:AAHtOUGOZfXFvANxFzxgaGBUP34bS6cNAiQ"
AFFILIATE_ID = "WXwrOePAXsTmqIRPvlxtfTAg45jDFtxC"

def convert_to_affiliate_link(product_url):
    """تحويل رابط المنتج إلى رابط أفليت"""
    try:
        encoded_url = requests.utils.quote(product_url)
        affiliate_link = f"https://s.click.aliexpress.com/e/{AFFILIATE_ID}?url={encoded_url}"
        return affiliate_link
    except Exception as e:
        logger.error(f"Error converting link: {e}")
        return None

def is_valid_aliexpress_link(url):
    """التحقق من أن الرابط من AliExpress"""
    return 'aliexpress.com' in url and 'item' in url

def start(update, context):
    """رسالة الترحيب"""
    welcome_text = """
🛍️ *مرحباً بك في بوت تحويل روابط AliExpress* 🛍️

🤖 *ماذا أستطيع أن أفعل؟*
• تحويل روابط منتجات AliExpress إلى روابط أفليت

📌 *كيفية الاستخدام؟*
1. أرسل لي رابط أي منتج من AliExpress
2. سأحوله لك إلى رابط أفليت

🎯 *مثال للرابط:*
https://www.aliexpress.com/item/1005006123456789.html

🚀 *ابدأ الآن بإرسال الرابط!*
    """
    update.message.reply_text(welcome_text)

def help_command(update, context):
    """أمر المساعدة"""
    help_text = """
📖 *دليل استخدام البوت*

🔹 *الأوامر المتاحة:*
/start - بدء استخدام البوت
/help - عرض هذه الرسالة

🔹 *طريقة العمل:*
1. ابحث عن منتج في AliExpress
2. انسخ رابط المنتج
3. أرسل الرابط للبوت
4. سيُعيد لك رابط الأفليت الجديد
    """
    update.message.reply_text(help_text)

def handle_message(update, context):
    """معالجة رسائل المستخدم"""
    user_message = update.message.text.strip()
    
    if not is_valid_aliexpress_link(user_message):
        error_text = """
❌ *رابط غير مدعوم*

يرجى إرسال رابط منتج صالح من AliExpress

📌 *مثال صحيح:*
https://www.aliexpress.com/item/1005006123456789.html
        """
        update.message.reply_text(error_text)
        return
    
    try:
        affiliate_link = convert_to_affiliate_link(user_message)
        
        if affiliate_link:
            success_text = f"""
✅ *تم تحويل الرابط بنجاح!*

🎯 *رابط الأفليت الجديد:*
`{affiliate_link}`

💰 *شارك هذا الرابط لربح العمولات!*
            """
            update.message.reply_text(success_text)
        else:
            update.message.reply_text("❌ حدث خطأ أثناء تحويل الرابط")
            
    except Exception as e:
        update.message.reply_text("❌ حدث خطأ غير متوقع")
        logger.error(f"Error: {e}")

def main():
    """الدالة الرئيسية"""
    try:
        logger.info("Starting AliExpress Affiliate Bot...")
        
        # إنشاء Updater
        updater = Updater(BOT_TOKEN, use_context=True)
        
        # الحصول على الـ Dispatcher
        dp = updater.dispatcher
        
        # إضافة المعالجات
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", help_command))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
        
        # بدء البوت
        logger.info("Bot is running and ready...")
        updater.start_polling()
        updater.idle()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")

if __name__ == '__main__':
    main()