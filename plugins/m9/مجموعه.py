import __main__, asyncio, json, os
from telethon import events, functions, types
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins

client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]
PROTECT_DIR = "Protect_Data"

if not os.path.exists(PROTECT_DIR):
    os.makedirs(PROTECT_DIR)

# --- دالة التخزين ---
async def get_db_path():
    me = await client.get_me()
    return os.path.join(PROTECT_DIR, f"group_{me.id}.json")

async def load_db():
    path = await get_db_path()
    if not os.path.exists(path): return {}
    with open(path, "r") as f: return json.load(f)

async def save_db(data):
    path = await get_db_path()
    with open(path, "w") as f: json.dump(data, f)

# --- أوامر القائمة ---

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م9$"))
async def m9(event):
    text = (
        "◈━━━━━━━━━━━━━━◈\n"
        "  ⚡️ **قائمة حماية المجموعات** ⚡️\n"
        "◈━━━━━━━━━━━━━━◈\n"
        "⦿ `.تفعيل مجموعه` : لتفعيل الحماية\n"
        "⦿ `.كتم` : بكتم الشخص بالرد\n"
        "⦿ `.فك كتم` : لفك كتم الشخص\n"
        "⦿ `.المكتومين` : عرض قائمة الكتم\n"
        "⦿ `.منع` : إدارة قفل/فتح الوسائط\n"
        "⦿ `.تفاعلي` : عرض معلوماتك بالمجموعة\n"
        "◈━━━━━━━━━━━━━━◈"
    )
    await event.edit(text)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل مجموعه$"))
async def enable_group(event):
    for i in range(10): 
        await event.edit(f"{VORTEX[i % 4]} 〔صبرك جاي يتفعل〕 {VORTEX[i % 4]}")
        await asyncio.sleep(0.3)
    
    db = await load_db()
    cid = str(event.chat_id)
    db[cid] = {"status": "مفعل", "locks": {}, "muted": []}
    await save_db(db)
    
    await event.edit("◈━━━━━━━━━━━━━━◈\n✅ **تم تفعيل حماية المجموعة بنجاح**\n⦿ تم إنشاء ملف التخزين الخاص بك\n◈━━━━━━━━━━━━━━◈")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كتم$"))
async def mute_user(event):
    if not event.is_reply: return await event.edit("◈〔 رُد على الشخص لكتمه 〕◈")
    reply = await event.get_reply_message()
    uid = reply.sender_id
    
    for i in range(6): 
        await event.edit(f"{VORTEX[i % 4]} 〔جاري الكتم〕 {VORTEX[i % 4]}")
        await asyncio.sleep(0.3)
    
    db = await load_db()
    cid = str(event.chat_id)
    if cid not in db: return await event.edit("◈〔 فعل المجموعة اولاً 〕◈")
    
    if uid not in db[cid]["muted"]:
        db[cid]["muted"].append(uid)
        await save_db(db)
    await event.edit("✅ تم كتم الشخص بنجاح.")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.فك كتم$"))
async def unmute_user(event):
    if not event.is_reply: return await event.edit("◈〔 رُد على الشخص لفك كتمه 〕◈")
    reply = await event.get_reply_message()
    uid = reply.sender_id
    db = await load_db()
    cid = str(event.chat_id)
    
    if uid in db.get(cid, {}).get("muted", []):
        db[cid]["muted"].remove(uid)
        await save_db(db)
        await event.edit("✅ تم فك الكتم عن الشخص.")
    else:
        await event.edit("◈〔 الشخص غير مكتوم أصلاً 〕◈")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.منع$"))
async def menu_locks(event):
    text = (
        "◈━━━━━━━━━━━━━━◈\n"
        "⚙️ **أوامر المنع والتحكم**\n"
        "◈━━━━━━━━━━━━━━◈\n"
        "⦿ `قفل/فتح صور`\n"
        "⦿ `قفل/فتح روابط`\n"
        "⦿ `قفل/فتح منشن`\n"
        "⦿ `قفل/فتح توجيه`\n"
        "⦿ `قفل/فتح فديوات`\n"
        "⦿ `قفل/فتح بوتات`\n"
        "⦿ `قفل/فتح رد`\n"
        "◈━━━━━━━━━━━━━━◈"
    )
    await event.edit(text)

@client.on(events.NewMessage(outgoing=True, pattern=r"^(قفل|فتح) (صور|روابط|منشن|توجيه|فديوات|بوتات|رد)$"))
async def locks_handler(event):
    action = event.pattern_match.group(1)
    item = event.pattern_match.group(2)
    cid = str(event.chat_id)
    db = await load_db()
    
    if cid not in db: return await event.edit("◈〔 فعل المجموعة اولاً 〕◈")
    
    db[cid]["locks"][item] = (action == "قفل")
    await save_db(db)
    await event.edit(f"✅ تم {action} {item} بنجاح.")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفاعلي$"))
async def interactive(event):
    me = await client.get_me()
    full = await client(functions.users.GetFullUserRequest(me.id))
    cid = event.chat_id
    
    # حساب عدد الرسائل (تجريبي)
    msgs = await client.get_messages(cid, limit=0)
    total = msgs.total
    
    # الرتبة
    rank = "عضو"
    if event.is_group:
        p = await client.get_permissions(cid, me.id)
        if p.is_creator: rank = "صاحب المجموعة"
        elif p.is_admin: rank = "مشرف"

    text = (
        f"👤 **الاسم:** {me.first_name}\n"
        f"📝 **الوصف:** {full.full_user.about or 'لا يوجد'}\n"
        f"🆔 **اليوزر:** @{me.username or 'لا يوجد'}\n"
        f"📊 **رسائلك هنا:** {total}\n"
        f"🎖️ **رتبتك:** {rank}\n"
    )
    # إرسال الصورة مع المعلومات
    photo = await client.download_profile_photo(me.id)
    await client.send_file(cid, photo, caption=text)
    await event.delete()

# --- محرك الحماية (الحذف التلقائي) ---
@client.on(events.NewMessage())
async def protector(event):
    if not event.is_group: return
    db = await load_db()
    cid = str(event.chat_id)
    if cid not in db: return
    
    uid = event.sender_id
    locks = db[cid].get("locks", {})
    
    # 1. فحص الكتم
    if uid in db[cid].get("muted", []):
        await event.delete()
        return

    # 2. فحص الأقفال
    if locks.get("صور") and event.photo: await event.delete()
    if locks.get("فديوات") and event.video: await event.delete()
    if locks.get("روابط") and ("http" in event.text or ".com" in event.text): await event.delete()
    if locks.get("منشن") and "@" in event.text: await event.delete()
    if locks.get("توجيه") and event.fwd_from: await event.delete()
    if locks.get("رد") and event.is_reply: await event.delete()
    
    # 3. فحص البوتات (عند الإضافة)
    if locks.get("بوتات") and event.user_joined:
        user = await event.get_user()
        if user.bot:
            await client.kick_participant(event.chat_id, user.id)
