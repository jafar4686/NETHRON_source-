import os, sys, asyncio, glob, importlib.util, __main__, subprocess
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from config import api_id, api_hash

# توكن البوت الخاص بك
BOT_TOKEN = "8136996400:AAEO4uDFUweXXiz49bs91hI_jmvBqh8CStI"
bot = TelegramClient('MakerBot', api_id, api_hash).start(bot_token=BOT_TOKEN)

# ملف تخزين الجلسات (قاعدة بيانات بسيطة)
SESSION_DB = "database.txt"

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

# دالة لحفظ السيزون في الملف
def save_session(session_str):
    with open(SESSION_DB, "a") as f:
        f.write(session_str + "\n")

# دالة لتشغيل الحسابات المحفوظة عند بداية التشغيل
async def load_saved_sessions():
    if os.path.exists(SESSION_DB):
        with open(SESSION_DB, "r") as f:
            sessions = f.readlines()
            for s in sessions:
                s = s.strip()
                if s:
                    try:
                        client = TelegramClient(StringSession(s), api_id, api_hash)
                        await client.connect()
                        if await client.is_user_authorized():
                            await load_plugins(client)
                            asyncio.create_task(client.run_until_disconnected())
                            print(f"✅ تم إعادة تشغيل حساب محفوظ.")
                    except Exception as e:
                        print(f"❌ فشل تشغيل حساب محفوظ: {e}")

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    buttons = [
        [Button.inline("➕ إضافة حساب", data="add_acc")],
        [Button.inline("🔄 تحديث السورس (GitHub)", data="restart")],
        [Button.inline("📊 الإحصائيات", data="stats")]
    ]
    await event.respond("☭ **لوحة تحكم نيثرون المطور** ☭", buttons=buttons)

@bot.on(events.CallbackQuery)
async def callback(event):
    data = event.data.decode('utf-8')
    chat_id = event.chat_id

    if data == "add_acc":
        async with bot.conversation(chat_id) as conv:
            await conv.send_message("📱 **أرسل رقم الهاتف مع رمز الدولة (مثال: +964...):**")
            response = await conv.get_response()
            phone = response.text.replace(" ", "")

            await conv.send_message("⏳ جاري طلب كود التحقق...")
            client = TelegramClient(StringSession(), api_id, api_hash)
            await client.connect()
            
            try:
                await client.send_code_request(phone)
                await conv.send_message("📥 **أرسل الكود الآن:**")
                code_res = await conv.get_response()
                await client.sign_in(phone, code_res.text)
                
                # حفظ الجلسة في الملف فور النجاح
                session_str = client.session.save()
                save_session(session_str)
                
                if chat_id not in __main__.active_sessions:
                    __main__.active_sessions[chat_id] = []
                __main__.active_sessions[chat_id].append(client)
                
                await conv.send_message("✅ **تم الربط وحفظ الجلسة بنجاح! جرب `.فحص` الآن.**")
                await load_plugins(client)
                asyncio.create_task(client.run_until_disconnected())
                
            except Exception as e:
                await conv.send_message(f"❌ فشل: {str(e)}")

    elif data == "restart":
        await event.answer("🔄 جاري سحب التحديثات وإعادة التشغيل...", alert=True)
        try:
            # سحب التحديثات من المستودع
            subprocess.run(["git", "pull", "--force"], check=True)
            # إعادة تشغيل السكريبت بالكامل
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            await event.respond(f"❌ خطأ أثناء التحديث: {e}")

    elif data == "stats":
        total = sum(len(v) for v in __main__.active_sessions.values())
        await event.answer(f"📊 الإحصائيات: {total} حساب نشط", alert=True)

print("--- Source Nethron Started ---")
# تشغيل الحسابات القديمة عند بدء الميكر
loop = asyncio.get_event_loop()
loop.create_task(load_saved_sessions())
bot.run_until_disconnected()
