import __main__, asyncio, json, os, re
from telethon import events, functions, types

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
        return {"status": False, "msg": "مرحباً بك.", "warn_limit": 5, "users": {}, "action": "كتم"}
    try:
        with open(path, "r", encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"status": False, "msg": "مرحباً بك.", "warn_limit": 5, "users": {}, "action": "كتم"}

async def save_data(data):
    path = await get_db_path()
    with open(path, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 1. أوامر الإعدادات
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة فار ([\s\S]+)"))
async def add_far(event):
    input_text = event.pattern_match.group(1)
    data = await load_data()
    match = re.search(r"\$warn/(\d+)", input_text)
    if match:
        limit = int(match.group(1))
        data["warn_limit"] = limit
        # مسح المتغير والرقم من النص الأساسي
        clean_msg = input_text.replace(f"$warn/{limit}", "").replace("$warn", "").strip()
        data["msg"] = clean_msg
    else:
        data["msg"] = input_text.replace("$warn", "").strip()
        data["warn_limit"] = 5
    await save_data(data)
    await event.edit(f"✅ **تم حفظ الفار بنجاح**\n\n**التحذيرات:** {data['warn_limit']}")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديد عقوبة (حظر|كتم)$"))
async def set_action(event):
    action = event.pattern_match.group(1)
    data = await load_data()
    data["action"] = action
    await save_data(data)
    await event.edit(f"⚙️ **تم تحديد العقوبة إلى: {action}**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(تفعيل|ايقاف) فار$"))
async def toggle_far(event):
    data = await load_data()
    data["status"] = True if "تفعيل" in event.text else False
    data["users"] = {} 
    await save_data(data)
    await event.edit(f"⚙️ **نظام الفار: {'شغال ✅' if data['status'] else 'مطفي ❌'}**")

# 2. نظام ترك رسالة
@client.on(events.NewMessage(incoming=True, pattern=r"^\.ترك رسالة ([\s\S]+)"))
async def leave_msg(event):
    if not event.is_private: return
    me = await client.get_me()
    sender = await event.get_sender()
    info = f"📩 **رسالة من:** [{sender.first_name}](tg://user?id={sender.id})\n📝 **النص:** {event.pattern_match.group(1)}"
    await client.send_message(me.id, info)
    await event.reply("✅ **وصلت رسالتك للمالك.**")

# 3. محرك الفار المطور
@client.on(events.NewMessage(incoming=True))
async def far_engine(event):
    if not event.is_private: return
    data = await load_data()
    if not data.get("status"): return
    
    me = await client.get_me()
    if event.sender_id == me.id: return

    uid = str(event.sender_id)
    users = data.get("users", {})
    user_warns = users.get(uid, 0)
    
    # تنفيذ العقوبة (حظر أو كتم)
    if user_warns >= data["warn_limit"]:
        if data["action"] == "حظر":
            try: await client(functions.contacts.BlockRequest(id=event.sender_id))
            except: pass
        else: # كتم
            await event.delete()
        return

    # الرد التلقائي
    if not event.text.startswith(".ترك رسالة"):
        user_warns += 1
        users[uid] = user_warns
        data["users"] = users
        await save_data(data)

        warn_left = data["warn_limit"] - user_warns
        admin_link = f"[𝑨𝑫𝑴𝑰𝑵](https://t.me/xxnnxg)"
        
        final_reply = (
            f"{data['msg']}\n\n"
            f"👤 مراسلة الـ {admin_link}\n"
            f"✉️ بالرد بـ: `.ترك رسالة [نصك]`\n\n"
            f"**عدد التحذيرات المتبقية:** {warn_left}"
        )
        await event.reply(final_reply)

# 4. السماح للمزعج
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.سماح للمزعج$"))
async def allow_user(event):
    if not event.is_reply: return await event.edit("⚠️ رد على رسالة الشخص.")
    reply = await event.get_reply_message()
    data = await load_data()
    uid = str(reply.sender_id)
    # إلغاء الحظر من التليجرام إذا كان محظوراً
    try: await client(functions.contacts.UnblockRequest(id=reply.sender_id))
    except: pass
    if uid in data["users"]:
        del data["users"][uid]
        await save_data(data)
        await event.edit("✅ **تم السماح للشخص وتصفير تحذيراته.**")

# 5. القائمة م10
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م10$"))
async def menu10(event):
    await event.edit(
        "🛡️ **نـظـام الـفـار والـحـمـايـة**\n"
        "•──────────────•\n"
        "• `.اضافة فار` [النص] $warn/العدد\n"
        "• `.تحديد عقوبة` [حظر/كتم]\n"
        "• `.تفعيل فار` / `.ايقاف فار`\n"
        "• `.سماح للمزعج` (بالرد)\n"
        "• `.حذف الفار` ↤ مسح البيانات\n"
        "•──────────────•"
        )
