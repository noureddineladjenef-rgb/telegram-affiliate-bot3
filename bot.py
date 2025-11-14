import os
from aiogram import Bot, Dispatcher, types, executor
import requests

# قراءة المتغيرات من GitHub Secrets أو Environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
AFFILIATE_ID = os.getenv("AFFILIATE_ID")
TRACKING_API_KEY = os.getenv("TRACKING_API_KEY")  # اختياري

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ===== رابط الأفليت =====
def generate_affiliate_link(product_url):
    return f"{product_url}?aff_fcid={AFFILIATE_ID}"

# ===== start =====
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply(
        "👋 أهلاً! أرسل رقم التتبع أو رابط المنتج.\n"
        "سأعطيك حالة الشحنة أو رابط أفليت تلقائي."
    )

# ===== handler =====
@dp.message_handler()
async def handler(message: types.Message):
    text = message.text.strip()

    # إذا رابط منتج → نحوله أفليت
    if text.startswith("http"):
        link = generate_affiliate_link(text)
        await message.reply(f"🔗 رابط أفليت جاهز:\n{link}")
        return

    # إذا رقم تتبع → API
    tracking = text
    try:
        # ضع API التتبع الحقيقي لاحقاً
        response = requests.get(
            f"https://api.example.com/track/{tracking}?key={TRACKING_API_KEY}"
        )
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "لا توجد بيانات متاحة")