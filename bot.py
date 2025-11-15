import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# الحصول على التوكن من متغير البيئة
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8548245901:AAHtOUGOZfXFvANxFzxgaGBUP34bS6cNAiQ')
AFFILIATE_ID = "WXwrOePAXsTmqIRPvlxtfTAg45jDFtxC"

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context):
    welcome_text = """
🛍️ *مرحباً بك في بوت تحويل روابط AliExpress* 🛍️

فقط أرسل لي رابط أي منتج من AliExpress وسأحوله لك إلى رابط أفليت!

📌 *مثال:*
https://www.aliexpress.com/item/xxxxxxxxx.html

🚀 ابدأ بإرسال الرابط الآن!
    """
    await update.message.reply_text(welcome_text)

async def convert_to_affiliate(update: Update, context):
    user_message = update.message.text.strip()
    
    if 'aliexpress.com' in user_message and 'item' in user_message:
        try:
            encoded_url = requests.utils.quote(user_message)
            affiliate_link = f"https://s.click.aliexpress.com/e/{AFFILIATE_ID}?url={encoded_url}"
            
            result_text = f"""
✅ *تم تحويل الرابط بنجاح!*

🎯 *رابط الأفليت الجديد:*
`{affiliate_link}`

📊 *يمكنك استخدام هذا الرابط للمشاركة والربح من العمولات!*
            """
            await update.message.reply_text(result_text)
            
        except Exception as e:
            await update.message.reply_text("❌ حدث خطأ أثناء تحويل الرابط")
            logger.error(f"Error: {e}")
    else:
        await update.message.reply_text("❌ يرجى إرسال رابط منتج من AliExpress فقط")

def main():
    # إنشاء التطبيق
    application = Application.builder().token(BOT_TOKEN).build()
    
    # إضافة handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert_to_affiliate))
    
    # بدء البوت
    logger.info("البوت يعمل الآن على Render...")
    application.run_polling()

if __name__ == '__main__':
    main()