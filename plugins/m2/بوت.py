import os, sys, asyncio, glob, importlib.util, __main__, subprocess, json, re, random
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from datetime import datetime, timedelta

# استيراد الإعدادات (تأكد من وجود ملف config.py)
try:
    from config import api_id, api_hash
except:
    api_id = 1234567 # حط ايديك هنا اذا ماكو ملف
    api_hash = "hash_here"

# --- [1] الإعدادات الأساسية ---
BOT_TOKEN = "8136996400:AAEO4uDFUweXXiz49bs91hI_jmvBqh8CStI"
COMP_BOT_TOKEN = "ضع_توكن_بوت_المسابقات_هنا" # حط التوكن الجديد هنا

SESSION_DB = "database.txt" 
USERS_DB = "nethron_vips.json"
CODES_FILE = "nethron_codes.txt" 
SUDO_IDS = [5580918933, 7273666832]

# --- [2] تعريف البوتات (بدون await هنا لتجنب خطأ الصورة) ---
bot = TelegramClient('MakerBot', api_id, api_hash)
comp_bot = TelegramClient('CompBot', api_id, api_hash)

# --- [3] نظام تحميل الملحقات (Plugins) ---
async def load_plugins(user_client):
    files = glob.glob("plugins/**/*.py", recursive=True)
    for f in files:
        if f.endswith("__init__.py"): continue
        name = os.path.basename(f)[:-3]
        try:
            spec = importlib.util.spec_from_file_location(name, f)
            mod = importlib.util.module_from_spec(spec)
            mod.client = user_client
            # تثبيت الكلاينت في المودول ليعمل بشكل صحيح
            spec.loader.exec_module(mod)
        except Exception as e:
            print(f"❌ فشل تحميل {name}: {e}")

# --- [4] تشغيل الحسابات المسجلة تلقائياً ---
async def start_all_accounts():
    if os.path.exists(SESSION_DB):
        with open(SESSION_DB, "r") as f:
            for s in f.read().splitlines():
                if not s.strip(): continue
                try:
                    c = TelegramClient(StringSession(s), api_id, api_hash)
                    await c.connect()
                    if await c.is_user_authorized():
                        await load_plugins(c)
                        asyncio.create_task(c.run_until_disconnected())
                except: pass

# --- [5] أوامر بوت المسابقات الجديد (comp_bot) ---
@comp_bot.on(events.NewMessage(pattern='/start'))
async def comp_start(event):
    btns = [
        [Button.inline("📊 نقاطي", data="pts"), Button.inline("🏆 المتصدرين", data="top")],
        [Button.url("📢 قناة السورس", "https://t.me/NETH_RON")]
    ]
    await event.reply("🏆 **مساعد مسابقات عراق ثون الرسمي**\nاضغط على الأزرار أدناه:", buttons=btns)

# --- [6] أوامر بوت التنصيب (bot) ---
@bot.on(events.NewMessage(pattern='/start'))
async def main_start(event):
    await event.reply("🚀 **بوت التنصيب شغال بنجاح!**")

# --- [7] المحرك الرئيسي (حل مشكلة الصورة) ---
async def main():
    # تشغيل البوتات بشكل صحيح باستخدام await
    await bot.start(bot_token=BOT_TOKEN)
    await comp_bot.start(bot_token=COMP_BOT_TOKEN)
    
    print("✅ تم تشغيل بوت التنصيب وبوت المسابقات بنجاح!")
    
    # تشغيل الحسابات
    await start_all_accounts()
    
    # الحفاظ على تشغيل الكل
    await asyncio.gather(
        bot.run_until_disconnected(),
        comp_bot.run_until_disconnected()
    )

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except Exception as e:
        print(f"❌ خطأ قاتل: {e}")
