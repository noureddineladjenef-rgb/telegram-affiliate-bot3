import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# التوكن والمعرف
BOT_TOKEN = "8548245901:AAHtOUGOZfXFvANxFzxgaGBUP34bS6cNAiQ"
AFFILIATE_ID = "WXwrOePAXsTmqIRPvlxtfTAg45jDFtxC"

class AffiliateBot:
    def __init__(self):
        self.affiliate_id = AFFILIATE_ID
    
    def convert_to_affiliate(self, product_url: str) -> str:
        """
        دالة لتحويل رابط المنتج إلى رابط أفليت
        """
        try:
            encoded_url = requests.utils.quote(product_url)
            affiliate_link = f"https://s.click.aliexpress.com/e/{self.affiliate_id}?url={encoded_url}"
            return affiliate_link
        except Exception as e:
            logger.error(f"Error converting link: {e}")
            return None
    
    def is_valid_aliexpress_link(self, url: str) -> bool:
        """
        التحقق من أن الرابط من AliExpress
        """
        return 'aliexpress.com' in url and 'item' in url

# إنشاء كائن البوت
affiliate_bot = AffiliateBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🛍️ *مرحباً بك في بوت تحويل روابط AliExpress* 🛍️

🤖 *ماذا أستطيع أن أفعل؟*
• تحويل روابط منتجات AliExpress إلى روابط أفليت
• مساعدتك في كسب العمولات من التسويق

📌 *كيفية الاستخدام؟*
1. أرسل لي رابط أي منتج من AliExpress
2. سأحوله لك إلى رابط أفليت
3. شارك الرابط واكسب العمولات!

🎯 *مثال للرابط:*
https://www.aliexpress.com/item/1005006123456789.html

🚀 *ابدأ الآن بإرسال الرابط!*
    """
    await update.message.reply_text(welcome_text)

async def convert_to_affiliate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    logger.info(f"Received message from user {update.effective_user.id}: {user_message}")
    
    if not affiliate_bot.is_valid_aliexpress_link(user_message):
        error_text = """
❌ *رابط غير مدعوم*

⚠️ يرجى إرسال رابط منتج صالح من AliExpress

📌 *شروط الرابط الصحيح:*
• يجب أن يكون من موقع aliexpress.com
• يجب أن يحتوي على /item/
• مثال صحيح: https://www.aliexpress.com/item/1005006123456789.html
        """
        await update.message.reply_text(error_text)
        return
    
    try:
        affiliate_link = affiliate_bot.convert_to_affiliate(user_message)
        
        if affiliate_link:
            success_text = f"""
✅ *تم تحويل الرابط بنجاح!*

🛒 *الرابط الأصلي:*
`{user_message}`

🎯 *رابط الأفليت الجديد:*
`{affiliate_link}`

💰 *كيفية الاستفادة:*
1. شارك هذا الرابط مع الآخرين
2. عند الشراء عبر الرابط، ستحصل على عمولة
3. تتبع أرباحك من خلال منصة الأفليت
            """
            await update.message.reply_text(success_text)
        else:
            await update.message.reply_text("❌ حدث خطأ أثناء تحويل الرابط")
            
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ غير متوقع")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 *دليل استخدام البوت*

🔹 *الأوامر المتاحة:*
/start - بدء استخدام البوت
/help - عرض هذه الرسالة

🔹 *طريقة العمل:*
1. ابحث عن منتج تريد تسويقه في AliExpress
2. انسخ رابط المنتج من المتصفح
3. أرسل الرابط للبوت
4. سيُعيد لك رابط الأفليت الجديد
    """
    await update.message.reply_text(help_text)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

def main():
    try:
        logger.info("Starting AliExpress Affiliate Bot...")
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert_to_affiliate))
        application.add_error_handler(error_handler)
        logger.info("Bot is running...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")

if __name__ == '__main__':
    main()