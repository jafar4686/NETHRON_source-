import json
import os
import random
import string
from datetime import datetime, timedelta
from telethon import events, Button
import __main__ # لسحب البوت من الملف الرئيسي

# محاولة سحب البوت من الملف الرئيسي (maker.py)
bot = getattr(__main__, 'bot', None)

KEYS_DB = "keys_db.json"
SUDO_ID = 5580918933
ADMIN_ID = 7273666832

def load_keys():
    if not os.path.exists(KEYS_DB): return {}
    with open(KEYS_DB, "r") as f: return json.load(f)

def save_keys(data):
    with open(KEYS_DB, "w") as f: json.dump(data, f, indent=4)

def is_authorized(user_id):
    return user_id in [SUDO_ID, ADMIN_ID]

if bot:
    # 1. إضافة كود (.اضافة كود 30)
    @bot.on(events.NewMessage(pattern=r"^\.اضافة كود (\d+)$"))
    async def add_key(event):
        if not is_authorized(event.sender_id): return
        days = int(event.pattern_match.group(1))
        code = f"NETH-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
        db = load_keys()
        serial = str(len(db) + 1)
        db[serial] = {"code": code, "days": days, "status": "available"}
        save_keys(db)
        await event.respond(f"✅ **تم إنشاء كود بنجاح**\n🎫 الكود: `{code}`\n🔢 التسلسل: {serial}")

    # 2. حالة المفاتيح (.حالة المفاتيح)
    @bot.on(events.NewMessage(pattern=r"^\.حالة المفاتيح$"))
    async def list_keys(event):
        if not is_authorized(event.sender_id): return
        db = load_keys()
        if not db: return await event.respond("📭 لا توجد مفاتيح.")
        msg = "📋 **قائمة المفاتيح:**\n"
        for s, d in db.items():
            status = "✅" if d['status'] == 'available' else "❌"
            msg += f"{s} - `{d['code']}` | {d['days']}يوم | {status}\n"
        await event.respond(msg)

    # 3. حذف كود (.حذف كود 1)
    @bot.on(events.NewMessage(pattern=r"^\.حذف كود (\d+)$"))
    async def delete_key(event):
        if not is_authorized(event.sender_id): return
        serial = event.pattern_match.group(1)
        db = load_keys()
        if serial in db:
            del db[serial]
            save_keys(db)
            await event.respond(f"🗑️ تم حذف الكود رقم {serial}")

    # 4. كليشة الأوامر (.الاكواد)
    @bot.on(events.NewMessage(pattern=r"^\.الاكواد$"))
    async def codes_info(event):
        if not is_authorized(event.sender_id): return
        await event.respond("🛠️ **إدارة الأكواد:**\n`.اضافة كود [ايام]`\n`.حالة المفاتيح`\n`.حذف كود [رقم]`")
