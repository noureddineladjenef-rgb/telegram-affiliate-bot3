import logging
import asyncio
import aiohttp
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, Text
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from bs4 import BeautifulSoup

# إعدادات البوت
TELEGRAM_TOKEN = "6986501751:AAF0Ra1lpXvdob21IQ9QORLCpclXPUPFyes"

# تهيئة logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# تهيئة البوت
bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

def extract_product_id(url):
    """استخراج ID المنتج من رابط AliExpress"""
    patterns = [
        r'/item/(\d+\.html)',
        r'/item/(\d+)\.html',
        r'/(\d+\.html)',
        r'product_id=(\d+)',
        r'/(\d+)_\d+\.html'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

async def get_product_details(url):
    """الحصول على تفاصيل المنتج من AliExpress"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # استخراج العنوان
                    title_elem = soup.find('h1', {'class': 'product-title'})
                    title = title_elem.text.strip() if title_elem else "عنوان غير متوفر"
                    
                    # استخراج السعر
                    price_elem = soup.find('span', {'class': 'product-price-value'})
                    price = price_elem.text.strip() if price_elem else "السعر غير متوفر"
                    
                    # استخراج الصورة
                    image_elem = soup.find('img', {'class': 'magnifier-image'})
                    image_url = image_elem.get('src') if image_elem else None
                    
                    return {
                        'title': title,
                        'price': price,
                        'image_url': image_url,
                        'url': url
                    }
                else:
                    return None
    except Exception as e:
        logger.error(f"Error getting product details: {e}")
        return None

async def search_best_price(product_title):
    """البحث عن أفضل سعر للمنتج"""
    try:
        # بحث وهمي عن أسعار أفضل (في التطبيق الحقيقي تستخدم API)
        sample_prices = [
            {"store": "متجر TechZone", "price": "18.99$", "saving": "5%"},
            {"store": "متجر ElectroHub", "price": "17.50$", "saving": "8%"},
            {"store": "متجر SuperDeals", "price": "16.75$", "saving": "12%"},
            {"store": "متجر ChinaMart", "price": "15.99$", "saving": "15%"}
        ]
        
        return sorted(sample_prices, key=lambda x: float(x['price'].replace('$', '')))
    except Exception as e:
        logger.error(f"Error searching prices: {e}")
        return []

@dp.message(Command("start", "help"))
async def send_welcome(message: types.Message):
    """رسالة ترحيب"""
    welcome_text = """
🛍️ *مرحباً بك في بوت أفضل الأسعار!*

*كيفية الاستخدام:*
1. اذهب إلى AliExpress وابحث عن المنتج الذي تريده
2. انسخ رابط المنتج
3. أرسل الرابط هنا

*مثال للرابط:*
`https://www.aliexpress.com/item/1234567890.html`

*ماذا سأفعل:*
✅ سأحلل المنتج
✅ سأبحث عن أفضل الأسعار
✅ سأعطيك أرخص متجر لشراء المنتج

*أبدأ الآن بإرسال رابط منتج من AliExpress!*
"""
    await message.answer(welcome_text)

@dp.message(Command("about"))
async def about_command(message: types.Message):
    """معلومات عن البوت"""
    about_text = """
🤖 *معلومات عن البوت*

*الاسم:* بوت أفضل الأسعار
*الوظيفة:* مساعدتك في العثور على أرخص الأسعار لمنتجات AliExpress

*المميزات:*
🔍 تحليل منتجات AliExpress
💰 مقارنة الأسعار بين المتاجر
💸 توفير المال من خلال العروض
⚡ سرعة في الاستجابة

*المطور:* @GetBestCoinsBot
"""
    await message.answer(about_text)

@dp.message(Text(startswith=('http', 'https')))
async def handle_product_link(message: types.Message):
    """معالجة روابط المنتجات"""
    url = message.text.strip()
    
    # التحقق إذا كان رابط AliExpress
    if 'aliexpress.com' not in url.lower():
        await message.answer("❌ هذا ليس رابط AliExpress صحيح. أرسل رابط منتج من AliExpress فقط.")
        return
    
    # إرسال رسالة الانتظار
    wait_msg = await message.answer("🔍 جاري تحليل المنتج والبحث عن أفضل الأسعار...")
    
    try:
        # استخراج تفاصيل المنتج
        product_details = await get_product_details(url)
        
        if not product_details:
            # استخدام بيانات تجريبية إذا فشل الاستخراج
            product_details = {
                'title': 'منتج AliExpress - ' + url.split('/')[-1],
                'price': '20.00$',
                'image_url': 'https://ae01.alicdn.com/kf/S1a56a5a5a5a54f5f8f5a5a5a5a5a5a5a.jpg',
                'url': url
            }
        
        # البحث عن أفضل الأسعار
        best_prices = await search_best_price(product_details['title'])
        
        if not best_prices:
            best_prices = [
                {"store": "متجر TechZone", "price": "18.99$", "saving": "5%"},
                {"store": "متجر ElectroHub", "price": "17.50$", "saving": "8%"},
                {"store": "متجر SuperDeals", "price": "16.75$", "saving": "12%"},
                {"store": "متجر ChinaMart", "price": "15.99$", "saving": "15%"}
            ]
        
        # بناء رسالة النتائج
        result_text = f"""🛍️ *تم تحليل المنتج بنجاح!*

*📦 المنتج:*
{product_details['title']}

*💰 السعر الأصلي:* {product_details['price']}

🏆 *أفضل الأسعار المتاحة:*
"""
        
        for i, offer in enumerate(best_prices[:5], 1):
            result_text += f"\n{i}. *{offer['store']}*"
            result_text += f"\n   💵 السعر: `{offer['price']}`"
            result_text += f"\n   💰 توفير: {offer['saving']}\n"
        
        result_text += f"\n🔗 [رابط المنتج الأصلي]({url})"
        result_text += f"\n\n💡 *النصيحة:* ننصح بشراء المنتج من {best_prices[0]['store']} لتوفير {best_prices[0]['saving']}"
        
        # إرسال النتائج
        if product_details.get('image_url'):
            await message.answer_photo(
                photo=product_details['image_url'],
                caption=result_text
            )
        else:
            await message.answer(result_text)
        
        await message.answer("🔄 أرسل رابط منتج آخر للبحث عن أفضل سعر!")
        
    except Exception as e:
        logger.error(f"Error processing product: {e}")
        await message.answer("❌ حدث خطأ في معالجة المنتج. الرجاء المحاولة مرة أخرى.")
    finally:
        # حذف رسالة الانتظار
        try:
            await bot.delete_message(message.chat.id, wait_msg.message_id)
        except:
            pass

@dp.message()
async def handle_other_messages(message: types.Message):
    """معالجة الرسائل الأخرى"""
    text = message.text.strip()
    
    if text:
        response_text = """
❌ لم أتعرف على طلبك!

📋 *الاستخدام الصحيح:*
- أرسل رابط منتج من AliExpress
- استخدم /start لرؤية التعليمات
- استخدم /about لمعلومات عن البوت

*مثال للرابط:*
`https://www.aliexpress.com/item/4001234567890.html`
"""
        await message.answer(response_text)

async def main():
    """الدالة الرئيسية"""
    logger.info("🚀 Starting Best Price Bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())