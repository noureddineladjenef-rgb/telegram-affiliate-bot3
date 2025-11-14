import logging
from aiogram import Bot, Dispatcher, executor, types
import aiohttp
import hashlib
import time

# التوكنات والمفاتيح - يفضل استخدام environment variables
TELEGRAM_TOKEN = "6986501751:AAF0Ra1lpXvdob21IQ9QORLCpclXPUPFyes"
APP_ID = "503368"
APP_SECRET = "WXwrOePAXsTmqIRPvlxtfTAg45jDFtxC"

# تهيئة logging
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

def sign(params, app_secret):
    """إنشاء التوقيع للـ API"""
    keys = sorted(params.keys())
    base = app_secret + ''.join(f"{k}{params[k]}" for k in keys) + app_secret
    return hashlib.md5(base.encode("utf-8")).hexdigest().upper()

async def aliexpress_search(keyword):
    """البحث في AliExpress API"""
    url = "https://api.aliexpress.com/v2/api"
    params = {
        "method": "aliexpress.affiliate.product.query",
        "app_key": APP_ID,
        "timestamp": str(int(time.time())),  # تحويل إلى string
        "keywords": keyword,
        "fields": "product_title,product_main_image_url,product_url,promotion_link",
        "sign_method": "md5"
    }
    
    # إضافة التوقيع
    params["sign"] = sign(params, APP_SECRET)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=30) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logging.error(f"API Error: {response.status}")
                    return None
    except Exception as e:
        logging.error(f"Request failed: {e}")
        return None

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """ترحيب بالمستخدم"""
    welcome_text = """
    🛍️ مرحباً بك في بوت AliExpress!
    
    فقط اكتب اسم المنتج الذي تريد البحث عنه وسأجد لك أفضل العروض.
    
    مثال:
    `iphone case`
    `laptop bag`
    `smart watch`
    """
    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message_handler()
async def handle_message(message: types.Message):
    """معالجة رسائل المستخدم"""
    keyword = message.text.strip()
    
    if len(keyword) < 2:
        await message.answer("⚠️ الرجاء إدخال كلمة بحث longer (أكثر من حرفين)")
        return

    await message.answer("🔍 جاري البحث في AliExpress...")

    try:
        data = await aliexpress_search(keyword)
        
        if not data:
            await message.answer("❌ حدث خطأ في الاتصال بالخدمة. الرجاء المحاولة لاحقاً.")
            return

        # التحقق من هيكل البيانات
        result = data.get("resp_result", {})
        if "result" not in result:
            await message.answer("❌ لم يتم العثور على منتجات تطابق بحثك.")
            return

        items = result["result"].get("products", [])
        
        if not items:
            await message.answer("❌ لم يتم العثور على منتجات تطابق بحثك.")
            return

        # إرسال أول 3 نتائج
        for i, item in enumerate(items[:3], 1):
            title = item.get("product_title", "بدون عنوان")
            img = item.get("product_main_image_url", "")
            link = item.get("promotion_link", "")
            
            # تنظيف العنوان من الأحرف غير المرغوبة
            title = title.replace('*', '').replace('_', '').replace('`', '')
            
            text = f"""🛍️ **المنتج {i}**
📌 {title}

🔗 [رابط الشراء]({link})
"""

            if img:
                await message.answer_photo(
                    photo=img, 
                    caption=text, 
                    parse_mode="Markdown"
                )
            else:
                await message.answer(text, parse_mode="Markdown")
                
        await message.answer("✅ اكتمل البحث! اكتب كلمة جديدة للبحث عن منتجات أخرى.")

    except Exception as e:
        logging.error(f"Error: {e}")
        await message.answer("⚠️ حدث خطأ غير متوقع. الرجاء المحاولة مرة أخرى.")

if __name__ == "__main__":
    logging.info("Starting bot...")
    executor.start_polling(dp, skip_updates=True)