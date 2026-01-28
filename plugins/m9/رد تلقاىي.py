import __main__, asyncio, json, os, re
from telethon import events, Button

client = getattr(__main__, 'client', None)
DB_DIR = "Far_Data"

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

async def get_db_path():
    me = await client.get_me()
    return os.path.join(DB_DIR, f"config_{me.id}.json")

async def load_data():
    path = await get_db_path()
    if not os.path.exists(path):
        return {"status": False, "msg": "", "warn_limit": 5, "users": {}, "action": "كتم"}
    try:
        with open(path, "r", encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"status": False, "msg": "", "warn_limit": 5, "users": {}, "action": "كتم"}

async def save_data(data):
    path = await get_db_path()
    with open(path, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 1. أوامر التحكم والاعدادات
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة فار ([\s\S]+)"))
async def add_far(event):
    input_text = event.pattern_match.group(1)
    data = await load_data()
    match = re.search(r"\$warn/(\d+)", input_text)
    if match:
        limit = int(match.group(1))
        data["warn_limit"] = limit
        data["msg"] = input_text.replace(f"/{limit}", "").strip()
    else:
        data["msg"] = input_text.strip()
        data["warn_limit"] = 5
    await save_data(data)
    await event.edit(f"✅ **تم حفظ كليشة الفار بنجاح**\n\n**التحذيرات المحددة:** {data['warn_limit']}")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديد عقوبة (حظر|كتم)$"))
async def set_action(event):
    action = event.pattern_match.group(1)
    data = await load_data()
    data["action"] = action
    await save_data(data)
    await event.edit(f"⚙️ **تم تحديد العقوبة عند اكتمال التحذيرات إلى: {action}**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(تفعيل|ايقاف) فار$"))
async def toggle_far(event):
    data = await load_data()
    data["status"] = True if "تفعيل" in event.text else False
    data["users"] = {} 
    await save_data(data)
    await event.edit(f"⚙️ **نظام الفار الآن: {'شغال ✅' if data['status'] else 'معطل ❌'}**")

# 2. نظام ترك رسالة للمطور
@client.on(events.NewMessage(incoming=True, pattern=r"^\.ترك رسالة ([\s\S]+)"))
async def leave_msg(event):
    if not event.is_private: return
    me = await client.get_me()
    sender = await event.get_sender()
    user_msg = event.pattern_match.group(1)
    
    # توجيه الرسالة للمطور
    info = f"📩 **رسالة جديدة من شخص عبر الفار:**\n\n"
    info += f"👤 **الشخص:** [{sender.first_name}](tg://user?id={sender.id})\n"
    info += f"🆔 **الايدي:** `{sender.id}`\n"
    info += f"📝 **الرسالة:** {user_msg}"
    
    await client.send_message(me.id, info)
    await event.reply("✅ **تم إرسال رسالتك بنجاح للمالك، سيتم الرد عليك قريباً.**")

# 3. محرك الفار والعقوبات
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
    
    # تطبيق العقوبة إذا تجاوز الحد
    if user_warns >= data["warn_limit"]:
        if data["action"] == "حظر":
            try: await client.edit_permissions(event.chat_id, view_messages=False)
            except: pass
        else: # كتم (مسح الرسالة)
            await event.delete()
        return

    # الرد التلقائي
    if not event.text.startswith(".ترك رسالة"):
        user_warns += 1
        users[uid] = user_warns
        data["users"] = users
        await save_data(data)

        warn_left = data["warn_limit"] - user_warns
        # الكليشة مع المراسلة المخفية
        admin_link = f"[𝑨𝑫𝑴𝑰𝑵](https://t.me/xxnnxg)"
        final_msg = f"{data['msg']}\n\n"
        final_msg += f"👤 مراسلة الـ {admin_link}\n"
        final_msg += f"✉️ يمكنك ترك رسالة بالرد بـ: `.ترك رسالة [نصك]`\n\n"
        final_msg += f"**عدد التحذيرات:** {warn_left}"

        await event.reply(final_msg)

# 4. السماح للمزعج
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.سماح للمزعج$"))
async def allow_user(event):
    if not event.is_reply: return await event.edit("⚠️ الرد على رسالة الشخص المزعج.")
    reply = await event.get_reply_message()
    data = await load_data()
    uid = str(reply.sender_id)
    if uid in data["users"]:
        del data["users"][uid]
        await save_data(data)
        await event.edit("✅ **تم تصفير تحذيرات الشخص والسماح له بالمراسلة.**")

# 5. قائمة الأوامر .م10
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م10$"))
async def menu10(event):
    menu = (
        "🛡️ **نـظـام الـفـار والـحـمـايـة**\n"
        "•──────────────•\n"
        "• `.اضافة فار` [النص] $warn/العدد\n"
        "⤷ لحفظ كليشة الرد مع تحديد التحذيرات.\n\n"
        "• `.تحديد عقوبة` [حظر/كتم]\n"
        "⤷ لاختيار الإجراء عند انتهاء التحذيرات.\n\n"
        "• `.تفعيل فار` / `.ايقاف فار`\n"
        "⤷ للتحكم بنظام الرد التلقائي.\n\n"
        "• `.سماح للمزعج` (بالرد)\n"
        "⤷ لإلغاء العقوبة عن الشخص.\n\n"
        "• `.حذف الفار` ↤ لمسح البيانات.\n"
        "•──────────────•"
    )
    await event.edit(menu)
