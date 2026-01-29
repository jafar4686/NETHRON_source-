import __main__, asyncio, json, os
from telethon import events, functions, types

client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]
PROTECT_DIR = "Protect_Data"

if not os.path.exists(PROTECT_DIR):
    os.makedirs(PROTECT_DIR)

# --- دالات التخزين ---
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
    if not event.is_group: return # يغلس بالخاص
    text = (
        "★────────☭────────★\n"
        "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
        "  ⚡️ **قائمة حماية المجموعات** ⚡️\n"
        "★────────☭────────★\n"
        "⦿ `.تفعيل مجموعه` : لتفعيل الحماية\n"
        "⦿ `.كتم` : بكتم الشخص بالرد\n"
        "⦿ `.فك كتم` : لفك كتم الشخص\n"
        "⦿ `.المكتومين` : عرض قائمة الكتم\n"
        "⦿ `.منع` : إدارة قفل/فتح الوسائط\n"
        "⦿ `.تفاعلي` : عرض معلوماتك بالمجموعة\n"
        "★────────☭────────★"
    )
    await event.edit(text)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل مجموعه$"))
async def enable_group(event):
    if not event.is_group: return # يغلس بالخاص
    for i in range(4): 
        await event.edit(f"{VORTEX[i % 4]} 〔صبرك جاي يتفعل〕 {VORTEX[i % 4]}")
        await asyncio.sleep(0.2)
    
    db = await load_db()
    cid = str(event.chat_id)
    db[cid] = {"status": "مفعل", "locks": {}, "muted": []}
    await save_db(db)
    await event.edit("✅ **تم تفعيل حماية المجموعة بنجاح**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كتم$"))
async def mute_user(event):
    if not event.is_group or not event.is_reply: return # يغلس إذا مو بمجموعة أو مو رد
    
    reply = await event.get_reply_message()
    uid = reply.sender_id
    db = await load_db()
    cid = str(event.chat_id)
    
    if cid not in db: return await event.edit("◈〔 فعل المجموعة اولاً 〕◈")
    
    for i in range(4): 
        await event.edit(f"{VORTEX[i % 4]} 〔جاري الكتم〕 {VORTEX[i % 4]}")
        await asyncio.sleep(0.1)
    
    if uid not in db[cid]["muted"]:
        db[cid]["muted"].append(uid)
        await save_db(db)
    await event.edit("✅ **تم كتم الشخص بنجاح.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.فك كتم$"))
async def unmute_user(event):
    if not event.is_group or not event.is_reply: return
    
    reply = await event.get_reply_message()
    uid = reply.sender_id
    db = await load_db()
    cid = str(event.chat_id)
    
    if uid in db.get(cid, {}).get("muted", []):
        db[cid]["muted"].remove(uid)
        await save_db(db)
        await event.edit("✅ **تم فك الكتم.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.منع$"))
async def menu_locks(event):
    if not event.is_group: return
    text = (
        "★────────☭────────★\n"
        "⚙️ **أوامر المنع والتحكم**\n"
        "★────────☭────────★\n"
        "⦿ `قفل/فتح صور`\n"
        "⦿ `قفل/فتح روابط`\n"
        "⦿ `قفل/فتح منشن`\n"
        "⦿ `قفل/فتح توجيه`\n"
        "⦿ `قفل/فتح فديوات`\n"
        "⦿ `قفل/فتح بوتات`\n"
        "⦿ `قفل/فتح رد`\n"
        "★────────☭────────★"
    )
    await event.edit(text)

@client.on(events.NewMessage(outgoing=True, pattern=r"^(قفل|فتح) (صور|روابط|منشن|توجيه|فديوات|بوتات|رد)$"))
async def locks_handler(event):
    if not event.is_group: return
    action, item = event.pattern_match.group(1), event.pattern_match.group(2)
    cid, db = str(event.chat_id), await load_db()
    
    if cid not in db: return
    db[cid]["locks"][item] = (action == "قفل")
    await save_db(db)
    await event.edit(f"✅ تم {action} {item}.")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفاعلي$"))
async def interactive(event):
    if not event.is_group: return
    me = await client.get_me()
    p = await client.get_permissions(event.chat_id, me.id)
    rank = "مشرف" if p.is_admin else "صاحب المجموعة" if p.is_creator else "عضو"

    text = f"👤 **الاسم:** {me.first_name}\n🎖️ **رتبتك:** {rank}\n★────────☭────────★"
    photo = await client.download_profile_photo(me.id)
    await client.send_file(event.chat_id, photo, caption=text)
    await event.delete()

# --- محرك الحماية ---
@client.on(events.NewMessage())
async def protector(event):
    if not event.is_group: return # المحرك يشتغل فقط بالمجموعات
    db = await load_db()
    cid = str(event.chat_id)
    if cid not in db: return
    
    uid = event.sender_id
    locks = db[cid].get("locks", {})
    
    if uid in db[cid].get("muted", []): return await event.delete()

    if locks.get("صور") and event.photo: await event.delete()
    if locks.get("فديوات") and event.video: await event.delete()
    if locks.get("روابط") and ("http" in (event.text or "") or ".com" in (event.text or "")): await event.delete()
    if locks.get("منشن") and "@" in (event.text or ""): await event.delete()
    if locks.get("توجيه") and event.fwd_from: await event.delete()
    if locks.get("رد") and event.is_reply: await event.delete()
