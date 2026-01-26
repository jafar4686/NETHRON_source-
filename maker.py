import os, sys, asyncio, glob, importlib.util, __main__, subprocess, json, re, random
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from datetime import datetime, timedelta
from config import api_id, api_hash

# --- [1] الإعدادات والملفات ---
BOT_TOKEN = "8136996400:AAEO4uDFUweXXiz49bs91hI_jmvBqh8CStI"
SESSION_DB = "database.txt"
USERS_DB = "nethron_vips.json"
CODES_FILE = "nethron_codes.txt" 
SUDO_ID = 5580918933 

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
    users = load_users()
    if str(uid) in users:
        return datetime.fromisoformat(users[str(uid)]) > datetime.now()
    return False

def verify_and_use_code(user_input):
    if not os.path.exists(CODES_FILE): return None
    clean_user_code = ""
    for word in user_input.replace('|', ' ').split():
        if word.strip().startswith("NETH-"):
            clean_user_code = word.strip()
            break
    if not clean_user_code: return None

    with open(CODES_FILE, "r") as f:
        lines = f.readlines()
    
    new_lines = []
    found_days = None
    for line in lines:
        if clean_user_code in line:
            try:
                parts = line.strip().split("|")
                if len(parts) >= 3:
                    day_match = re.search(r'\d+', parts[2])
                    found_days = int(day_match.group()) if day_match else 30
                else:
                    suffix = line.split(clean_user_code)[1]
                    day_match = re.search(r'\d+', suffix)
                    found_days = int(day_match.group()) if day_match else 30
            except: found_days = 30
            continue 
        new_lines.append(line)
    
    if found_days:
        with open(CODES_FILE, "w") as f:
            f.writelines(new_lines)
    return found_days

# --- [3] تشغيل السورس ---
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
        except: pass

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

# --- [4] كليشة الترحيب والأنيميشن ---
FRAMES = ["◜", "◝", "◞", "◟"]

def get_welcome_text(frame):
    return (
        "◆━━━━━━━━━━━━━━━━━◆\n"
        f"   🌀 **𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 𝑉𝐼𝑃** {frame}\n"
        "◆━━━━━━━━━━━━━━━━━◆\n\n"
        f"⦿ أهلاً بك في نظام التنصيب الذكي {frame}\n"
        f"⦿ سورس نيثرون يوفر لك أقوى حماية {frame}\n"
        f"⦿ ميزات حصرية وتشفير كامل للبيانات {frame}\n"
        f"⦿ سهولة في التحكم وسرعة في الأداء {frame}\n\n"
        "◆━━━━━━━━━━━━━━━━━◆\n"
        f"◈➥ [𝑫𝑬𝑽〔المطور〕](https://t.me/NETH_RON) {frame}\n"
        f"◈➥ [𝑫𝑬𝑽〔المطور〕](https://t.me/xxnnxg) {frame}\n"
        "◆━━━━━━━━━━━━━━━━━◆"
    )

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    uid = event.sender_id
    
    # اختيار يوزر عشوائي لزر الشراء
    buy_url = random.choice(["https://t.me/NETH_RON", "https://t.me/xxnnxg"])
    
    if is_subscribed(uid):
        buttons = [[Button.inline("📱 فتح لوحة التحكم", data="open_panel")],
                   [Button.url("🛒 شراء كود تفعيل", url=buy_url)]]
    else:
        buttons = [[Button.inline("🔑 تفعيل الاشتراك بالكود", data="activate_code")],
                   [Button.url("🛒 شراء كود تفعيل", url=buy_url)]]

    # تشغيل الأنيميشن (4 دورات للدوامة)
    msg = await event.respond(get_welcome_text(FRAMES[0]), buttons=buttons, link_preview=False)
    for _ in range(3): 
        for frame in FRAMES:
            await asyncio.sleep(0.3)
            await msg.edit(get_welcome_text(frame), buttons=buttons, link_preview=False)

@bot.on(events.NewMessage(pattern='/P'))
async def fast_panel(event):
    if is_subscribed(event.sender_id):
        btns = [[Button.inline("➕ إضافة حساب", data="add_acc")],
                [Button.inline("🔄 تحديث السورس", data="restart")],
                [Button.inline("📊 إحصائيات", data="stats")]]
        await event.respond("⚙️ **لوحة التحكم - سورس نيثرون**", buttons=btns)
    else:
        await event.respond("⚠️ **عذراً، يجب عليك تفعيل الاشتراك أولاً.**")

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode()
    uid = event.sender_id

    if data == "activate_code":
        async with bot.conversation(event.chat_id) as conv:
            dev_user = random.choice(["NETH_RON", "xxnnxg"])
            await conv.send_message(f"🎟️ **أرسل كود التفعيل الخاص بك:**\n📥 للشراء: @{dev_user}")
            user_input = (await conv.get_response()).text.strip()
            days = verify_and_use_code(user_input)
            if days:
                users = load_users()
                users[str(uid)] = (datetime.now() + timedelta(days=days)).isoformat()
                save_users(users)
                await conv.send_message(f"✅ **تم التفعيل بنجاح لمدة {days} يوم!**\nارسل /P للوحة.")
            else:
                await conv.send_message("❌ **الكود خاطئ أو مستخدم مسبقاً!**")

    elif data == "open_panel":
        if not is_subscribed(uid): return await event.answer("⚠️ منتهي!", alert=True)
        btns = [[Button.inline("➕ إضافة حساب", data="add_acc")],
                [Button.inline("🔄 تحديث السورس", data="restart")],
                [Button.inline("📊 إحصائيات", data="stats")]]
        await event.edit("⚙️ **لوحة التحكم الأصلية**", buttons=btns)

    elif data == "add_acc":
        if not is_subscribed(uid): return
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("📱 **أرسل الرقم مع الرمز (مثل +964):**")
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
        if uid == SUDO_ID:
            await event.answer("🔄 جاري التحديث...", alert=True)
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            await event.answer("❌ للمطور فقط!", alert=True)

# تشغيل
loop = asyncio.get_event_loop()
loop.create_task(start_all_accounts())
bot.run_until_disconnected()
