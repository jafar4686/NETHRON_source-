import os, sys, asyncio, glob, importlib.util, __main__, json
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession

# --- [1] الإعدادات الأساسية (تأكد من صحتها) ---
try:
    from config import api_id, api_hash
except:
    api_id = 21743603 # مثال: حط ايديك هنا
    api_hash = "61e38933224b7496181f26710787e682"

BOT_TOKEN = "8136996400:AAEO4uDFUweXXiz49bs91hI_jmvBqh8CStI"
COMP_BOT_TOKEN = "ضع_توكن_بوت_المسابقات_هنا" # <--- حط التوكن الجديد هنا

# --- [2] تعريف البوتات بأسماء جلسات مختلفة لمنع التعارض ---
bot = TelegramClient('MainMakerSession', api_id, api_hash)
comp_bot = TelegramClient('CompetitionBotSession', api_id, api_hash)

# --- [3] أوامر بوت التنصيب (الأساسي) ---
@bot.on(events.NewMessage(pattern='/start'))
async def main_bot_handler(event):
    await event.reply("🚀 **أهلاً بك في بوت التنصيب الرئيسي!**\nالسورس شغال الآن وبانتظار أوامرك.")

# --- [4] أوامر بوت المسابقات (الجديد) ---
@comp_bot.on(events.NewMessage(pattern='/start'))
async def comp_bot_handler(event):
    btns = [
        [Button.inline("📊 نقاطي", data="pts"), Button.inline("🏆 المتصدرين", data="top")],
        [Button.url("📢 قناة السورس", "https://t.me/NETH_RON")]
    ]
    await event.reply("🏆 **مساعد مسابقات عراق ثون**\nأنا البوت المخصص للمسابقات، كيف يمكنني مساعدتك؟", buttons=btns)

# --- [5] المحرك التشغيلي (الحل النهائي) ---
async def start_everything():
    print("🚀 جاري تشغيل الأنظمة...")
    
    # تشغيل البوت الأول
    await bot.start(bot_token=BOT_TOKEN)
    print("✅ بوت التنصيب: متصل")
    
    # تشغيل البوت الثاني
    await comp_bot.start(bot_token=COMP_BOT_TOKEN)
    print("✅ بوت المسابقات: متصل")
    
    # تشغيل حسابات السورس (إذا موجودة)
    if os.path.exists("database.txt"):
        # هنا تكدر تضيف دالة start_all_accounts() إذا ردتها
        print("ℹ️ جاري فحص جلسات الحسابات...")

    print("⚡ الكل شغال الآن.. أرسل /start للبوتين لتجربتهم!")
    
    # الحفاظ على الاتصال مفتوحاً للطرفين
    await asyncio.gather(
        bot.run_until_disconnected(),
        comp_bot.run_until_disconnected()
    )

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_everything())
