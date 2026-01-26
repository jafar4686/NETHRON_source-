import os, sys, asyncio, glob, importlib.util, __main__, subprocess, json
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from datetime import datetime, timedelta
from config import api_id, api_hash

# --- [1] الإعدادات والملفات ---
BOT_TOKEN = "8136996400:AAEO4uDFUweXXiz49bs91hI_jmvBqh8CStI"
SESSION_DB = "database.txt"
USERS_DB = "nethron_vips.json"
CODES_FILE = "nethron_codes.txt" # نفس ملفك
SUDO_ID = 5580918933
SUDO2_ID = 7273666832

bot = TelegramClient('MakerBot', api_id, api_hash).start(bot_token=BOT_TOKEN)
__main__.bot = bot
__main__.client = None 

# --- [2] دالات النظام ---
def load_users():
    if not os.path.exists(USERS_DB): return {}
    try:
        with open(USERS_DB, "r") as f: return json.load(f)
    except: return {}

def save_users(data):
    with open(USERS_DB, "w") as f: json.dump(data, f, indent=4)

def is_subscribed(uid):
    if uid in [SUDO_ID, SUDO2_ID]: return True
    users = load_users()
    if str(uid) in users:
        return datetime.fromisoformat(users[str(uid)]) > datetime.now()
    return False

# دالة التحقق من الكود ومسحه (الربط مع ملفك)
def verify_and_use_code(user_code):
    if not os.path.exists(CODES_FILE): return None
    with open(CODES_FILE, "r") as f:
        lines = f.readlines()
    
    new_lines = []
    found_days = None
    for line in lines:
        parts = line.strip().split("|")
        if len(parts) == 3 and parts[1] == user_code:
            found_days = int(parts[2]) # أخذ عدد الأيام
            continue # تخطي السطر (حذف الكود)
        new_lines.append(line)
    
    if found_days:
        with open(CODES_FILE, "w") as f:
            f.writelines(new_lines)
    return found_days

# --- [3] تشغيل البلكنز والحسابات ---
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

# --- [4] واجهة البوت والأوامر ---
HEADER = "★──────────☭──────────★\n"

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    uid = event.sender_id
    msg = (
        f"{HEADER}"
        "   ☭ • **𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 𝑉𝐼𝑃** • ☭\n"
        f"{HEADER}\n"
        "مرحباً بك في بوت التنصيب.\n\n"
        "➥ **𝑫𝑬𝑽 1 :** @NETH_RON\n"
        "➥ **𝑫𝑬𝑽 2 :** @xxnnxg\n"
        f"{HEADER}"
    )
    
    if is_subscribed(uid):
        buttons = [[Button.inline("📱 فتح لوحة التحكم", data="open_panel")]]
    else:
        buttons = [[Button.inline("🔑 تفعيل الاشتراك بالكود", data="activate_code")]]
    
    await event.respond(msg, buttons=buttons)

@bot.on(events.NewMessage(pattern='/P'))
async def fast_panel(event):
    if is_subscribed(event.sender_id):
        btns = [[Button.inline("➕ إضافة حساب", data="add_acc")],
                [Button.inline("🔄 تحديث", data="restart")],
                [Button.inline("📊 إحصائيات", data="stats")]]
        await event.respond("⚙️ **لوحة تحكم نيثرون**", buttons=btns)
    else:
        await event.respond("⚠️ **عذراً، يجب عليك الاشتراك أولاً.**")

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode()
    uid = event.sender_id

    if data == "activate_code":
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("🎟️ **أرسل كود التفعيل الخاص بك:**")
            user_input = (await conv.get_response()).text.strip()
            
            days = verify_and_use_code(user_input)
            
            if days:
                p = await conv.send_message("🔄 **جاري التحقق من الكود...**\n`▒▒▒▒▒ 0%`")
                for i in range(1, 6):
                    await asyncio.sleep(0.3)
                    await p.edit(f"🔄 **جاري التحقق...**\n`{'█'*i}{'▒'*(5-i)} {i*20}%`️")
                
                users = load_users()
                users[str(uid)] = (datetime.now() + timedelta(days=days)).isoformat()
                save_users(users)
                
                await p.edit(f"✅ **تم التفعيل بنجاح لمدة {days} يوم!**\nارسل /P للوحة.")
            else:
                await conv.send_message("❌ **الكود خاطئ أو تم استخدامه مسبقاً!**")

    elif data == "open_panel":
        if not is_subscribed(uid): return await event.answer("⚠️ اشتراكك منتهي!", alert=True)
        btns = [[Button.inline("➕ إضافة حساب (رقم)", data="add_acc")],
                [Button.inline("🔄 تحديث السورس", data="restart")],
                [Button.inline("📊 إحصائيات", data="stats")]]
        await event.edit("⚙️ **لوحة التحكم الأصلية**", buttons=btns)

    elif data == "add_acc":
        if not is_subscribed(uid): return
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("📱 **أرسل الرقم مع الرمز (مثال +964):**")
            phone = (await conv.get_response()).text.replace(" ", "")
            c = TelegramClient(StringSession(), api_id, api_hash)
            await c.connect()
            try:
                await c.send_code_request(phone)
                await conv.send_message("📥 **أرسل الكود:**")
                code_in = (await conv.get_response()).text.replace(" ", "")
                await c.sign_in(phone, code_in)
                with open(SESSION_DB, "a") as f: f.write(c.session.save() + "\n")
                await conv.send_message("✅ **تم ربط الحساب بنجاح!**")
                await load_plugins(c)
                asyncio.create_task(c.run_until_disconnected())
            except Exception as e: await conv.send_message(f"❌ خطأ: {e}")

    elif data == "restart":
        await event.answer("🔄 جاري التحديث...", alert=True)
        os.execl(sys.executable, sys.executable, *sys.argv)

    elif data == "stats":
        num = len(open(SESSION_DB).readlines()) if os.path.exists(SESSION_DB) else 0
        await event.answer(f"📊 الحسابات: {num}", alert=True)

# تشغيل
loop = asyncio.get_event_loop()
loop.create_task(start_all_accounts())
bot.run_until_disconnected()
