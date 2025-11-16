import logging
import aiohttp
import hashlib
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# -------------------------------
# معلوماتك الخاصة
BOT_TOKEN = "8548245901:AAHtOUGOZfXFvANxFzxgaGBUP34bS6cNAiQ"
APP_KEY = "503368"
APP_SECRET = "OMIS6a8bKcWrUsu5Bsr34NooT9yYwB3q"
# -------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "https://gw.api.alibaba.com/openapi/param2/2/portals.open/api.createPromotionLink/"

def generate_sign(params):
    sorted_params = "".join(f"{k}{v}" for k, v in sorted(params.items()))
    to_sign = APP_SECRET + sorted_params + APP_SECRET
    return hashlib.md5(to_sign.encode()).hexdigest().upper()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً! أرسل لي رابط منتج من AliExpress وسأعطيك رابط أفلييت."
    )
    logger.info(f"User {update.effective_user.username} started the bot.")

async def generate_affiliate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_url = update.message.text.strip()
    logger.info(f"Received URL: {product_url} from {update.effective_user.username}")

    if "aliexpress" not in product_url:
        await update.message.reply_text("يرجى إرسال رابط صالح من AliExpress.")
        return

    params = {
        "app_key": APP_KEY,
        "timestamp": int(time.time() * 1000),
        "targetUrl": product_url,
        "format": "json",
    }

    try:
        params["sign"] = generate_sign(params)
    except Exception as e:
        logger.error(f"Error generating sign: {e}")
        await update.message.reply_text("خطأ في توليد التوقيع. تحقق من APP_SECRET.")
        return

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(API_URL, params=params) as resp:
                logger.info(f"API status: {resp.status}")
                data = await resp.json()
                logger.info(f"API response: {data}")

                try:
                    affiliate_link = data["promotionLink"]["promotionUrl"]
                    await update.message.reply_text(f"✅ رابط الأفلييت:\n{affiliate_link}")
                except Exception as e:
                    logger.error(f"Failed to extract affiliate link: {e}")
                    await update.message.reply_text(
                        "فشل استخراج رابط الأفلييت. تحقق من APP_KEY و APP_SECRET أو الرابط."
                    )
        except Exception as e:
            logger.error(f"API connection error: {e}")
            await update.message.reply_text("خطأ في الاتصال بالـ API.")

def main():
    logger.info("Starting bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_affiliate))

    try:
        app.run_polling()
    except Exception as e:
        logger.error(f"Bot failed to run: {e}")

if __name__ == "__main__":
    main()