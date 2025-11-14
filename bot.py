import logging
from aiogram import Bot, Dispatcher, executor, types
import aiohttp
import hashlib
import time
import json

# التوكنات - تأكد من صحتها
TELEGRAM_TOKEN = "6986501751:AAF0Ra1lpXvdob21IQ9QORLCpclXPUPFyes"
APP_ID = "503368"
APP_SECRET = "WXwrOePAXsTmqIRPvlxtfTAg45jDFtxC"

# تهيئة logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

def generate_signature(params, app_secret):
    """إنشاء توقيع API"""
    try:
        # ترتيب المعاملات أبجديًا
        sorted_params = sorted(params.items())
        
        # بناء سلسلة للتوقيع
        base_string = app_secret
        for key, value in sorted_params:
            base_string += f"{key}{value}"
        base_string += app_secret
        
        # إنشاء توقيع MD5
        return hashlib.md5(base_string.encode('utf-8')).hexdigest().upper()
    except Exception as e:
        logger.error(f"Error generating signature: {e}")
        return None

async def search_aliexpress_products(keyword):
    """البحث عن منتجات في AliExpress"""
    try:
        # معلمات API
        params = {
            "app_key": APP_ID,
            "method": "aliexpress.affiliate.product.query",
            "sign_method": "md5",
            "timestamp": str(int(time.time() * 1000)),  # وقت بالمللي ثانية
            "format": "json",
            "v": "2.0",
            "keywords": keyword,
            "fields": "productId,productTitle,productMainImageUrl,productUrl,promotionLink,originalPrice,salePrice",
            "page_size": "3"
        }
        
        # إنشاء التوقيع
        signature = generate_signature(params, APP_SECRET)
        if not signature:
            return None
            
        params["sign"] = signature
        
        # عنوان API الجديد
        api_url = "https://api-sg.aliexpress.com/rest"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"API Response: {json.dumps(data, indent=2)}")
                    return data
                else:
                    logger.error(f"API Error: Status {response.status}")
                    return None
                    
    except aiohttp.ClientError as e:
        logger.error(f"Network error: {e}")
        return None
    except Exception as e:
        logger.error(f"Search error: {e}")
        return None

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """رسالة ترحيب"""
    welcome_text = """
    🛍️ *مرحباً بك في بوت AliExpress!*
    
    *كيفية الاستخدام:*
    فقط اكتب اسم المنتج الذي تريد البحث عنه وسأجد لك أفضل العروض.
    
    *أمثلة:*
    📱 `iphone case`
    💻 `laptop bag`
    ⌚ `smart watch`
    🎧 `bluetooth headphones`
    
    *ملاحظة:* سأعرض لك أول 3 نتائج من AliExpress.
    """
    await message.answer(welcome_text, parse_mode="Markdown")

@dp.message_handler()
async def handle_search(message: types.Message):
    """معالجة طلبات البحث"""
    keyword = message.text.strip()
    
    if len(keyword) < 2:
        await message.answer("⚠️ الرجاء إدخال كلمة بحث أطول (أكثر من حرفين)")
        return
    
    # إرسال رسالة الانتظار
    wait_msg = await message.answer("🔍 جاري البحث في AliExpress...")
    
    try:
        # البحث عن المنتجات
        data = await search_aliexpress_products(keyword)
        
        if not data:
            await message.answer("❌ حدث خطأ في الاتصال بالخدمة. الرجاء المحاولة لاحقاً.")
            return
        
        # التحقق من وجود أخطاء في الاستجابة
        error_response = data.get('error_response')
        if error_response:
            error_msg = error_response.get('msg', 'خطأ غير معروف في API')
            await message.answer(f"❌ خطأ في الخدمة: {error_msg}")
            return
        
        # استخراج المنتجات
        products = data.get('result', {}).get('products', [])
        
        if not products:
            await message.answer("❌ لم أجد أي منتجات تطابق بحثك. حاول بكلمات أخرى.")
            return
        
        # عرض المنتجات
        for i, product in enumerate(products[:3], 1):
            title = product.get('productTitle', 'بدون عنوان')
            image_url = product.get('productMainImageUrl', '')
            product_url = product.get('promotionLink', product.get('productUrl', ''))
            
            # تنظيف العنوان
            clean_title = title.replace('*', '').replace('_', '').replace('`', '').replace('[', '').replace(']', '')
            
            # بناء رسالة المنتج
            product_text = f"""
🛍️ *المنتج {i}:*
*{clean_title}*

🔗 [رابط الشراء على AliExpress]({product_url})
            """
            
            try:
                if image_url and image_url.startswith('http'):
                    await message.answer_photo(
                        photo=image_url,
                        caption=product_text,
                        parse_mode="Markdown"
                    )
                else:
                    await message.answer(product_text, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Error sending product {i}: {e}")
                await message.answer(product_text, parse_mode="Markdown")
        
        await message.answer("✅ اكتمل البحث! اكتب كلمة جديدة للبحث عن المزيد من المنتجات.")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await message.answer("⚠️ حدث خطأ غير متوقع. الرجاء المحاولة مرة أخرى.")
    finally:
        # حذف رسالة الانتظار
        try:
            await bot.delete_message(message.chat.id, wait_msg.message_id)
        except:
            pass

if __name__ == "__main__":
    logger.info("🚀 Starting AliExpress Bot...")
    executor.start_polling(dp, skip_updates=True)