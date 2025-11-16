import logging
import aiohttp
import hashlib
import time
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# استخدام Environment Variables
BOT_TOKEN = os.environ.get("8548245901:AAHtOUGOZfXFvANxFzxgaGBUP34bS6cNAiQ")
APP_KEY = os.environ.get("503368")
APP_SECRET = os.environ.get("OMIS6a8bKcWrUsu5Bsr34NooT9yYwB3q")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AliExpress Open API endpoint
API_URL = "https://gw.api.alibaba.com/openapi/param2/2/portals.open/api.createPromotionLink/"

def generate_sign(params):
    sorted_params = "".join(f"{k}{v}" for k, v in sorted(params.items()))
    to_sign = APP_SECRET + sorted_params + APP_SECRET
    return hashlib.md5(to_sign.encode()).hexdigest().upper()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً! أرسل لي أي رابط منتج من AliExpress وسأعطيك رابط أفلييت مباشر."
    )

async def generate_affiliate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_url = update.message.text.strip()

    if "aliexpress" not in product_url:
        await update.message.reply_text("يرجى إرسال رابط صالح من AliExpress.")
        return

    params = {
        "app_key": APP_KEY,
        "timestamp": int(time.time() * 1000),
        "targetUrl": product_url,
        "format": "json",
    }

    params["sign"] = generate_sign(params)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(API_URL, params=params) as resp:
                data = await resp.json()
                logger.info(data)

                try:
                    affiliate_link = data["promotionLink"]["promotionUrl"]
                    await update.message.reply_text(f"✅ رابط الأفلييت:\n{affiliate_link}")
                except:
                    await update.message.reply_text(
                        "فشل استخراج رابط الأفلييت. تحقق من APP_KEY و APP_SECRET أو من الرابط."
                    )
        except Exception as e:
            logger.error(e)
            await update.message.reply_text(
                "خطأ في الاتصال بالـ API. تأكد من صحة APP_KEY و APP_SECRET."
            )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_affiliate))
    app.run_polling()

if __name__ == "__main__":
    main()