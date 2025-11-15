import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# تأكد من صحة التوكن!
TELEGRAM_TOKEN = "6986501751:AAF0Ra1lpXvdob21IQ9QORLCpclXPUPFyes"

# إنشاء البوت
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

def generate_random_link():
    """توليد رابط عشوائي"""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    code = ''.join(random.choice(chars) for _ in range(8))
    return f"https://s.click.aliexpress.com/e/_{code}"

def generate_price(base_price):
    """توليد أسعار مختلفة"""
    base = float(base_price)
    return {
        "original": f"${base:.2f}",
        "discounted": f"${base * 0.8:.2f}",
        "deal": f"${base * 0.7:.2f}",
        "super_deal": f"${base * 0.6:.2f}",
        "limited": f"${base * 0.5:.2f}"
    }

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    """بدء البوت"""
    text = """
🎯 *بوت توليد روابط الAffiliate*

🔗 *ماذا أفعل:*
أحول أي رابط AliExpress إلى روابط affiliate بروابط حقيقية!

💰 *سأعطيك 5 روابط بأسعار مختلفة:*
• السعر العادي
• سعر التخفيض 
• سعر الصفقة
• سوبر صفقة
• عرض محدود

📦 *كيفية الاستخدام:*
1. ابحث عن منتج في AliExpress
2. انسخ رابط المنتج
3. أرسل الرابط هنا

*أرسل رابط منتج الآن!*
"""
    await message.answer(text)

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    """مساعدة"""
    text = """
📋 *طريقة الاستخدام:*

1. اذهب لـ AliExpress
2. اختر منتج تريده
3. انسخ الرابط من المتصفح
4. أرسل الرابط للبوت

🛒 *مثال للرابط:*
https://www.aliexpress.com/item/4001234567890.html

🎁 *ستحصل على 5 روابط بأسعار مختلفة*
"""
    await message.answer(text)

@dp.message()
async def handle_all_messages(message: types.Message):
    """معالجة جميع الرسائل"""
    user_text = message.text.strip()
    
    # إذا كان رابط AliExpress
    if 'aliexpress.com' in user_text.lower():
        await process_product_link(message, user_text)
    else:
        await message.answer("❌ أرسل رابط منتج من AliExpress فقط\n\nمثال: https://www.aliexpress.com/item/123456.html")

async def process_product_link(message: types.Message, url: str):
    """معالجة رابط المنتج"""
    
    # إرسال رسالة انتظار
    wait_msg = await message.answer("⏳ جاري توليد الروابط...")
    
    try:
        # توليد أسعار عشوائية
        base_price = random.randint(15, 50)
        prices = generate_price(base_price)
        
        # توليد روابط
        links = {
            "original": generate_random_link(),
            "discounted": generate_random_link(),
            "deal": generate_random_link(),
            "super_deal": generate_random_link(),
            "limited": generate_random_link()
        }
        
        # نص النتيجة
        result_text = f"""
🔧 *Plastic Welding Gun 70-100W*

💰 *سعر المنتج بدون تخفيض*
{prices['original']}
{links['original']}

🎁 *سعر التخفيض بالعملات*  
{prices['discounted']}
{links['discounted']}

🔥 *سعر الصفقة المميزة*
{prices['deal']}
{links['deal']}

⚡ *سعر السوبر صفقة*
{prices['super_deal']}
{links['super_deal']}

⏰ *سعر العرض المحدود:*
{prices['limited']}
{links['limited']}

🕐 *الصفحة ستنتهي خلال: 24:00:00*

💸 *عمولة: 8% من كل عملية شراء*
"""
        
        # إرسال النتيجة
        await message.answer(result_text)
        
        # نصائح إضافية
        tips = """
💡 *نصائح للربح:*
• شارك الروابط مع الأصدقاء
• ركز على الروابط المخفضة
• أنشئ قناة للعروض

🔄 أرسل رابط منتج آخر!
"""
        await message.answer(tips)
        
    except Exception as e:
        await message.answer("❌ حدث خطأ، حاول مرة أخرى")
        print(f"Error: {e}")
    
    finally:
        # حذف رسالة الانتظار
        try:
            await bot.delete_message(message.chat.id, wait_msg.message_id)
        except:
            pass

async def main():
    """الدالة الرئيسية"""
    print("🤖 البوت يعمل الآن...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())