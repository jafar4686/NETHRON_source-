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

# المطورين (دخول مباشر بدون قيود)
SUDO_IDS = [5580918933, 7273666832]

bot = TelegramClient('MakerBot', api_id, api_hash).start(bot_token=BOT_TOKEN)

# --- [2] نظام تشغيل الأوامر (Plugins) لكل حساب ---
async def load_plugins(user_client):
    """تحميل الأوامر وربطها بالكلاينت المشغل"""
    files = glob.glob("plugins/**/*.py", recursive=True)
    for f in files:
        if f.endswith("__init__.py"): continue
        name = os.path.basename(f)[:-3]
        try:
            spec = importlib.util.spec_from_file_location(name, f)
            mod = importlib.util.module_from_spec(spec)
            # ربط الكلاينت داخل المديول لضمان عمل الأوامر مثل .فحص
            mod.client = user_client 
            spec.loader.exec_module(mod)
        except Exception as e: 
            print(f"❌ خطأ في تحميل {name}: {e}")

async def start_all_accounts():
    """تشغيل كافة الحسابات المحفوظة في الداتا بيس عند إقلاع البوت"""
    if os.path.exists(SESSION_DB):
        with open(SESSION_DB, "r") as f:
            for s in f.readlines():
                s = s.strip()
                if s:
                    try:
                        c = TelegramClient(StringSession(s), api_id, api_hash)
                        await c.connect()
                        if await c.is_user_authorized():
                            await load_plugins(c) # تحميل الأوامر لهذا الحساب
                            asyncio.create_task(c.run_until_disconnected())
                            print(f"✅ تم تشغيل حساب من القاعدة")
                    except: pass

# --- [3] نظام فحص الاشتراك الحديدي ---
def check_vip(uid):
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

# --- [4] كليشة الترحيب المزخرفة ---
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

# --- [5] أحداث البوت المساعد (الميكر) ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    uid = event.sender_id
    is_vip, _, _ = check_vip(uid)
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
    
    if data == "open_panel":
        if not is_vip:
            return await event.answer("⚠️ اشتراكك غير مفعّل!", alert=True)
        
        btns = [[Button.inline("➕ إضافة حساب (رقم)", data="add_acc")], 
                [Button.inline("🔄 ريستارت السورس", data="restart")]]
        await event.edit("⚙️ **لوحة التحكم الأصلية - نيثرون VIP**", buttons=btns)

    elif data == "add_acc":
        if not is_vip: return
        async with bot.conversation(event.chat_id, timeout=300) as conv:
            await conv.send_message("📱 **أرسل الرقم مع رمز الدولة (مثال: +964...):**")
            try:
                p_res = await conv.get_response()
                phone = p_res.text.replace(" ", "")
                
                # إنشاء جلسة نصية جديدة
                client = TelegramClient(StringSession(), api_id, api_hash)
                await client.connect()
                await client.send_code_request(phone)
                
                await conv.send_message("📥 **أرسل كود التحقق الآن:**")
                c_res = await conv.get_response()
                await client.sign_in(phone, c_res.text)
                
                # حفظ الجلسة في الملف لضمان عدم ضياعها
                with open(SESSION_DB, "a") as f:
                    f.write(client.session.save() + "\n")
                
                await conv.send_message("✅ **تم الربط بنجاح! الأوامر (.فحص الخ) تعمل الآن.**")
                
                # تشغيل الأوامر لهذا الحساب فوراً
                await load_plugins(client)
                asyncio.create_task(client.run_until_disconnected())
                
            except asyncio.TimeoutError:
                await conv.send_message("⚠️ تأخرت في الرد، تم إلغاء العملية.")
            except Exception as e:
                await conv.send_message(f"❌ حدث خطأ: {str(e)}")

    elif data == "restart" and uid in SUDO_IDS:
        await event.answer("🔄 جاري إعادة التشغيل...", alert=True)
        os.execl(sys.executable, sys.executable, *sys.argv)

# --- [6] الانطلاق ---
loop = asyncio.get_event_loop()
loop.create_task(start_all_accounts()) 
print("🚀 سورس نيثرون ميكر قيد التشغيل...")
bot.run_until_disconnected()
