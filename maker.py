import os, sys, asyncio, glob, importlib.util, __main__, subprocess, json, re, random
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from datetime import datetime, timedelta
from config import api_id, api_hash

# --- [1] الإعدادات الأساسية والملفات ---
BOT_TOKEN = "8136996400:AAEO4uDFUweXXiz49bs91hI_jmvBqh8CStI"
SESSION_DB = "database.txt"
USERS_DB = "nethron_vips.json"
CODES_FILE = "nethron_codes.txt" 
SUDO_ID = 5580918933 # أيدي المطور الأساسي

bot = TelegramClient('MakerBot', api_id, api_hash).start(bot_token=BOT_TOKEN)
__main__.bot = bot

# --- [2] نظام إدارة المستخدمين والأكواد ---
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
        # التحقق من أن تاريخ انتهاء الاشتراك لم يأتِ بعد
        return datetime.fromisoformat(users[str(uid)]) > datetime.now()
    return False

def verify_and_use_code(user_input):
    if not os.path.exists(CODES_FILE): return None
    
    # تنظيف المدخل: استخراج الكود الذي يبدأ بـ NETH-
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
                # البحث عن الأيام في العمود الثالث (بعد الكود) لتجنب رقم التسلسل
                if len(parts) >= 3:
                    day_match = re.search(r'\d+', parts[2])
                    found_days = int(day_match.group())
                else:
                    # محاولة سحب أي رقم يظهر بعد الكود مباشرة
                    suffix = line.split(clean_code)[1]
                    day_match = re.search(r'\d+', suffix)
                    found_days = int(day_match.group())
            except:
                found_days = 30 # افتراضي
            continue # حذف الكود من الملف
        new_lines.append(line)
    
    if found_days:
        with open(CODES_FILE, "w") as f: f.writelines(new_lines)
    return found_days

# --- [3] الأنيميشن (الدوامة المتحركة) ---
VORTEX_FRAMES = ["◜", "◝", "◞", "◟"]

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

async def run_vortex(msg, buttons):
    """دالة تحديث الدوامة باستمرار في الخلفية"""
    i = 0
    try:
        while True:
            # تحديث النص مع الفريم الجديد للدوامة
            await msg.edit(get_welcome_text(VORTEX_FRAMES[i % 4]), buttons=buttons, link_preview=False)
            i += 1
            await asyncio.sleep(0.5) # سرعة الدوران
    except:
        # يتوقف الأنيميشن إذا تم مسح الرسالة أو الضغط على زر يغير المحتوى
        pass

# --- [4] الأوامر واللوحة ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    uid = event.sender_id
    # اختيار يوزر عشوائي للشراء
    buy_url = random.choice(["https://t.me/NETH_RON", "https://t.me/xxnnxg"])
    
    if is_subscribed(uid):
        buttons = [
            [Button.inline("📱 فتح لوحة التحكم", data="open_panel")],
            [Button.url("🛒 شراء كود تفعيل", url=buy_url)]
        ]
    else:
        buttons = [
            [Button.inline("🔑 تفعيل الاشتراك بالكود", data="activate_code")],
            [Button.url("🛒 شراء كود تفعيل", url=buy_url)]
        ]

    # إرسال الرسالة وبدء مهمة الأنيميشن
    msg = await event.respond(get_welcome_text(VORTEX_FRAMES[0]), buttons=buttons, link_preview=False)
    asyncio.create_task(run_vortex(msg, buttons))

@bot.on(events.NewMessage(pattern='/P'))
async def fast_panel(event):
    if is_subscribed(event.sender_id):
        btns = [[Button.inline("➕ إضافة حساب", data="add_acc")],
                [Button.inline("🔄 تحديث السورس", data="restart")]]
        await event.respond("⚙️ **لوحة التحكم - سورس نيثرون**", buttons=btns)
    else:
        await event.respond("⚠️ **يجب عليك تفعيل الاشتراك بالكود أولاً.**")

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
                await conv.send_message("❌ **الكود خاطئ أو تم استخدامه مسبقاً!**")

    elif data == "open_panel":
        if not is_subscribed(uid): return await event.answer("⚠️ اشتراكك منتهي!", alert=True)
        btns = [[Button.inline("➕ إضافة حساب", data="add_acc")],
                [Button.inline("🔄 تحديث السورس", data="restart")]]
        await event.edit("⚙️ **لوحة التحكم الأصلية**", buttons=btns)

    elif data == "add_acc":
        if not is_subscribed(uid): return
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("📱 **أرسل الرقم مع الرمز (مثال +964):**")
            p_res = await conv.get_response()
            phone = p_res.text.replace(" ", "")
            client = TelegramClient(StringSession(), api_id, api_hash)
            await client.connect()
            try:
                await client.send_code_request(phone)
                await conv.send_message("📥 **أرسل الكود المكون من 5 أرقام:**")
                c_res = await conv.get_response()
                await client.sign_in(phone, c_res.text)
                with open(SESSION_DB, "a") as f: f.write(client.session.save() + "\n")
                await conv.send_message("✅ **تم ربط الحساب بنجاح!**")
            except Exception as e: await conv.send_message(f"❌ خطأ: {e}")

    elif data == "restart":
        if uid == SUDO_ID:
            await event.answer("🔄 جاري إعادة التشغيل...", alert=True)
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            await event.answer("❌ هذا الأمر للمطور الأساسي فقط.", alert=True)

# --- [5] تشغيل السيرفر ---
print("🚀 سورس نيثرون يعمل الآن بنظام الأنيميشن والأكواد...")
bot.run_until_disconnected()
