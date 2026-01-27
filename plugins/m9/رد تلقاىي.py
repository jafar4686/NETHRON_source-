import __main__, asyncio, json, os, re
from telethon import events

# استدعاء الكلاينت
client = getattr(__main__, 'client', None)
DB_DIR = "Far_Data"

# التأكد من وجود المجلد
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# دالة لجلب مسار الملف داخل المجلد الجديد
async def get_db_path():
    me = await client.get_me()
    return os.path.join(DB_DIR, f"config_{me.id}.json")

async def load_data():
    path = await get_db_path()
    if not os.path.exists(path):
        return {"status": False, "msg": "مرحباً، المالك مشغول حالياً.", "warn_limit": 5, "users": {}}
    try:
        with open(path, "r", encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"status": False, "msg": "مرحباً، المالك مشغول حالياً.", "warn_limit": 5, "users": {}}

async def save_data(data):
    path = await get_db_path()
    with open(path, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 1. أمر إضافة الفار
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة فار ([\s\S]+)"))
async def add_far(event):
    input_text = event.pattern_match.group(1)
    data = await load_data()
    
    match = re.search(r"\$warn/(\d+)", input_text)
    if match:
        limit = int(match.group(1))
        data["warn_limit"] = limit
        clean_msg = input_text.replace(f"/{limit}", "")
        data["msg"] = clean_msg
    else:
        data["msg"] = input_text
        data["warn_limit"] = 5
        
    await save_data(data)
    await event.edit(f"✅ **تم الحفظ بنجاح!**\n📁 الملف: `{DB_DIR}/config_{ (await client.get_me()).id }.json`\n⚠️ التحذيرات: {data['warn_limit']}")

# 2. أوامر التحكم
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(تفعيل|ايقاف) فار$"))
async def toggle_far(event):
    data = await load_data()
    data["status"] = True if "تفعيل" in event.text else False
    data["users"] = {} 
    await save_data(data)
    status_icon = "✅" if data["status"] else "❌"
    await event.edit(f"⚙️ **نظام الفار: {'شغال ' + status_icon if data['status'] else 'مطفي ' + status_icon}**")

# 3. محرك الرد التلقائي
@client.on(events.NewMessage(incoming=True))
async def far_engine(event):
    if not event.is_private: return
    
    data = await load_data()
    if not data.get("status"): return
    
    me = await client.get_me()
    if event.sender_id == me.id: return
    
    sender = await event.get_sender()
    if sender and getattr(sender, 'bot', False): return

    uid = str(event.sender_id)
    users = data.get("users", {})
    user_warns = users.get(uid, 0)
    
    if user_warns >= data["warn_limit"]:
        return

    user_warns += 1
    users[uid] = user_warns
    data["users"] = users
    await save_data(data)

    warn_left = data["warn_limit"] - user_warns
    final_reply = data["msg"].replace("$warn", str(warn_left))

    try:
        await event.reply(final_reply)
    except: pass

# 4. حذف وحالة الفار
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حذف الفار$"))
async def del_far(event):
    path = await get_db_path()
    if os.path.exists(path):
        os.remove(path)
        await event.edit("🗑️ **تم مسح بيانات الفار نهائياً.**")
    else:
        await event.edit("⚠️ لا توجد بيانات مسجلة لهذا الحساب.")

# 5. قائمة الأوامر .م10
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م10$"))
async def menu10(event):
    await event.edit(
        "📂 **نظام الفار (إدارة المجلدات):**\n"
        "•──────────────•\n"
        "• `.اضافة فار` الكليشة مع $warn/العدد\n"
        "• `.تفعيل فار` ↤ تشغيل\n"
        "• `.ايقاف فار` ↤ إيقاف\n"
        "• `.حذف الفار` ↤ مسح ملف الحساب\n"
        "•──────────────•\n"
        "📌 يتم خزن كل حساب في مجلد `Far_Data`."
    )
