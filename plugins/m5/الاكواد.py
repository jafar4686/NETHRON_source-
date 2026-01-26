import __main__
import json
import os
import random
import string
from datetime import datetime, timedelta
from telethon import events, Button

# سحب البوت والكلاينت من الملف الرئيسي كما في ملفاتك
bot = __main__.bot
client = __main__.client

KEYS_DB = "keys_db.json"
SUDO_ID = 5580918933
ADMIN_ID = 7273666832

# دالات البيانات
def load_keys():
    if not os.path.exists(KEYS_DB): return {}
    try:
        with open(KEYS_DB, "r") as f: return json.load(f)
    except: return {}

def save_keys(data):
    with open(KEYS_DB, "w") as f: json.dump(data, f, indent=4)

def is_authorized(user_id):
    return user_id in [SUDO_ID, ADMIN_ID]

HEADER = "★──────────☭──────────★\n"

# 1. أمر إضافة كود
@bot.on(events.NewMessage(pattern=r"^\.اضافة كود (\d+)$"))
async def add_key(event):
    if not is_authorized(event.sender_id): return
    
    days = int(event.pattern_match.group(1))
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    code = f"NETH-{random_str}"
    
    db = load_keys()
    serial = str(len(db) + 1)
    db[serial] = {
        "code": code,
        "days": days,
        "status": "available"
    }
    save_keys(db)
    
    msg = (
        f"{HEADER}"
        "✨ **تم إنشاء مفتاح تفعيل جديد**\n"
        f"{HEADER}\n"
        f"🎫 **الكود:** `{code}`\n"
        f"⏱️ **المدة:** {days} يوم\n"
        f"🔢 **التسلسل:** {serial}\n"
        f"{HEADER}"
    )
    await event.respond(msg)

# 2. أمر حالة المفاتيح
@bot.on(events.NewMessage(pattern=r"^\.حالة المفاتيح$"))
async def list_keys(event):
    if not is_authorized(event.sender_id): return
    
    db = load_keys()
    if not db: return await event.respond("📭 **لا توجد أكواد في القاعدة حالياً.**")
    
    msg = f"{HEADER}📋 **قائمة مفاتيح نيثرون:**\n{HEADER}\n"
    for s, d in db.items():
        status = "✅ متاح" if d['status'] == 'available' else "❌ مستخدم"
        msg += f"🔢 **{s}** ➥ `{d['code']}`\n⏱️ {d['days']} يوم | {status}\n\n"
    
    msg += f"{HEADER}"
    await event.respond(msg)

# 3. أمر حذف كود
@bot.on(events.NewMessage(pattern=r"^\.حذف كود (\d+)$"))
async def delete_key(event):
    if not is_authorized(event.sender_id): return
    
    serial = event.pattern_match.group(1)
    db = load_keys()
    
    if serial in db:
        del db[serial]
        save_keys(db)
        await event.respond(f"🗑️ **تم حذف المفتاح رقم ({serial}) بنجاح.**")
    else:
        await event.respond("❌ **هذا الرقم التسلسلي غير موجود!**")

# 4. كليشة المساعدة
@bot.on(events.NewMessage(pattern=r"^\.الاكواد$"))
async def codes_info(event):
    if not is_authorized(event.sender_id): return
    
    info = (
        f"{HEADER}"
        "🛠️ **إدارة مفاتيح سورس نيثرون**\n"
        f"{HEADER}\n"
        "• `.اضافة كود (الايام)`\n"
        "• `.حالة المفاتيح`\n"
        "• `.حذف كود (التسلسل)`\n"
        f"{HEADER}"
    )
    await event.respond(info)
