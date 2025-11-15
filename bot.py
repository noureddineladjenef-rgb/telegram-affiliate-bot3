import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
import random
import re

# توكن البوت
TELEGRAM_TOKEN = "6986501751:AAF0Ra1lpXvdob21IQ9QORLCpclXPUPFyes"

# تهيئة البوت
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

def generate_affiliate_links(product_url, product_title, original_price):
    """توليد روابط affiliate متعددة بأسعار مختلفة"""
    
    # إنشاء أسعار عشوائية (في الواقع تستخدم API)
    prices = {
        "original": original_price,
        "discounted": f"${round(float(original_price.replace('$', '')) * 0.8, 2)}",
        "deal": f"${round(float(original_price.replace('$', '')) * 0.7, 2)}",
        "super_deal": f"${round(float(original_price.replace('$', '')) * 0.6, 2)}",
        "limited": f"${round(float(original_price.replace('$', '')) * 0.5, 2)}"
    }
    
    # إنشاء روابط affiliate عشوائية (في الواقع تستخدم API حقيقي)
    links = {
        "original": f"https://s.click.aliexpress.com/e/_{generate_random_code()}",
        "discounted": f"https://s.click.aliexpress.com/e/_{generate_random_code()}",
        "deal": f"https://s.click.aliexpress.com/e/_{generate_random_code()}",
        "super_deal": f"https://s.click.aliexpress.com/e/_{generate_random_code()}",
        "limited": f"https://s.click.aliexpress.com/e/_{generate_random_code()}"
    }
    
    return prices, links

def generate_random_code():
    """توليد كود عشوائي للرابط"""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return ''.join(random.choice(chars) for _ in range(8))

def extract_product_info(url):
    """استخراج معلومات المنتج من الرابط"""
    # في الواقع تستخدم web scraping أو API
    # هنا نستخدم بيانات عشوائية للتوضيح
    
    sample_titles = [
        "Kunststoff-Schweißgerät 70-100W Heißhefter Stoßstange",
        "PVC Schweißer Auto Stoßstange Reparatursatz",
        "Plastic Welding Gun Repair Tool Kit",
        "Hot Stapler Bumper Repair Welding Machine"
    ]
    
    sample_prices = ["$25.99", "$34.50", "$19.99", "$42.75", "$28.30"]
    
    return {
        "title": random.choice(sample_titles),
        "original_price": random.choice(sample_prices),
        "image": "https://ae01.alicdn.com/kf/Sabc123def456.jpg"
    }

@dp.message(Command("start"))
async def start_command(message: types.Message):
    """رسالة ترحيب"""
    welcome_text = """
🔗 *بوت توليد روابط الAffiliate*

🎯 *ماذا أفعل:*
أحول روابط AliExpress إلى روابط affiliate بأسعار مميزة!

💰 *أنواع الأسعار:*
• السعر العادي
• سعر التخفيض 
• سعر الصفقة
• السوبر صفقة
• العرض المحدود

📦 *كيفية الاستخدام:*
1. أرسل رابط منتج من AliExpress
2. سأولد لك 5 روابط بأسعار مختلفة
3. اختر الأنسب واحصل على عمولة!

*أرسل رابط منتج الآن للبدء!*
"""
    await message.answer(welcome_text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("help"))
async def help_command(message: types.Message):
    """تعليمات المساعدة"""
    help_text = """
📋 *تعليمات الاستخدام:*

1. *ابحث عن منتج* في AliExpress
2. *انسخ رابط المنتج* من المتصفح
3. *أرسل الرابط* للبوت
4. *احصل على 5 روابط* بأسعار مختلفة

🛒 *مثال للرابط:*
`https://www.aliexpress.com/item/4001234567890.html`

💰 *معدل العمولة:* حتى 8% من كل عملية شراء

🔗 *شارك الروابط* واكسب عمولة!
"""
    await message.answer(help_text, parse_mode=ParseMode.MARKDOWN)

@dp.message(lambda message: message.text and 'aliexpress.com' in message.text)
async def handle_product_link(message: types.Message):
    """معالجة روابط المنتجات"""
    url = message.text.strip()
    
    # إرسال رسالة الانتظار
    processing_msg = await message.answer("🔄 جاري توليد روابط الaffiliate...")
    
    try:
        # استخراج معلومات المنتج
        product_info = extract_product_info(url)
        
        # توليد الروابط والأسعار
        prices, links = generate_affiliate_links(
            url, 
            product_info["title"], 
            product_info["original_price"]
        )
        
        # بناء رسالة النتائج
        result_text = f"""
🛠️ *{product_info['title']}*

💰 *سعر المنتج بدون تخفيض*
{prices['original']}
{links['original']}

🎁 *سعر التخفيض بالعملات*  
{prices['discounted']}
{links['discounted']}

🔥 *سعر الهدل ديلز*
{prices['deal']}
{links['deal']}

⚡ *سعر السوبر ديلز*
{prices['super_deal']}
{links['super_deal']}

⏰ *سعر العرض المحدود:*
{prices['limited']}
{links['limited']}

🕐 *الصفحة ستنتهي خلال: 24:00:00*

💸 *معدل العمولة: 8% من كل عملية شراء*
"""
        
        # إرسال النتائج مع صورة المنتج
        await message.answer_photo(
            photo=product_info['image'],
            caption=result_text,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # إرسال تعليمات إضافية
        tips_text = """
💡 *نصائح للربح:*
• شارك الروابط على وسائل التواصل
• ركز على الروابط ذات الأسعار المخفضة
• استهدف العملاء المهتمين بالمنتج

🔄 أرسل رابط منتج آخر لتوليد روابط جديدة!
"""
        await message.answer(tips_text, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logging.error(f"Error: {e}")
        await message.answer("❌ حدث خطأ في معالجة الرابط. تأكد من صحة الرابط وحاول مرة أخرى.")
    
    finally:
        # حذف رسالة الانتظار
        try:
            await bot.delete_message(message.chat.id, processing_msg.message_id)
        except:
            pass

@dp.message()
async def handle_other_messages(message: types.Message):
    """معالجة الرسائل الأخرى"""
    response_text = """
❌ لم أتعرف على رابط منتج!

📋 *الاستخدام الصحيح:*
- أرسل رابط منتج من AliExpress فقط
- مثال: `https://www.aliexpress.com/item/1234567890.html`

🔧 *الأوامر المتاحة:*
/start - بدء البوت
/help - التعليمات

*انسخ رابط منتج من AliExpress وأرسله الآن!*
"""
    await message.answer(response_text, parse_mode=ParseMode.MARKDOWN)

async def main():
    """تشغيل البوت"""
    logging.info("🚀 بدء تشغيل بوت الAffiliate...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())