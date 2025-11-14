import logging
from aiogram import Bot, Dispatcher, executor, types
import aiohttp
import hashlib
from datetime import datetime
import asyncio

# إعدادات البوت وAliExpress
TELEGRAM_TOKEN = "6986501751:AAF0Ra1lpXvdob21IQ9QORLCpclXPUPFyes"
APP_ID = "503368"
APP_SECRET = "WXwrOePAXsTmqIRPvlxtfTAg45jDFtxC"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# دالة إنشاء التوقيع
def sign(params, app_secret):
    keys = sorted(params.keys())
    base = app_secret + ''.join(f"{k}{params[k]}" for k in keys) + app_secret
    return hashlib.md5(base.encode("utf-8")).hexdigest().upper()

# البحث في AliExpress
async def aliexpress_search(keyword):
    url = "https://api.aliexpress.com/v2/api"
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    params = {
        "method": "aliexpress.affiliate.product.query",
        "app_key": APP_ID,
        "timestamp": timestamp,
        "keywords": keyword,
        "fields": "product_title,product_main_image_url,product_url,promotion_link"
    }
    params["sign"] = sign(params, APP_SECRET)

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as r:
            try:
                return await r.json()
            except Exception as e:
                logging.error(f"خطأ في قراءة JSON: {e}")
                return {}

# التعامل مع الرسائل
@dp.message_handler()
async def handle_message(message: types.Message):
    keyword = message.text.strip()
    await message.answer("🔍 يتم البحث في AliExpress …")

    try:
        data = await aliexpress_search(keyword)
        items = data.get("resp_result", {}).get("result", {}).get("products", [])

        if not items:
            await message.answer("❌ لم يتم العثور على منتجات.")
            return

        for item in items[:3]:
            title = item.get("product_title", "بدون عنوان").replace("_", "\\_").replace("*", "\\*")
            img = item.get("product_main_image_url", "")
            link = item.get("promotion_link", "")
            text = f"📌 *{title}*\n🔗 {link}"

            if img:
                await message.answer_photo(photo=img, caption=text, parse_mode="MarkdownV2")
            else:
                await message.answer(text, parse_mode="MarkdownV2")

    except Exception as e:
        logging.error(f"Error: {e}")
        await message.answer(f"⚠️ خطأ أثناء جلب النتائج:\n{e}")

# تشغيل البوت
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)