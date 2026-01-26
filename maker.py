import os, sys, asyncio, glob, importlib.util, __main__, subprocess
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from config import api_id, api_hash

# إعدادات البوت والمجلدات
BOT_TOKEN = "8136996400:AAEO4uDFUweXXiz49bs91hI_jmvBqh8CStI"
SESSION_DB = "database.txt" # لحفظ السيزونات النصية
OLD_SESSION_FILE = "session.session" # ملف الجلسة الذي وجدته

bot = TelegramClient('MakerBot', api_id, api_hash).start(bot_token=BOT_TOKEN)

if not hasattr(__main__, 'active_sessions'):
    __main__.active_sessions = {}

async def load_plugins(user_client):
    __main__.client = user_client
    files = glob.glob("plugins/**/*.py", recursive=True)
    for f in files:
        if f.endswith("__init__.py"): continue
        name = os.path.basename(f)[:-3]
        try:
            spec = importlib.util.spec_from_file_location(name, f)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as e: print(f"❌ Error loading {name}: {e}")

# دالة تشغيل الحسابات (من الملف أو السيزون)
async def start_all_accounts():
    # 1. محاولة تشغيل ملف الجلسة التقليدي إذا وجد
    if os.path.exists(OLD_SESSION_FILE):
        try:
            c = TelegramClient("session", api_id, api_hash)
            await c.connect()
            if await c.is_user_authorized():
                print("✅ تم تشغيل الحساب من ملف session.session")
                await load_plugins(c)
                asyncio.create_task(c.run_until_disconnected())
        except Exception as e: print(f"⚠️ فشل تشغيل ملف الجلسة: {e}")

    # 2. تشغيل الحسابات من قاعدة بيانات السيزونات النصية
    if os.path.exists(SESSION_DB):
        with open(SESSION_DB, "r") as f:
            for s in f.readlines():
                s = s.strip()
                if s:
                    try:
                        c = TelegramClient(StringSession(s), api_id, api_hash)
                        await c.connect()
                        if await c.is_user_authorized():
                            await load_plugins(c)
                            asyncio.create_task(c.run_until_disconnected())
                            print("✅ تم تشغيل حساب من database.txt")
                    except Exception as e: print(f"⚠️ فشل سيزون نصي: {e}")

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    buttons = [
        [Button.inline("➕ إضافة حساب (رقم)", data="add_acc")],
        [Button.inline("🔄 تحديث السورس وإعادة تشغيل", data="restart")],
        [Button.inline("📊 إحصائيات", data="stats")]
    ]
    await event.respond("☭ **مرحباً بك في لوحة تحكم نيثرون** ☭\n\nالسورس الآن يدعم الحفظ التلقائي للجلسات.", buttons=buttons)

@bot.on(events.CallbackQuery)
async def callback(event):
    data = event.data.decode('utf-8')
    
    if data == "add_acc":
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("📱 أرسل الرقم مع رمز الدولة:")
            p_res = await conv.get_response()
            phone = p_res.text.replace(" ", "")
            
            # نستخدم StringSession لضمان سهولة النقل والحفظ
            client = TelegramClient(StringSession(), api_id, api_hash)
            await client.connect()
            try:
                await client.send_code_request(phone)
                await conv.send_message("📥 أرسل الكود:")
                c_res = await conv.get_response()
                await client.sign_in(phone, c_res.text)
                
                # حفظ السيزون فوراً في ملف خارجي للأمان
                with open(SESSION_DB, "a") as f:
                    f.write(client.session.save() + "\n")
                
                await conv.send_message("✅ تم الربط بنجاح! الحساب الآن محفوظ ولن يطلب كود مرة أخرى.")
                await load_plugins(client)
                asyncio.create_task(client.run_until_disconnected())
            except Exception as e:
                await conv.send_message(f"❌ خطأ: {str(e)}")

    elif data == "restart":
        await event.answer("🔄 جاري التحديث وإعادة التشغيل...", alert=True)
        try: subprocess.run(["git", "pull", "--force"], check=True)
        except: pass
        os.execl(sys.executable, sys.executable, *sys.argv)

# تشغيل المهام
loop = asyncio.get_event_loop()
loop.create_task(start_all_accounts())
print("🚀 سورس نيثرون قيد التشغيل...")
bot.run_until_disconnected()
