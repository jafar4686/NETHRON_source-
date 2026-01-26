import os, sys, asyncio, glob, importlib.util, __main__, subprocess, json
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from datetime import datetime, timedelta
from config import api_id, api_hash
from keys import load_keys, save_keys # استدعاء ملف المفاتيح

# --- الإعدادات ---
BOT_TOKEN = "8136996400:AAEO4uDFUweXXiz49bs91hI_jmvBqh8CStI"
SESSION_DB = "database.txt"
USERS_DB = "nethron_vips.json"
SUDO_ID = 5580918933
SUDO2_ID = 7273666832

bot = TelegramClient('MakerBot', api_id, api_hash).start(bot_token=BOT_TOKEN)

if not hasattr(__main__, 'active_sessions'):
    __main__.active_sessions = {}

# --- وظائف الإدارة والتحقق ---
def load_users():
    if not os.path.exists(USERS_DB): return {}
    with open(USERS_DB, "r") as f: return json.load(f)

def save_users(data):
    with open(USERS_DB, "w") as f: json.dump(data, f, indent=4)

def is_subscribed(uid):
    if uid in [SUDO_ID, SUDO2_ID]: return True
    users = load_users()
    if str(uid) in users:
        return datetime.fromisoformat(users[str(uid)]) > datetime.now()
    return False

# --- الكود الأصلي لتشغيل الحسابات والبلكنز ---
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

async def start_all_accounts():
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
                    except: pass

# --- واجهة المستخدم (START) ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    uid = event.sender_id
    msg = "★──────────☭──────────★\n   ☭ • **𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 𝑉𝐼𝑃** • ☭\n★──────────☭──────────★"
    
    if is_subscribed(uid):
        buttons = [[Button.inline("📱 فتح لوحة التحكم", data="open_panel")]]
    else:
        buttons = [[Button.inline("🔑 تفعيل الاشتراك بالكود", data="activate_code")]]
    await event.respond(msg, buttons=buttons)

# --- معالجة الأزرار (لوحة التحكم الأصلية) ---
@bot.on(events.CallbackQuery)
async def callback(event):
    data = event.data.decode('utf-8')
    uid = event.sender_id

    if data == "activate_code":
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("🎟️ أرسل كود التفعيل:")
            code = (await conv.get_response()).text.strip()
            keys = load_keys()
            for serial, kdata in keys.items():
                if kdata["code"] == code and kdata["status"] == "available":
                    # شريط التحميل
                    p = await conv.send_message("🔄 جاري التفعيل... `▒▒▒▒▒ 0%`")
                    for i in range(1, 6):
                        await asyncio.sleep(0.3)
                        await p.edit(f"🔄 جاري التفعيل... `{'█'*i}{'▒'*(5-i)} {i*20}%`️")
                    
                    users = load_users()
                    users[str(uid)] = (datetime.now() + timedelta(days=kdata["days"])).isoformat()
                    save_users(users)
                    keys[serial]["status"] = "used"
                    save_keys(keys)
                    await p.edit("✅ تم التفعيل! اضغط /start")
                    return
            await conv.send_message("❌ كود غير صالح.")

    elif data == "open_panel":
        if not is_subscribed(uid): return
        buttons = [
            [Button.inline("➕ إضافة حساب (رقم)", data="add_acc")],
            [Button.inline("🔄 تحديث السورس وإعادة تشغيل", data="restart")],
            [Button.inline("📊 إحصائيات", data="stats")]
        ]
        await event.edit("⚙️ **لوحة التحكم الأصلية**", buttons=buttons)

    elif data == "add_acc":
        if not is_subscribed(uid): return
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("📱 أرسل الرقم مع رمز الدولة:")
            phone = (await conv.get_response()).text.replace(" ", "")
            client = TelegramClient(StringSession(), api_id, api_hash)
            await client.connect()
            try:
                await client.send_code_request(phone)
                await conv.send_message("📥 أرسل الكود:")
                code = (await conv.get_response()).text.replace(" ", "")
                await client.sign_in(phone, code)
                with open(SESSION_DB, "a") as f:
                    f.write(client.session.save() + "\n")
                await conv.send_message("✅ تم الربط بنجاح!")
                await load_plugins(client)
                asyncio.create_task(client.run_until_disconnected())
            except Exception as e: await conv.send_message(f"❌ خطأ: {e}")

    elif data == "restart":
        await event.answer("🔄 جاري إعادة التشغيل...", alert=True)
        os.execl(sys.executable, sys.executable, *sys.argv)

    elif data == "stats":
        num = len(open(SESSION_DB).readlines()) if os.path.exists(SESSION_DB) else 0
        await event.answer(f"📊 عدد الحسابات: {num}", alert=True)

# --- تشغيل المهام ---
loop = asyncio.get_event_loop()
loop.create_task(start_all_accounts())
bot.run_until_disconnected()
