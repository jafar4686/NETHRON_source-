import json
import os
import random
import string
from datetime import datetime, timedelta
from telethon import events, Button

# --- الإعدادات وصلاحيات الوصول ---
KEYS_DB = "keys_db.json"
SUDO_ID = 5580918933
ADMIN_ID = 7273666832

def load_keys():
    if not os.path.exists(KEYS_DB): return {}
    with open(KEYS_DB, "r") as f: return json.load(f)

def save_keys(data):
    with open(KEYS_DB, "w") as f: json.dump(data, f, indent=4)

# دالة توليد كود عشوائي
def generate_random_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def is_authorized(user_id):
    return user_id in [SUDO_ID, ADMIN_ID]

# 1. أمر إضافة كود (مثال: .اضافة كود 30)
@events.register(events.NewMessage(pattern=r"^\.اضافة كود (\d+)$"))
async def add_key(event):
    if not is_authorized(event.sender_id): return
    
    days = int(event.pattern_match.group(1))
    code = f"NETH-{generate_random_code()}"
    db = load_keys()
    
    # حساب رقم تسلسلي تلقائي
    serial = len(db) + 1
    
    db[str(serial)] = {
        "code": code,
        "days": days,
        "status": "available", # available or used
        "created_at": datetime.now().isoformat()
    }
    save_keys(db)
    
    msg = (
        "✅ **تم إنشاء مفتاح جديد بنجاح**\n"
        "★──────────★\n"
        f"🎫 **الكود:** `{code}`\n"
        f"⏱️ **المدة:** {days} يوم\n"
        f"🔢 **الرقم التسلسلي:** {serial}\n"
        "★──────────★"
    )
    await event.respond(msg)

# 2. أمر حالة المفاتيح (.حالة المفاتيح)
@events.register(events.NewMessage(pattern=r"^\.حالة المفاتيح$"))
async def list_keys(event):
    if not is_authorized(event.sender_id): return
    
    db = load_keys()
    if not db: return await event.respond("📭 لا توجد مفاتيح في القاعدة حالياً.")
    
    msg = "📋 **قائمة المفاتيح المتوفرة:**\n"
    msg += "★──────────★\n"
    
    for serial, data in db.items():
        status_icon = "✅" if data["status"] == "available" else "❌"
        msg += f"{serial} - `{data['code']}` | {data['days']}يوم | {status_icon}\n"
    
    msg += "★──────────★\n"
    msg += "عرض المفاتيح المتاحة فقط."
    await event.respond(msg)

# 3. أمر حذف كود (.حذف كود 1)
@events.register(events.NewMessage(pattern=r"^\.حذف كود (\d+)$"))
async def delete_key(event):
    if not is_authorized(event.sender_id): return
    
    serial = event.pattern_match.group(1)
    db = load_keys()
    
    if serial in db:
        del db[serial]
        save_keys(db)
        await event.respond(f"🗑️ تم حذف المفتاح رقم ({serial}) بنجاح.")
    else:
        await event.respond("❌ الرقم التسلسلي غير موجود.")

# 4. كليشة الأكواد (.الاكواد)
@events.register(events.NewMessage(pattern=r"^\.الاكواد$"))
async def codes_info(event):
    if not is_authorized(event.sender_id): return
    
    info = (
        "🛠️ **لوحة إدارة مفاتيح نيثرون**\n"
        "★──────────★\n"
        "• `.اضافة كود [الأيام]` : لإنشاء مفتاح جديد.\n"
        "• `.حالة المفاتيح` : لعرض الأكواد المتوفرة.\n"
        "• `.حذف كود [الرقم]` : لحذف مفتاح معين.\n"
        "★──────────★"
    )
    await event.respond(info)
