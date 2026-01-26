import __main__
import json
import os
import random
import string
from datetime import datetime, timedelta
from telethon import events, Button

# سحب البوت والكلاينت من الملف الرئيسي (نفس نظام dark.py و music.py)
bot = getattr(__main__, 'bot', None)
client = getattr(__main__, 'client', None)

KEYS_DB = "keys_db.json"
SUDO_ID = 5580918933
ADMIN_ID = 7273666832

# دالة إدارة البيانات (JSON)
def load_keys():
    if not os.path.exists(KEYS_DB): return {}
    try:
        with open(KEYS_DB, "r") as f: return json.load(f)
    except: return {}

def save_keys(data):
    with open(KEYS_DB, "w") as f: json.dump(data, f, indent=4)

HEADER = "★──────────☭──────────★\n"

# فحص الصلاحية للمطور والآدمن
def is_auth(uid):
    return uid in [SUDO_ID, ADMIN_ID]

if bot:
    # 1. إضافة كود (.اضافة كود 30)
    @bot.on(events.NewMessage(pattern=r"^\.اضافة كود (\d+)$"))
    async def add_key(event):
        if not is_auth(event.sender_id): return
        
        days = int(event.pattern_match.group(1))
        # توليد كود عشوائي (6 رموز)
        code = f"NETH-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        
        db = load_keys()
        serial = str(len(db) + 1)
        db[serial] = {
            "code": code, 
            "days": days, 
            "status": "available",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        save_keys(db)
        
        res = (
            f"{HEADER}"
            "✨ **تم إنشاء مفتاح جديد بنجاح**\n"
            f"{HEADER}\n"
            f"🎫 **الكود:** `{code}`\n"
            f"⏱️ **المدة:** {days} يوم\n"
            f"🔢 **التسلسل:** {serial}\n"
            f"{HEADER}"
        )
        await event.respond(res)

    # 2. حالة المفاتيح (.حالة المفاتيح)
    @bot.on(events.NewMessage(pattern=r"^\.حالة المفاتيح$"))
    async def list_keys(event):
        if not is_auth(event.sender_id): return
        
        db = load_keys()
        if not db: return await event.respond("📭 **لا توجد أكواد محفوظة.**")
        
        msg = f"{HEADER}📋 **مفاتيح سورس نيثرون:**\n{HEADER}\n"
        for s, d in db.items():
            st = "✅ متاح" if d['status'] == 'available' else "❌ مستخدم"
            msg += f"🔢 {s} ➥ `{d['code']}`\n⏱️ {d['days']} يوم | {st}\n\n"
        
        await event.respond(msg + HEADER)

    # 3. حذف كود (.حذف كود 1)
    @bot.on(events.NewMessage(pattern=r"^\.حذف كود (\d+)$"))
    async def del_key(event):
        if not is_auth(event.sender_id): return
        
        serial = event.pattern_match.group(1)
        db = load_keys()
        
        if serial in db:
            del db[serial]
            save_keys(db)
            await event.respond(f"🗑️ **تم حذف المفتاح رقم ({serial}) بنجاح.**")
        else:
            await event.respond("❌ **هذا التسلسل غير موجود.**")

    # 4. المساعدة (.الاكواد)
    @bot.on(events.NewMessage(pattern=r"^\.الاكواد$"))
    async def help_keys(event):
        if not is_auth(event.sender_id): return
        
        help_msg = (
            f"{HEADER}"
            "🛠️ **لوحة إدارة مفاتيح التفعيل**\n"
            f"{HEADER}\n"
            "• `.اضافة كود (الايام)`\n"
            "• `.حالة المفاتيح`\n"
            "• `.حذف كود (التسلسل)`\n"
            f"{HEADER}"
        )
        await event.respond(help_msg)
