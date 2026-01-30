import __main__, asyncio, json, os
from telethon import events, functions, types

client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]
GROUP_DIR = "group"

if not os.path.exists(GROUP_DIR):
    os.makedirs(GROUP_DIR)

# --- دالة جلب ID المالك الحقيقي ---
async def get_owner_id():
    me = await client.get_me()
    return me.id

# --- دالات التخزين ---
async def get_db_path():
    oid = await get_owner_id()
    return os.path.join(GROUP_DIR, f"user_{oid}.json")

async def load_db():
    path = await get_db_path()
    if not os.path.exists(path): return {}
    try:
        with open(path, "r") as f: return json.load(f)
    except: return {}

async def save_db(data):
    path = await get_db_path()
    with open(path, "w") as f: json.dump(data, f)

# --- فلتر التحقق من المالك ---
async def is_owner(event):
    oid = await get_owner_id()
    return event.out and event.sender_id == oid

# --- أوامر المجموعات (قفل للمالك) ---

@client.on(events.NewMessage(outgoing=True))
async def group_commands_handler(event):
    # التحقق الصارم: لازم الرسالة طالعة منك وأنت صاحب الـ ID
    if not await is_owner(event):
        return

    cmd = event.raw_text
    cid = str(event.chat_id)

    # 1. منيو .م2
    if cmd == ".م2":
        text = (
            "★────────☭────────★\n"
            "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
            "                  ☭ • سورس عراق ثون • ☭\n"
            "★────────☭────────★\n\n"
            "🛡 **أوامر الحماية (للمالك فقط):**\n\n"
            "• `.تفعيل مجموعه` ➥ لتفعيل النظام\n"
            "• `.كتم` ➥ لكتم الشخص (بالرد)\n"
            "• `.فك كتم` ➥ لفك الكتم (بالرد)\n"
            "• `.تفاعلي` ➥ عرض معلوماتك\n"
            "• `.كشف` ➥ كشف الحساب (بالرد)\n\n"
            "★────────☭────────★"
        )
        await event.edit(text)

    # 2. تفعيل المجموعة
    elif cmd == ".تفعيل مجموعه":
        if not event.is_group: return
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري تفعيل مجموعتك 〕 {f} ⌯")
            await asyncio.sleep(0.2)
        db = await load_db()
        if cid not in db:
            db[cid] = {"muted": [], "msgs": {}}
            await save_db(db)
        await event.edit(f"⌯ {VORTEX[0]} 〔 تم تفعيل مجموعتك بنجاح 〕 {VORTEX[0]} ⌯")
        await asyncio.sleep(5); await event.delete()

    # 3. الكتم
    elif cmd == ".كتم" and event.is_reply:
        db = await load_db()
        if cid not in db: return await event.edit("⚠️ فعل المجموعة أولاً")
        reply = await event.get_reply_message()
        uid = reply.sender_id
        if uid == (await get_owner_id()): return await event.edit("⚠️ ما تكدر تكتم نفسك")
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري كتم الشخص 〕 {f} ⌯"); await asyncio.sleep(0.1)
        if uid not in db[cid]["muted"]:
            db[cid]["muted"].append(uid); await save_db(db)
        await event.edit(f"⌯ {VORTEX[0]} 〔 تم كتمه بنجاح 〕 {VORTEX[0]} ⌯")

    # 4. فك الكتم
    elif cmd == ".فك كتم" and event.is_reply:
        db = await load_db()
        reply = await event.get_reply_message()
        uid = reply.sender_id
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري فك الكتم 〕 {f} ⌯"); await asyncio.sleep(0.1)
        if uid in db.get(cid, {}).get("muted", []):
            db[cid]["muted"].remove(uid); await save_db(db)
        await event.edit(f"⌯ {VORTEX[0]} 〔 تم الفك بنجاح 〕 {VORTEX[0]} ⌯")

    # 5. تفاعلي
    elif cmd == ".تفاعلي":
        me = await client.get_me()
        full = await client(functions.users.GetFullUserRequest(me.id))
        db = await load_db()
        count = db.get(cid, {}).get("msgs", {}).get(str(me.id), 0)
        text = (
            "★────────☭────────★\n"
            "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {me.first_name}\n"
            f"• 𝑼𝒔𝒆𝒓 ⌯ @{me.username or 'None'}\n"
            f"• 𝑴𝒂𝒔𝒔𝒆𝒈𝒆 ⌯ {count}\n"
            "•  ⌯\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )
        await event.edit(text, link_preview=False)

    # 6. كشف
    elif cmd == ".كشف" and event.is_reply:
        reply = await event.get_reply_message()
        user = await client.get_entity(reply.sender_id)
        full = await client(functions.users.GetFullUserRequest(user.id))
        db = await load_db()
        count = db.get(cid, {}).get("msgs", {}).get(str(user.id), 0)
        date = user.date.strftime("%Y/%m/%d") if hasattr(user, 'date') and user.date else "قديم"
        text = (
            "★────────☭────────★\n"
            "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {user.first_name}\n"
            f"• 𝑰𝒅 ⌯ `{user.id}`\n"
            f"• 𝑱𝒐𝒊𝒏 𝑫𝒂𝒕𝒆 ⌯ {date}\n"
            f"• 𝑴𝒂𝒔𝒔𝒆𝒈𝒆 ⌯ {count}\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )
        photo = await client.download_profile_photo(user.id)
        await client.send_file(event.chat_id, photo, caption=text); await event.delete()

# --- المحرك العام (لحذف المكتومين والعداد) ---
@client.on(events.NewMessage())
async def handler(event):
    if not event.is_group: return
    db = await load_db()
    cid = str(event.chat_id)
    if cid not in db: return
    
    uid = str(event.sender_id)
    # العداد
    db[cid]["msgs"][uid] = db[cid]["msgs"].get(uid, 0) + 1
    await save_db(db)
    
    # حذف المكتومين
    if event.sender_id in db[cid].get("muted", []):
        try: await event.delete()
        except: pass
