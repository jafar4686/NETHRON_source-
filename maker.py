import os, sys, asyncio, glob, importlib.util, __main__, subprocess, json, re, random
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from datetime import datetime, timedelta
from config import api_id, api_hash

# --- [1] الإعدادات الأساسية ---
BOT_TOKEN = "8136996400:AAEO4uDFUweXXiz49bs91hI_jmvBqh8CStI"
SESSION_DB = "database.txt"
USERS_DB = "nethron_vips.json"
CODES_FILE = "nethron_codes.txt" 
SUDO_ID = 5580918933 

bot = TelegramClient('MakerBot', api_id, api_hash).start(bot_token=BOT_TOKEN)
__main__.bot = bot

# --- [2] دالات النظام والأكواد ---
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
    clean_code = ""
    for word in user_input.replace('|', ' ').split():
        if word.strip().startswith("NETH-"):
            clean_code = word.strip()
            break
    if not clean_code: return None
    with open(CODES_FILE, "r") as f:
        lines = f.readlines()
    new_lines = []
    found_days = None
    for line in lines:
        if clean_code in line:
            try:
                parts = line.strip().split("|")
                # سحب الأيام من العمود الثالث وتجاهل أي رقم تسلسلي في البداية
                day_match = re.search(r'\d+', parts[2]) if len(parts) >= 3 else re.search(r'\d+', line.split(clean_code)[1])
                found_days = int(day_match.group()) if day_match else 30
            except: found_days = 30
            continue 
        new_lines.append(line)
    if found_days:
        with open(CODES_FILE, "w") as f: f.writelines(new_lines)
    return found_days

# --- [3] نظام الأنيميشن (الدوامة) ---
VORTEX = ["◜", "◝", "◞", "◟"]

def get_welcome_text(frame):
    return (
        "◆━━━━━━━━━━━━━━━━━◆\n"
        f"   {frame} **𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 𝑉𝐼𝑃** {frame}\n"
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

async def animate_start(msg, buttons):
    """تحديث الدوامة باستمرار في رسالة الترحيب"""
    i = 0
    try:
        while True:
            await msg.edit(get_welcome_text(VORTEX[i % 4]), buttons=buttons, link_preview=False)
            i += 1
            await asyncio.sleep(0.5)
    except: pass # يتوقف التحديث إذا تغيرت الرسالة أو حذفت

# --- [4] الأوامر واللوحة ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    uid = event.sender_id
    buy_url = random.choice(["https://t.me/NETH_RON", "https://t.me/xxnnxg"])
    
    if is_subscribed(uid):
        buttons = [[Button.inline("📱 فتح لوحة التحكم", data="open_panel")],
                   [Button.url("🛒 شراء كود تفعيل", url=buy_url)]]
    else:
        buttons = [[Button.inline("🔑 تفعيل الاشتراك بالكود", data="activate_code")],
                   [Button.url("🛒 شراء كود تفعيل", url=buy_url)]]

    msg = await event.respond(get_welcome_text(VORTEX[0]), buttons=buttons, link_preview=False)
    # تشغيل الدوامة كـ Task منفصل لكي لا تعطل البوت
    asyncio.create_task(animate_start(msg, buttons))

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode()
    uid = event.sender_id

    if data == "activate_code":
        async with bot.conversation(event.chat_id) as conv:
            dev = random.choice(["NETH_RON", "xxnnxg"])
            await conv.send_message(f"🎟️ **أرسل كود التفعيل الخاص بك:**\n📥 للشراء: @{dev}")
            res = await conv.get_response()
            days = verify_and_use_code(res.text.strip())
            if days:
                users = load_users()
                users[str(uid)] = (datetime.now() + timedelta(days=days)).isoformat()
                save_users(users)
                await conv.send_message(f"✅ **تم التفعيل بنجاح لمدة {days} يوم!**\nارسل /start لفتح اللوحة.")
            else:
                await conv.send_message("❌ الكود خاطئ أو تم استخدامه.")

    elif data == "open_panel":
        if not is_subscribed(uid): return await event.answer("⚠️ اشتراكك منتهي!", alert=True)
        btns = [[Button.inline("➕ إضافة حساب", data="add_acc")],
                [Button.inline("🔄 تحديث السورس", data="restart")]]
        await event.edit("⚙️ **لوحة التحكم الأصلية**", buttons=btns)

    elif data == "restart" and uid == SUDO_ID:
        await event.answer("🔄 جاري التحديث...", alert=True)
        os.execl(sys.executable, sys.executable, *sys.argv)

# --- [5] تشغيل الحسابات المنصبة ---
async def start_all():
    if os.path.exists(SESSION_DB):
        with open(SESSION_DB, "r") as f:
            for s in f:
                if s.strip():
                    try:
                        c = TelegramClient(StringSession(s.strip()), api_id, api_hash)
                        await c.connect()
                    except: pass

loop = asyncio.get_event_loop()
loop.create_task(start_all())
bot.run_until_disconnected()
