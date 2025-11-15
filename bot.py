import os
import logging
from flask import Flask, request

# محاولة استيراد المكتبات مع معالجة الأخطاء
try:
    import telebot
    from telebot import types
    TELEBOT_AVAILABLE = True
except ImportError as e:
    logging.error(f"Telebot import error: {e}")
    TELEBOT_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# إعداد التطبيق
app = Flask(__name__)

# تهيئة البوت إذا كانت المكتبات متاحة
if TELEBOT_AVAILABLE:
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    if BOT_TOKEN:
        bot = telebot.TeleBot(BOT_TOKEN)
    else:
        logging.error("BOT_TOKEN not found")
        bot = None
else:
    bot = None
    logging.error("pyTelegramBotAPI is not installed")

# صفحة الرئيسية
@app.route('/')
def home():
    if not TELEBOT_AVAILABLE:
        return "❌ Error: pyTelegramBotAPI not installed. Check requirements.txt"
    elif not BOT_TOKEN:
        return "❌ Error: BOT_TOKEN not set in environment variables"
    else:
        return "✅ Bot is running on Render!"

# ويبهوك للتلغرام
@app.route('/webhook', methods=['POST'])
def webhook():
    if not bot:
        return "Bot not initialized", 500
    
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'OK'

# أوامر البوت (فقط إذا كان البوت متاحاً)
if bot:
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        if bot:
            bot.reply_to(message, "🎯 البوت يعمل بنجاح على Render!")

# تشغيل التطبيق
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    if bot and BOT_TOKEN:
        # إعداد ويبهوك للسيرفر
        webhook_url = f"https://{os.environ.get('RENDER_APP_NAME', 'your-app')}.onrender.com/webhook"
        try:
            bot.remove_webhook()
            bot.set_webhook(url=webhook_url)
            logging.info(f"Webhook set to: {webhook_url}")
        except Exception as e:
            logging.error(f"Webhook error: {e}")
    
    app.run(host='0.0.0.0', port=port, debug=False)