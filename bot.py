import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio
import aiohttp
import hashlib
import time

TELEGRAM_TOKEN = "6986501751:AAF0Ra1lpXvdob21IQ9QORLCpclXPUPFyes"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

async def search_aliexpress_direct(keyword):
    """بحث مباشر باستخدام AliExpress API"""
    try:
        # استخدام API مختلف أو طريقة بديلة
        # هذا مثال - تحتاج لتحديثه بـ API keys صحيحة
        url = "https://axapi.aliseeks.com/v1/search"
        
        headers = {
            "Content-Type": "application/json",
        }
        
        payload = {
            "keywords": keyword,
            "sort": "orders_desc",
            "limit": 3
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=30) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API Error: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"Search error: {e}")
        # إرجاع بيانات تجريبية في حالة الخطأ
        return {
            "products": [
                {
                    "title": f"{keyword} - منتج مميز",
                    "imageUrl": "https://via.placeholder.com/300",
                    "productUrl": "https://aliexpress.com",
                    "price": "29.99"
                }
            ]
        }

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("🛍️ أهلاً! اكتب اسم المنتج للبحث في AliExpress")

@dp.message()
async def handle_search(message: types.Message):
    keyword = message.text.strip()
    
    if len(keyword) < 2:
        await message.answer("⚠️ أدخل كلمة بحث أطول")
        return
        
    processing_msg = await message.answer("🔍 جاري البحث...")
    
    try:
        results = await search_aliexpress_direct(keyword)
        
        if results and "products" in results:
            for product in results["products"][:3]:
                text = f"🛍️ {product['title']}\n💰 {product['price']} USD\n🔗 [اشتري الآن]({product['productUrl']})"
                
                if product.get('imageUrl'):
                    await message.answer_photo(product['imageUrl'], caption=text)
                else:
                    await message.answer(text)
                    
            await message.answer("✅ اكتمل البحث!")
        else:
            await message.answer("❌ لم أجد نتائج. حاول بكلمات أخرى")
            
    except Exception as e:
        await message.answer("⚠️ حدث خطأ. حاول مرة أخرى")
    finally:
        await bot.delete_message(message.chat.id, processing_msg.message_id)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())