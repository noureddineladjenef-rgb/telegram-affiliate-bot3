import logging
import aiohttp
import hashlib
import time
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

# -------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN") or "8548245901:AAHtOUGOZfXFvANxFzxgaGBUP34bS6cNAiQ"
APP_KEY = os.environ.get("APP_KEY") or "503368"
APP_SECRET = os.environ.get("APP_SECRET") or "OMIS6a8bKcWrUsu5Bsr34NooT9yYwB3q"
# -------------------------------

if not BOT_TOKEN or not APP_KEY or not APP_SECRET:
    raise ValueError("❌ BOT_TOKEN, APP_KEY, or APP_SECRET not set!")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "https://gw.api.alibaba.com/openapi/param2/2/portals.open/api.createPromotionLink/"

def generate_sign(params):
    sorted_params = "".join(f"{k}{v}" for k, v in sorted(params.items()))
    to_sign = APP_SECRET + sorted_params + APP_SECRET
    return hashlib.md5(to_sign.encode()).hexdigest().upper()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send me an AliExpress product link and I will generate an affiliate link for you."
    )

def convert_short_link(url):
    """Convert a short AliExpress link (a.aliexpress.com/...) to a full product URL if possible."""
    if "a.aliexpress.com" in url:
        # This is a basic conversion; for full reliability, use requests to follow redirect
        return url.replace("a.aliexpress.com/", "www.aliexpress.com/item/")
    return url

async def generate_affiliate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_url = update.message.text.strip()
    logger.info(f"Received URL: {product_url}")

    product_url = convert_short_link(product_url)

    if "aliexpress" not in product_url:
        await update.message.reply_text("Please send a valid AliExpress product URL.")
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
        await update.message.reply_text("Error generating the signature. Check APP_SECRET.")
        return

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(API_URL, params=params) as resp:
                data = await resp.json()
                logger.info(f"API status: {resp.status}")
                logger.info(f"API response: {data}")

                # Show full API response for debugging
                await update.message.reply_text(f"🔍 API Response:\n{data}")

                try:
                    affiliate_link = data["promotionLink"]["promotionUrl"]
                    await update.message.reply_text(f"✅ Affiliate link:\n{affiliate_link}")
                except Exception as e:
                    logger.error(f"Failed to extract affiliate link: {e}")
                    await update.message.reply_text(
                        "❌ Failed to extract affiliate link. Check APP_KEY, APP_SECRET, or the product URL.\n"
                        "🔍 See the previous API response for details."
                    )
        except Exception as e:
            logger.error(f"API connection error: {e}")
            await update.message.reply_text("Error connecting to the AliExpress API.")

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