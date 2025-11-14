from aiogram import Bot, Dispatcher, executor, types
import aiohttp

TELEGRAM_TOKEN = "6986501751:AAF0Ra1lpXvdob21IQ9QORLCpclXPUPFyes"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

async def aliexpress_search(keyword):
    # مثال بسيط، يمكنك تعديل الرابط إلى API رسمي لاحقًا
    url = f"https://api.aliexpress.com/v2/api?method=aliexpress.affiliate.product.query&keywords={keyword}&app_key=503368"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            return await r.json()

@dp.message_handler()
async def handle_message(message: types.Message):
    keyword = message.text.strip()
    await message.answer("🔍 جاري البحث …")
    
    data = await aliexpress_search(keyword)
    items = data.get("resp_result", {}).get("result", {}).get("products", [])

    if not items:
        await message.answer("❌ لم يتم العثور على منتجات.")
        return

    for item in items[:3]:
        title = item.get("product_title", "بدون عنوان")
        link = item.get("promotion_link", "")
        img = item.get("product_main_image_url", "")

        if img:
            await message.answer_photo(photo=img, caption=f"{title}\n{link}")
        else:
            await message.answer(f"{title}\n{link}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)