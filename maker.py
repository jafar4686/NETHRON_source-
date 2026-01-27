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

# قائمة المطورين (المستثنون من الفحص)
SUDO_IDS = [5580918933, 7273666832]

bot = TelegramClient('MakerBot', api_id, api_hash).start(bot_token=BOT_TOKEN)

# --- [2] نظام التحقق الصارم (الدرع) ---
def check_vip(uid):
    """تحقق حقيقي وصارم من التاريخ"""
    if uid in SUDO_IDS:
        return True, "مطور السورس 👑", "∞"
    
    if not os.path.exists(USERS_DB):
        return False, "غير مفعّل ✘", "0"
        
    try:
        with open(USERS_DB, "r") as f:
            users = json.load(f)
            if str(uid) in users:
                expiry = datetime.fromisoformat(users[str(uid)])
                if expiry > datetime.now():
                    rem = (expiry - datetime.now()).days
                    return True, "مفعّل ✔", str(rem)
    except: pass
    return False, "غير مفعّل ✘", "0"

# --- [3] نظام تشغيل الحسابات والملفات ---
async def load_plugins(user_client):
    files = glob.glob("plugins/**/*.py", recursive=True)
    for f in files:
        if f.endswith("__init__.py"): continue
        name = os.path.basename(f)[:-3]
        try:
            spec = importlib.util.spec_from_file_location(name, f)
            mod = importlib.util.module_from_spec(spec)
            mod.client = user_client
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
        "⦿ سهولة في التحكم وسرعة في الأداء\n"
        "◆━━━━━━━━━━━━━━━━━◆\n"
        "◈➥ [𝑫𝑬𝑽〔المطور〕](https://t.me/NETH_RON)\n"
        "◈➥ [𝑫𝑬𝑽〔المطور〕](https://t.me/xxnnxg)\n"
        "◆━━━━━━━━━━━━━━━━━◆"
    )

# --- [5] الأحداث واللوحة ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    uid = event.sender_id
    is_vip, status, _ = check_vip(uid)
    url = random.choice(["https://t.me/NETH_RON", "https://t.me/xxnnxg"])
    
    if is_vip:
        btns = [[Button.inline("📱 فتح لوحة التحكم", data="open_panel")], 
                [Button.url("🛒 شراء كود", url=url)]]
    else:
        btns = [[Button.inline("🔑 تفعيل الاشتراك", data="activate_code")], 
                [Button.url("🛒 شراء كود تفعيل", url=url)]]
    
    await event.respond(get_welcome_text(uid), buttons=btns, link_preview=False)

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode(); uid = event.sender_id
    is_vip, _, _ = check_vip(uid)
    
    if data == "activate_code":
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("🎟️ **أرسل كود التفعيل الخاص بك:**")
            res = await conv.get_response()
            # دالة فحص الكود (verify_code) تُفترض موجودة كما في الكود السابق
            from main_logic import verify_code # أو ضع الدالة هنا مباشرة
            days = verify_code(res.text.strip()) 
            if days:
                d = json.load(open(USERS_DB)) if os.path.exists(USERS_DB) else {}
                d[str(uid)] = (datetime.now() + timedelta(days=days)).isoformat()
                json.dump(d, open(USERS_DB, "w"), indent=4)
                await conv.send_message(f"✅ تم التفعيل! ارسل /start")
            else: await conv.send_message("❌ كود خطأ!")

    elif data == "open_panel":
        # إعادة التحقق فور الضغط على الزر
        if not is_vip:
            return await event.answer("⚠️ عذراً، اشتراكك منتهي أو غير مفعل!", alert=True)
            
        btns = [[Button.inline("➕ إضافة حساب", data="add_acc")], 
                [Button.inline("🔄 ريستارت السورس", data="restart")]]
        await event.edit("⚙️ **لوحة التحكم الأصلية - VIP**", buttons=btns)

    elif data == "add_acc":
        if not is_vip: return await event.answer("⚠️ لا تملك صلاحية!", alert=True)
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("📱 أرسل الرقم مع الرمز:")
            p_res = await conv.get_response()
            phone = p_res.text.replace(" ", "")
            client = TelegramClient(StringSession(), api_id, api_hash)
            await client.connect()
            try:
                await client.send_code_request(phone)
                await conv.send_message("📥 الكود:")
                c_res = await conv.get_response()
                await client.sign_in(phone, c_res.text)
                with open(SESSION_DB, "a") as f: f.write(client.session.save() + "\n")
                await conv.send_message("✅ تم الربط!")
                await load_plugins(client)
                asyncio.create_task(client.run_until_disconnected())
            except Exception as e: await conv.send_message(f"❌: {e}")

    elif data == "restart" and uid in SUDO_IDS:
        os.execl(sys.executable, sys.executable, *sys.argv)

# --- [6] التشغيل ---
loop = asyncio.get_event_loop()
loop.create_task(start_all_accounts()) 
bot.run_until_disconnected()
