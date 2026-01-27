import __main__, asyncio, json, os, re
from telethon import events

# استدعاء الكلاينت
client = getattr(__main__, 'client', None)
FAR_DB = "far_data.json"

def load_data():
    if not os.path.exists(FAR_DB):
        return {"status": False, "msg": "مرحباً، المالك مشغول.", "warn_limit": 5, "users": {}}
    try:
        with open(FAR_DB, "r") as f: return json.load(f)
    except: return {"status": False, "msg": "مرحباً، المالك مشغول.", "warn_limit": 5, "users": {}}

def save_data(data):
    with open(FAR_DB, "w") as f: json.dump(data, f)

# 1. أمر الإضافة
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة فار (.+)"))
async def add_far(event):
    input_text = event.pattern_match.group(1)
    data = load_data()
    
    match = re.search(r"\$warn/(\d+)", input_text)
    if match:
        limit = int(match.group(1))
        data["warn_limit"] = limit
        data["msg"] = input_text.replace(f"/{limit}", "")
    else:
        data["msg"] = input_text
        data["warn_limit"] = 5
        
    save_data(data)
    await event.edit(f"✅ **تم حفظ الفار بنجاح!**\nتحذيرات: {data['warn_limit']}")

# 2. أوامر التفعيل والإيقاف
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(تفعيل|ايقاف) فار$"))
async def toggle_far(event):
    data = load_data()
    data["status"] = True if "تفعيل" in event.text else False
    data["users"] = {} # تصفير القائمة
    save_data(data)
    status = "شغال ✅" if data["status"] else "مطفي ❌"
    await event.edit(f"⚙️ **نظام الفار الآن: {status}**")

# 3. محرك الرد التلقائي (المصلح)
@client.on(events.NewMessage(incoming=True))
async def far_engine(event):
    # نرد فقط على الرسائل الخاصة (Private)
    if not event.is_private: return
    
    data = load_data()
    if not data.get("status"): return
    
    # تجنب الرد على نفسك أو على البوتات
    me = await client.get_me()
    if event.sender_id == me.id: return
    
    sender = await event.get_sender()
    if sender and getattr(sender, 'bot', False): return

    uid = str(event.sender_id)
    users = data.get("users", {})
    user_warns = users.get(uid, 0)
    
    # إذا وصل للحد المسموح يسكت السورس
    if user_warns >= data["warn_limit"]:
        return

    # زيادة العداد وحفظه
    user_warns += 1
    users[uid] = user_warns
    data["users"] = users
    save_data(data)

    # تحضير الرسالة
    warn_left = data["warn_limit"] - user_warns
    msg_to_send = data["msg"].replace("$warn", str(warn_left))
    
    # إضافة معلومات التواصل
    final_text = (
        f"{msg_to_send}\n\n"
        f"👤 الأدمن: @xxnnxg\n"
        f"✉️ أرسل رسالتك وسنرد عليك لاحقاً."
    )

    # إرسال الرد
    try:
        await event.reply(final_text)
    except Exception as e:
        print(f"Error in Far System: {e}")

# 4. المنيو .م10
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م10$"))
async def menu10(event):
    await event.edit(
        "🛡️ **نظام الفار (الرد التلقائي):**\n"
        "• `.اضافة فار` [الكليشة] $warn/5\n"
        "• `.تفعيل فار` / `.ايقاف فار`\n"
        "• `.حذف الفار`"
)
