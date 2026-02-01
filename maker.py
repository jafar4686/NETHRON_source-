import os, sys, asyncio, glob, importlib.util, __main__, subprocess, json, re, random
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from datetime import datetime, timedelta
from config import api_id, api_hash
# --- استدعاء ملف الأزرار المنفصل ---
import rank_buttons 

# --- [1] الإعدادات الأساسية ---
BOT_TOKEN = "8136996400:AAEO4uDFUweXXiz49bs91hI_jmvBqh8CStI"
SESSION_DB = "database.txt" 
USERS_DB = "nethron_vips.json"
CODES_FILE = "nethron_codes.txt" 
SUDO_IDS = [5580918933, 7273666832]

bot = TelegramClient('MakerBot', api_id, api_hash).start(bot_token=BOT_TOKEN)

# --- [2] نظام تشغيل الأوامر (إصلاح AttributeError) ---
async def load_plugins(user_client):
    files = glob.glob("plugins/**/*.py", recursive=True)
    for f in files:
        if f.endswith("__init__.py"): continue
        name = os.path.basename(f)[:-3]
        try:
            spec = importlib.util.spec_from_file_location(name, f)
            mod = importlib.util.module_from_spec(spec)
            mod.client = user_client
            __main__.client = user_client
            spec.loader.exec_module(mod)
        except Exception as e:
            print(f"❌ فشل تحميل {name}: {e}")

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

# --- [3] نظام التحقق ---
def check_vip(uid):
    if uid in SUDO_IDS: return True, "مطور السورس 👑", "∞"
    if not os.path.exists(USERS_DB): return False, "غير مفعّل ✘", "0"
    try:
        with open(USERS_DB, "r") as f:
            u = json.load(f)
            if str(uid) in u:
                exp = datetime.fromisoformat(u[str(uid)])
                if exp > datetime.now():
                    return True, "مفعّل ✔", str((exp - datetime.now()).days)
    except: pass
    return False, "غير مفعّل ✘", "0"

def verify_code(user_input):
    if not os.path.exists(CODES_FILE): return None
    clean = next((w for w in user_input.replace('|',' ').split() if w.startswith("NETH-")), None)
    if not clean: return None
    with open(CODES_FILE, "r") as f: lines = f.readlines()
    new_l = []; days = None
    for l in lines:
        if clean in l:
            p = l.split("|")
            days = int(re.search(r'\d+', p[2]).group()) if len(p)>=3 else 30
            continue
        new_l.append(l)
    if days: open(CODES_FILE, "w").writelines(new_l)
    return days

# --- [4] كليشة الترحيب ---
def get_welcome_text(uid):
    is_vip, status, days = check_vip(uid)
    return (
        "◆━━━━━━━━━━━━━━◆\n"
        f"◈➥حالة الاشتراك 〔 {status} 〕\n"
        f"◈➥الايام المتبقية 〔 {days} 〕✔\n"
        "◆━━━━━━━━━━━━━◆\n\n"
        "🌀 **𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 𝑉𝐼𝑃**\n"
        "◆━━━━━━━━━━━━━━━━━◆\n"
        "⦿ أهلاً بك في نظام التنصيب الذكي\n"
        "⦿ سورس نيثرون يوفر لك أقوى حماية\n"
        "⦿ ميزات حصرية وتشفير كامل للبيانات\n"
        "◆━━━━━━━━━━━━━━━━━◆\n"
        "◈➥ [𝑫𝑬𝑽〔المطور〕](https://t.me/NETH_RON)\n"
        "◈➥ [𝑫𝑬𝑽〔المطور〕](https://t.me/xxnnxg)\n"
        "◆━━━━━━━━━━━━━━━━━◆"
    )

# --- [5] الأحداث والتحكم ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    is_vip, _, _ = check_vip(event.sender_id)
    url = random.choice(["https://t.me/NETH_RON", "https://t.me/xxnnxg"])
    
    if is_vip:
        btns = [
            [Button.inline("📱 فتح لوحة التحكم", data="panel")],
            [Button.url("🛒 شراء كود", url=url)]
        ]
    else:
        btns = [
            [Button.inline("🔑 تفعيل الاشتراك", data="activate")],
            [Button.url("🛒 شراء كود", url=url)]
        ]
    
    await event.respond(get_welcome_text(event.sender_id), buttons=btns, link_preview=False)

# --- حدث استقبال نداء أمر الصلاحيات ---
@bot.on(events.NewMessage(pattern="عرض_الصلاحيات"))
async def send_perms_panel(event):
    is_vip, _, _ = check_vip(event.sender_id)
    if is_vip:
        # استدعاء الأزرار من الملف الخارجي
        await event.respond("⚙️ **لوحة التحكم بالصلاحيات [تجريبي]**", 
                             buttons=rank_buttons.get_main_perms_buttons())
        await event.delete()

@bot.on(events.CallbackQuery)
async def cb(event):
    uid = event.sender_id
    is_vip, _, _ = check_vip(uid)
    data = event.data.decode()

    if data == "activate":
        async with bot.conversation(event.chat_id, timeout=300) as conv:
            await conv.send_message("🎟️ **أرسل كود التفعيل الخاص بك:**")
            res = await conv.get_response()
            days = verify_code(res.text.strip())
            if days:
                d = json.load(open(USERS_DB)) if os.path.exists(USERS_DB) else {}
                d[str(uid)] = (datetime.now() + timedelta(days=days)).isoformat()
                json.dump(d, open(USERS_DB, "w"), indent=4)
                await conv.send_message(f"✅ تم التفعيل بنجاح!")
            else: await conv.send_message("❌ كود خاطئ!")

    elif data == "panel" and is_vip:
        btns = [[Button.inline("➕ إضافة حساب", data="add")], [Button.inline("🔄 ريستارت", data="restart")]]
        await event.edit("⚙️ **لوحة التحكم الأصلية**", buttons=btns)

    # --- منطق أزرار الصلاحيات (تجريبي) ---
    elif data == "test_1" and is_vip:
        await event.answer("✅ تم ضغط الزر التجريبي الأول!", alert=True)
    
    elif data == "test_2" and is_vip:
        await event.answer("🚀 تم ضغط الزر التجريبي الثاني!", alert=True)

    elif data == "close_perms" and is_vip:
        await event.delete()

    elif data == "add" and is_vip:
        async with bot.conversation(event.chat_id, timeout=300) as conv:
            await conv.send_message("📱 **أرسل الرقم مع رمز الدولة:**")
            try:
                p_res = await conv.get_response()
                phone = p_res.text.replace(" ", "")
                client = TelegramClient(StringSession(), api_id, api_hash)
                await client.connect()
                await client.send_code_request(phone)
                await conv.send_message("📥 **أرسل الكود:**")
                c_res = await conv.get_response()
                await client.sign_in(phone, c_res.text)
                with open(SESSION_DB, "a") as f: f.write(client.session.save() + "\n")
                await load_plugins(client)
                asyncio.create_task(client.run_until_disconnected())
                await conv.send_message("✅ **تم الربط وتشغيل الأوامر!**")
            except Exception as e: await conv.send_message(f"❌ خطأ: {e}")

    elif data == "restart" and uid in SUDO_IDS:
        os.execl(sys.executable, sys.executable, *sys.argv)

# --- [6] الانطلاق ---
loop = asyncio.get_event_loop()
loop.create_task(start_all_accounts())
bot.run_until_disconnected()
