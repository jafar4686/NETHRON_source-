import __main__, asyncio, json, os
from telethon import events, functions, types
from datetime import datetime

client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]
GROUP_DIR = "group"

if not os.path.exists(GROUP_DIR):
    os.makedirs(GROUP_DIR)

# --- دالات التخزين المعزولة ---
async def get_db_path():
    me = await client.get_me()
    return os.path.join(GROUP_DIR, f"user_{me.id}.json")

async def load_db():
    path = await get_db_path()
    if not os.path.exists(path): return {}
    with open(path, "r") as f: return json.load(f)

async def save_db(data):
    path = await get_db_path()
    with open(path, "w") as f: json.dump(data, f)

# --- أوامر المجموعات ---

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل مجموعه$"))
async def enable_group(event):
    if not event.is_group: return
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري تفعيل مجموعتك 〕 {f} ⌯")
        await asyncio.sleep(0.2)
    
    db = await load_db()
    cid = str(event.chat_id)
    db[cid] = {"muted": [], "msgs": {}}
    await save_db(db)
    
    await event.edit(f"⌯ {VORTEX[0]} 〔 تم تفعيل مجموعتك بنجاح 〕 {VORTEX[0]} ⌯")
    await asyncio.sleep(10)
    await event.delete()

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كتم$"))
async def mute_user(event):
    if not event.is_group or not event.is_reply: return
    db = await load_db()
    cid = str(event.chat_id)
    if cid not in db: return
    
    reply = await event.get_reply_message()
    uid = reply.sender_id
    
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري كتم الشخص 〕 {f} ⌯")
        await asyncio.sleep(0.1)
    
    if uid not in db[cid]["muted"]:
        db[cid]["muted"].append(uid)
        await save_db(db)
    await event.edit(f"⌯ {VORTEX[0]} 〔 تم كتم الشخص بنجاح 〕 {VORTEX[0]} ⌯")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.فك كتم$"))
async def unmute_user(event):
    if not event.is_group or not event.is_reply: return
    db = await load_db()
    cid = str(event.chat_id)
    if cid not in db: return
    
    reply = await event.get_reply_message()
    uid = reply.sender_id
    
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري فتح الكتم 〕 {f} ⌯")
        await asyncio.sleep(0.1)
    
    if uid in db[cid].get("muted", []):
        db[cid]["muted"].remove(uid)
        await save_db(db)
    await event.edit(f"⌯ {VORTEX[0]} 〔 تم فك الكتم بنجاح 〕 {VORTEX[0]} ⌯")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفاعلي$"))
async def interactive(event):
    if not event.is_group: return
    me = await client.get_me()
    full = await client(functions.users.GetFullUserRequest(me.id))
    db = await load_db()
    cid = str(event.chat_id)
    
    count = db.get(cid, {}).get("msgs", {}).get(str(me.id), 0)
    p = await client.get_permissions(event.chat_id, me.id)
    rank = "صاحب المجموعة" if p.is_creator else "مشرف" if p.is_admin else "عضو"

    text = (
        "★────────☭────────★\n"
        "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
        "★────────☭────────★\n\n"
        f"• 𝑵𝒂𝒎𝒆 ⌯ {me.first_name}\n"
        f"• 𝑼𝒔𝒆𝒓 ⌯ @{me.username or 'لا يوجد'}\n"
        f"• 𝑩𝒊𝒐 ⌯ {full.full_user.about or 'لا يوجد'}\n"
        f"• 𝑴𝒂𝒔𝒔𝒆𝒈𝒆 ⌯ {count}\n"
        f"• 𝑼𝒏𝒊𝒕 𝑹𝒂𝒏𝒌 ⌯ {rank}\n"
        "•  ⌯\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
    )
    await event.edit(text, link_preview=False)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كشف$"))
async def detect(event):
    if not event.is_group or not event.is_reply: return
    reply = await event.get_reply_message()
    user = await client.get_entity(reply.sender_id)
    full = await client(functions.users.GetFullUserRequest(user.id))
    db = await load_db()
    cid = str(event.chat_id)
    
    count = db.get(cid, {}).get("msgs", {}).get(str(user.id), 0)
    p = await client.get_permissions(event.chat_id, user.id)
    rank = "صاحب المجموعة" if p.is_creator else "مشرف" if p.is_admin else "عضو"
    date = user.date.strftime("%Y/%m/%d") if user.date else "غير معروف"

    text = (
        "★────────☭────────★\n"
        "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
        "★────────☭────────★\n\n"
        f"• 𝑵𝒂𝒎𝒆 ⌯ {user.first_name}\n"
        f"• 𝑼𝒔𝒆𝒓 ⌯ @{user.username or 'لا يوجد'}\n"
        f"• 𝑩𝒊𝒐 ⌯ {full.full_user.about or 'لا يوجد'}\n"
        f"• 𝑴𝒂𝒔𝒔𝒆𝒈𝒆 ⌯ {count}\n"
        f"• 𝑹𝒂𝒏𝒌 ⌯ {rank}\n"
        f"• 𝑱𝒐𝒊𝒏 𝑫𝒂𝒕𝒆 ⌯ {date}\n"
        f"• 𝑰𝒅 ⌯ `{user.id}`\n\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
    )
    photo = await client.download_profile_photo(user.id)
    await client.send_file(event.chat_id, photo, caption=text, link_preview=False)
    await event.delete()

# --- المحرك (حذف رسائل المكتومين + عداد الرسائل) ---
@client.on(events.NewMessage())
async def handler(event):
    if not event.is_group: return
    db = await load_db()
    cid = str(event.chat_id)
    if cid not in db: return
    
    uid = str(event.sender_id)
    # 1. عداد الرسائل
    msgs = db[cid].get("msgs", {})
    msgs[uid] = msgs.get(uid, 0) + 1
    db[cid]["msgs"] = msgs
    await save_db(db)
    
    # 2. حذف المكتومين
    if event.sender_id in db[cid].get("muted", []):
        await event.delete()
