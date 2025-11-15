import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode

# توكن البوت
TELEGRAM_TOKEN = "6986501751:AAF0Ra1lpXvdob21IQ9QORLCpclXPUPFyes"

# تهيئة البوت
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# قائمة العروض والكوبونات
COUPONS = [
    {
        "title": "🛍️ كوبون خصم 10$ على أول طلب",
        "code": "WELCOME10",
        "discount": "10$",
        "description": "خصم 10 دولار على أول طلب من AliExpress",
        "link": "https://s.click.aliexpress.com/e/_DkzQ9eB"
    },
    {
        "title": "🔥 كوبون خصم 15% على الإلكترونيات",
        "code": "ELECTRO15", 
        "discount": "15%",
        "description": "خصم 15% على جميع الإلكترونيات والهواتف",
        "link": "https://s.click.aliexpress.com/e/_DkzQ9eB"
    },
    {
        "title": "🎁 عرض خاص على الملابس",
        "code": "FASHION20",
        "discount": "20%",
        "description": "خصم 20% على الملابس والأزياء",
        "link": "https://s.click.aliexpress.com/e/_DkzQ9eB"
    },
    {
        "title": "💎 كوبون مجاني للشحن",
        "code": "FREESHIP",
        "discount": "شحن مجاني",
        "description": "شحن مجاني على الطلبات فوق 20$",
        "link": "https://s.click.aliexpress.com/e/_DkzQ9eB"
    }
]

@dp.message(Command("start"))
async def start_command(message: types.Message):
    """رسالة ترحيب"""
    welcome_text = """
🎉 *مرحباً بك في بوت العروض والكوبونات!*

*ماذا أقدم:*
✅ أكواد خصم حصرية
🔥 عروض خاصة من AliExpress
💸 توفير في المشتريات

*الأوامر المتاحة:*
/start - بدء البوت
/coupons - جميع الكوبونات
/offers - أحدث العروض
/help - المساعدة

*اختر /coupons لرؤية جميع أكواد الخصم!*
"""
    await message.answer(welcome_text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("coupons"))
async def coupons_command(message: types.Message):
    """عرض جميع الكوبونات"""
    coupons_text = "🎁 *أكواد الخصم المتاحة:*\n\n"
    
    for i, coupon in enumerate(COUPONS, 1):
        coupons_text += f"{i}. *{coupon['title']}*\n"
        coupons_text += f"   📦 {coupon['description']}\n"
        coupons_text += f"   💰 الخصم: {coupon['discount']}\n"
        coupons_text += f"   🏷️ الكود: `{coupon['code']}`\n\n"
    
    coupons_text += "🔗 *طريقة الاستخدام:*\n"
    coupons_text += "1. انقر على رابط المنتج\n"
    coupons_text += "2. أضف الكود أثناء الدفع\n"
    coupons_text += "3. استمتع بالخصم!\n\n"
    coupons_text += "📱 *لرؤية العروض:* /offers"
    
    await message.answer(coupons_text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("offers"))
async def offers_command(message: types.Message):
    """عرض العروض الخاصة"""
    offers_text = """
🔥 *أحدث العروض الخاصة:*

🛒 *عرض اليوم:*
• خصم 50% على الإلكترونيات
• شحن مجاني لجميع الطلبات
• عروض التخفيضات الكبرى

📱 *عروض الهواتف:*
• هواتف ذكية بأسعار مذهلة
• إكسسوارات مجانية مع الشراء
• ضمان لمدة عام

👕 *عروض الأزياء:*
• ملابس صيفية بأسعار مخفضة
• خصم 30% على الأحذية
• تشكيلة جديدة من الحقائب

💎 *عروض المجوهرات:*
• ذهب ومجوهرات بأسعار منافسة
• خصم 25% على الساعات
• هدايا مجانية مع الشراء

🎯 *لرؤية أكواد الخصم:* /coupons
"""
    
    # إرسال صورة مع العرض
    await message.answer_photo(
        photo="https://ae01.alicdn.com/kf/S12345678901234567890123456789012.jpg",
        caption=offers_text,
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(Command("help"))
async def help_command(message: types.Message):
    """تعليمات المساعدة"""
    help_text = """
📋 *كيفية استخدام البوت:*

1. */coupons* - رؤية جميع أكواد الخصم
2. */offers* - رؤية أحدث العروض
3. */start* - إعادة بدء البوت

💡 *نصائح مهمة:*
• الأكواد صالحة لمدة محدودة
• يمكن استخدام كل كود مرة واحدة
• العروض تتجدد يومياً

🛒 *للشراء من AliExpress:*
1. اختر المنتج الذي تريده
2. انسخ كود الخصم
3. أضف الكود أثناء الدفع
4. استمتع بالتوفير!

📞 *للاستفسار:* @coupons213_bot
"""
    await message.answer(help_text, parse_mode=ParseMode.MARKDOWN)

@dp.message()
async def handle_all_messages(message: types.Message):
    """رد على أي رسالة"""
    text = """
🎊 *مرحباً بك في بوت العروض!*

اختر أحد الأوامر التالية:

/coupons - 🎁 أكواد الخصم
/offers - 🔥 العروض الخاصة  
/help - 📋 المساعدة

أو انقر على /start للبدء!
"""
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

async def main():
    """تشغيل البوت"""
    print("🚀 البوت يعمل الآن...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())