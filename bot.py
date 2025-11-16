import logging
import aiohttp
import hashlib
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# بيانات البوت والأفلييت
BOT_TOKEN = "8548245901:AAHtOUGOZfXFvANxFzxgaGBUP34bS6cNAiQ"
APP_KEY = "503368"
APP_SECRET = "OMIS6a8bKcWrUsu5Bsr34NooT9yYwB3q"

API_URL = "https://gw.api.alibaba.com/openapi/param2/2/portals.open/api.createPromotionLink/"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# توليد توقيع الطلب (signature)
def generate_sign(params: dict) -> str:
    sorted_params = "".join(f"{k}{v}" for k, v in sorted(params.items()))
    to_sign = APP_SECRET + sorted_params + APP_SECRET
    return hashlib.md5(to_sign.encode()).hexdigest().upper()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛍️ مرحباً بك! أرسل لي رابط منتج AliExpress وسأعطيك رابط أفلييت صالح."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_url = update.message.text.strip()
    user_id = update.message.from_user.id

    # التحقق من صحة الرابط
    if "aliexpress" not in product_url.lower():
        await update.message.reply_text("❌ الرجاء إرسال رابط صحيح من AliExpress فقط.")
        return

    processing_msg = await update.message.reply_text("⏳ جاري إنشاء رابط الأفلييت...")

    # إعداد معلمات API
    params = {
        "app_key": APP_KEY,
        "timestamp": str(int(time.time() * 1000)),
        "targetUrl": product_url,
        "format": "json",
    }

    params["sign"] = generate_sign(params)

    # إرسال الطلب
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(API_URL, params=params, timeout=30) as resp:
                if resp.status != 200:
                    await processing_msg.edit_text(f"❌ خطأ في الخادم: {resp.status}")
                    return

                data = await resp.json()
                logger.info(f"API Response for user {user_id}: {data}")

                # التحقق من وجود رابط صحيح في الاستجابة
                if "result" in data and "promotionLink" in data["result"]:
                    affiliate_link = data["result"]["promotionLink"]
                    await processing_msg.edit_text(f"🔗 رابط الأفلييت الخاص بك:\n{affiliate_link}")
                else:
                    await processing_msg.edit_text("❌ لم يتم إنشاء رابط أفلييت. تأكد من الرابط أو بيانات API.")

        except Exception as e:
            logger.error(f"Error while calling API: {e}")
            await processing_msg.edit_text(f"❌ حدث خطأ أثناء الاتصال بالـ API:\n{e}")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()


if __name__ == "__main__":
    main()