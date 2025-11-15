import os
import telebot
import requests
import sqlite3
import logging
from flask import Flask, request
from telebot import types

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)

# إعداد البوت
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    logging.error("❌ BOT_TOKEN not found in environment variables")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# قاعدة البيانات البسيطة
def init_db():
    conn = sqlite3.connect('bot_data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, username TEXT, join_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS links 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, original_url TEXT, 
                  affiliate_url TEXT, created_at TEXT)''')
    conn.commit()
    conn.close()

init_db()

# أوامر البوت
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or "زائر"
    
    # حفظ المستخدم
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id, username, join_date) VALUES (?, ?, datetime("now"))', 
              (user_id, username))
    conn.commit()
    conn.close()
    
    welcome_text = f"""
🎯 **مرحباً {username}!**

🤖 **بوت AliExpress الافليت المتكامل**

📦 **المميزات:**
• تحويل روابط إلى روابط تابعة
• تتبع الشحنات
• إحصائيات الأداء
• دعم متعدد اللغات

🔧 **كيفية الاستخدام:**
1. أرسل رابط منتج AliExpress
2. سأحوله إلى رابط تابع
3. اربح العمولات!

💡 **الأوامر:**
/start - بدء البوت
/help - المساعدة
/stats - إحصائياتك
    """
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('🔄 تحويل رابط')
    btn2 = types.KeyboardButton('📊 إحصائياتي')
    btn3 = types.KeyboardButton('📖 المساعدة')
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
📖 **دليل الاستخدام:**

1. **تحويل الروابط:**
   - أرسل رابط منتج AliExpress
   - مثال: `https://www.aliexpress.com/item/1005005000000000.html`

2. **تتبع الشحنات:**
   - أرسل رقم التتبع
   - مثال: `LB123456789CN`

3. **الإحصائيات:**
   - استخدم /stats لرؤية أدائك

🔗 **المنصات المدعومة:**
• AliExpress
• Amazon
• eBay
"""
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['stats'])
def show_stats(message):
    user_id = message.from_user.id
    
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM links WHERE user_id = ?', (user_id,))
    links_count = c.fetchone()[0]
    
    c.execute('SELECT join_date FROM users WHERE user_id = ?', (user_id,))
    join_date = c.fetchone()
    
    conn.close()
    
    stats_text = f"""
📊 **إحصائياتك الشخصية**

👤 **المستخدم:** @{message.from_user.username or 'زائر'}
🔗 **الروابط المحولة:** {links_count}
📅 **تاريخ الانضمام:** {join_date[0] if join_date else 'غير معروف'}

🎯 **استمر في العمل!**
"""
    bot.reply_to(message, stats_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == '🔄 تحويل رابط')
def ask_for_link(message):
    bot.reply_to(message, "📥 أرسل لي رابط منتج AliExpress لتحويله:")

@bot.message_handler(func=lambda message: message.text == '📊 إحصائياتي')
def stats_button(message):
    show_stats(message)

@bot.message_handler(func=lambda message: message.text == '📖 المساعدة')
def help_button(message):
    send_help(message)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text
    
    if 'aliexpress.com' in text:
        # تحويل الرابط
        convert_url(message, text)
    elif text.startswith('LB') or len(text) in [13, 15]:
        # تتبع شحنة
        track_shipment(message, text)
    else:
        bot.reply_to(message, "❌ لم أفهم طلبك. أرسل رابط منتج أو رقم تتبع.")

def convert_url(message, original_url):
    """تحويل الرابط إلى رابط افليت"""
    try:
        wait_msg = bot.reply_to(message, "🔄 جاري تحويل الرابط...")
        
        # محاكاة تحويل الرابط (استبدل بـ API حقيقي)
        product_id = extract_product_id(original_url)
        
        if product_id:
            affiliate_url = f"https://s.click.aliexpress.com/e/_D{product_id}"
            
            # حفظ في قاعدة البيانات
            conn = sqlite3.connect('bot_data.db')
            c = conn.cursor()
            c.execute('INSERT INTO links (user_id, original_url, affiliate_url, created_at) VALUES (?, ?, ?, datetime("now"))',
                     (message.from_user.id, original_url, affiliate_url))
            conn.commit()
            conn.close()
            
            # إعداد النتيجة
            result_text = f"""
✅ **تم تحويل الرابط بنجاح!**

🔗 **الرابط التابع:**
`{affiliate_url}`

💰 **ابدأ بمشاركته لكسب العمولات!**
"""
            markup = types.InlineKeyboardMarkup()
            copy_btn = types.InlineKeyboardButton("📋 نسخ الرابط", callback_data=f"copy_{affiliate_url}")
            share_btn = types.InlineKeyboardButton("📤 مشاركة", url=f"https://t.me/share/url?url={affiliate_url}")
            markup.add(copy_btn, share_btn)
            
            bot.edit_message_text(result_text, message.chat.id, wait_msg.message_id, 
                                parse_mode='Markdown', reply_markup=markup)
        else:
            bot.edit_message_text("❌ لم أتمكن من استخراج معرف المنتج من الرابط", 
                                message.chat.id, wait_msg.message_id)
            
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {str(e)}")

def extract_product_id(url):
    """استخراج معرف المنتج من الرابط"""
    import re
    patterns = [
        r'/item/(\d+)\.html',
        r'product-(\d+)',
        r'/(\d+)\.html'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def track_shipment(message, tracking_number):
    """تتبع الشحنة"""
    try:
        wait_msg = bot.reply_to(message, f"🔍 جاري تتبع الشحنة {tracking_number}...")
        
        # محاكاة التتبع (استبدل بـ GTiT API)
        tracking_info = {
            'number': tracking_number,
            'status': 'In Transit',
            'location': 'China',
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'estimated_delivery': '2024-01-15'
        }
        
        result_text = f"""
📦 **معلومات التتبع**

🆔 **رقم التتبع:** `{tracking_info['number']}`
📊 **الحالة:** {tracking_info['status']}
📍 **الموقع:** {tracking_info['location']}
⏰ **آخر تحديث:** {tracking_info['last_update']}
📅 **التوصيل المتوقع:** {tracking_info['estimated_delivery']}
"""
        bot.edit_message_text(result_text, message.chat.id, wait_msg.message_id, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ في التتبع: {str(e)}")

# ويبهوك للسيرفر
@app.route('/')
def home():
    return "🤖 Bot is running on Render!"

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'OK'

# تشغيل البوت
if __name__ == '__main__':
    logging.info("🚀 Starting bot on Render...")
    # إعداد ويبهوك للسيرفر
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.environ.get('RENDER_APP_NAME', 'your-app')}.onrender.com/webhook")
    app.run(host="0.0.0.0", port=5000)