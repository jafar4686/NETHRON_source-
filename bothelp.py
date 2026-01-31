import asyncio
from telethon import TelegramClient, events, Button

# --- [1] استدعاء الإعدادات تلقائياً ---
try:
    # راح يسحب الـ api_id والـ api_hash من ملف الكونفج مالتك الأصلي كبل
    from config import api_id, api_hash
except ImportError:
    print("❌ خطأ: ملف config.py غير موجود!")
    exit()

# حط توكن بوت المسابقات الجديد هنا
BOT_TOKEN = "8579454046:AAGn52vlNAwQzaRx-ABWfMnBTppv1ckmCds" 

# --- [2] تعريف وتشغيل البوت كبل ---
# سميناه HelperBot حتى ما يتصادم وية ملفات الجلسة القديمة
bot = TelegramClient('HelperBotSession', api_id, api_hash)

# --- [3] أوامر البوت ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    # رد بسيط وفول أوبشن بالأزرار
    await event.reply(
        "👋 **هلا بيك يابة!**\n\n"
        "أنا البوت المساعد التابع لسورس **نيثرون**.\n"
        "شغال مية بالمية ومنفصل عن بوت التنصيب.",
        buttons=[
            [Button.url("📢 قناة السورس", "https://t.me/NETH_RON")],
            [Button.inline("📊 إحصائياتي", data="stats")]
        ]
    )

@bot.on(events.CallbackQuery(data="stats"))
async def stats(event):
    await event.answer("جاري جلب البيانات من ملفات السورس... ⚡", alert=True)

# --- [4] التشغيل التلقائي الفول ---
async def main():
    print("🚀 جاري تشغيل البوت المساعد...")
    await bot.start(bot_token=BOT_TOKEN)
    print("✅ البوت اشتغل كبل وبدون تسجيل رقم!")
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
