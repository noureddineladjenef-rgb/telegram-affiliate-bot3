import logging
import aiohttp
import hashlib
import time
import re
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()

# الحصول على المتغيرات البيئية
BOT_TOKEN = os.environ.get("8548245901:AAHtOUGOZfXFvANxFzxgaGBUP34bS6cNAiQ")
APP_KEY = os.environ.get("503368")
APP_SECRET = os.environ.get("OMIS6a8bKcWrUsu5Bsr34NooT9yYwB3q")

# التحقق من وجود المتغيرات
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not found! Please set it in .env file")
if not APP_KEY:
    raise ValueError("❌ APP_KEY not found! Please set it in .env file")
if not APP_SECRET:
    raise ValueError("❌ APP_SECRET not found! Please set it in .env file")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

API_URL = "https://gw.api.alibaba.com/openapi/param2/2/portals.open/api.createPromotionLink/"

def generate_sign(params):
    """توقيع الطلب API"""
    sorted_params = "".join(f"{k}{v}" for k, v in sorted(params.items()))
    to_sign = APP_SECRET + sorted_params + APP_SECRET
    return hashlib.md5(to_sign.encode()).hexdigest().upper()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /start"""
    await update.message.reply_text(
        "🛍️ **مرحباً بكم في بوت AliExpress!**\n\n"
        "أرسل لي رابط أي منتج من AliExpress وسأحولها إلى رابط إحالة (Affiliate)\n\n"
        "**Examples:**\n"
        "• https://www.aliexpress.com/item/1005005000000000.html\n"
        "• https://a.aliexpress.com/_mKXyz123"
    )

def is_valid_aliexpress_url(url):
    """التحقق من صحة روابط AliExpress"""
    patterns = [
        r'https?://(www\.)?aliexpress\.(com|ru|fr|de|es|it)/item/',
        r'https?://a\.aliexpress\.com/_.*',
        r'https?://[a-z]+\.aliexpress\.com/.*item.*'
    ]
    
    for pattern in patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    return False

async def generate_affiliate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إنشاء رابط الإحالة"""
    user_id = update.message.from_user.id
    product_url = update.message.text.strip()
    
    logger.info(f"User {user_id} sent URL: {product_url}")

    # التحقق من صحة الرابط
    if not is_valid_aliexpress_url(product_url):
        await update.message.reply_text(
            "❌ **رابط غير صالح!**\n\n"
            "يرجى إرسال رابط منتج صحيح من AliExpress.\n\n"
            "**أمثلة:**\n"
            "• https://www.aliexpress.com/item/1234567890.html\n"
            "• https://a.aliexpress.com/_mABC123"
        )
        return

    # إعلام المستخدم بأن المعالجة جارية
    processing_msg = await update.message.reply_text("⏳ جاري معالجة الرابط...")

    # إعداد معلمات API
    params = {
        "app_key": APP_KEY,
        "timestamp": str(int(time.time() * 1000)),
        "targetUrl": product_url,
        "format": "json",
    }

    try:
        params["sign"] = generate_sign(params)
    except Exception as e:
        logger.error(f"Error generating sign: {e}")
        await processing_msg.edit_text("❌ خطأ في إنشاء التوقيع الأمني")
        return

    # إرسال طلب API
    async with aiohttp.ClientSession() as session:
        try:
            await processing_msg.edit_text("🔄 جاري الاتصال بخدمة AliExpress...")
            
            async with session.get(API_URL, params=params, timeout=30) as resp:
                if resp.status != 200:
                    await processing_msg.edit_text(f"❌ خطأ في الخادم: {resp.status}")
                    return
                
                data = await resp.json()
                logger.info(f"API Response for user {user_id}: {data}")

                # معالجة الاستجابة
                if "error" in data:
                    error_code = data.get("error_code", "Unknown")
                    error_msg = data.get("error_message", "Unknown error")
                    await processing_msg.edit_text(
                        f"❌ **خطأ من AliExpress:**\n\n"
                        f"**Code:** {error_code}\n"
                        f"**Message:** {