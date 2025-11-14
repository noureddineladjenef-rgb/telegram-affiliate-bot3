import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import aiohttp
import hashlib
import time

TELEGRAM_TOKEN = "6986501751:AAF0Ra1lpXvdob21IQ9QORLCpclXPUPFyes"
APP_ID = "503368"
APP_SECRET = "WXwrOePAXsTmqIRPvlxtfTAg45jDFtxC"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

def sign(params, app_secret):
    keys = sorted(params.keys())
    base = app_secret + ''.join(f"{k}{params[k]}" for k in keys) + app_secret
    return hashlib.md5(base.encode("utf-8")).hexdigest().upper()

async def aliexpress_search(keyword):
    url = "https://api.aliexpress.com/v2/api"
    params = {
        "method": "aliexpress.affiliate.product.query",
        "app_key": APP_ID,
        "timestamp": int(time.time()),
        "keywords": keyword,
        "fields": "product_title,product_main_image_url,product_url,promotion_link"
    }
    params["sign"] = sign(params, APP_SECRET)

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as r:
            return await r.json()

@dp.message_handler()
async def handle_message(message: types.Message):
    keyword = message.text
    await message.answer("🔍 يتم البحث في AliExpress …")

    try:
        data = await aliexpress_search(keyword)
        items = data.get("resp_result", {}).get("result", {}).get("products", [])

        if not items:
            await message.answer("❌ لم يتم العثور على منتجات.")
            return

        for item in items[:3]:
            title = item.get("product_title", "بدون عنوان")
            img = item.get("product_main_image_url", "")
            link = item.get("promotion_link", "")
            text = f"📌 *{title}*
🔗 {link}"

            if img:
                await message.answer_photo(photo=img, caption=text, parse_mode="Markdown")
            else:
                await message.answer(text, parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"⚠️ خطأ أثناء جلب النتائج:
{e}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
