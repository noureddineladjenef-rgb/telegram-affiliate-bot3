# bot.py
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# معلومات البوت الخاصة بك
BOT_TOKEN = "6986501751:AAF0Ra11pXvdob21IQ9QORLCpc1XPUPFyes"

# معلومات AliExpress API
ALI_API_KEY = "WXwrOePAXsTmqIRPvlxtfTAg45jDFtxC"
ALI_PID = "503368"

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "مرحبا! 🚀\nأرسل رابط المنتج الذي تريد معرفة أقل سعر له."
    )

def get_lowest_price(product_url):
    """
    دالة للبحث عن أقل سعر عبر AliExpress Affiliate API
    """
    api_url = "https://api.taobao.com/router/rest"  # مثال، يمكن تغييره حسب مزود API
    params = {
        "method": "aliexpress.affiliate.product.query",
        "app_key": ALI_API_KEY,
        "pid": ALI_PID,
        "url": product_url,
        "format": "json"
    }
    try:
        response = requests.get(api_url, params=params, timeout=10)
        data = response.json()
        # تأكد من مسار البيانات حسب API
        if "result" in data and len(data["result"]) > 0:
            price = data["result"][0].get("min_price", "غير متوفر")
            title = data["result"][0].get("product_title", "المنتج")
            link = data["result"][0].get("product_url", product_url)
            return f"{title}\nأقل سعر: {price}\nرابط الشراء: {link}"
        else:
            return "عذرًا، لم أتمكن من العثور على سعر للمنتج."
    except Exception as e:
        return f"حدث خطأ أثناء البحث: {e}"

def handle_link(update: Update, context: CallbackContext):
    product_link = update.message.text
    update.message.reply_text("جاري البحث عن أفضل سعر... 🔍")
    result = get_lowest_price(product_link)
    update.message.reply_text(result)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add