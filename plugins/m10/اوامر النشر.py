import __main__, os, json, asyncio
from telethon import events, functions, types

# استخراج الكلاينت والبيانات
client = getattr(__main__, 'client', None)
BC_FILE = "broadcast.json"
VORTEX = ["◜", "◝", "◞", "◟"]

# متغيرات السيطرة
running_bc = {"all": False, "db": False}

def get_bc_db():
    if not os.path.exists(BC_FILE):
        with open(BC_FILE, "w", encoding="utf-8") as f: json.dump([], f)
        return []
    try:
        with open(BC_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def save_bc_db(data):
    with open(BC_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

# ==========================================
# 1. المنيو الملكي (.م10)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م10$"))
async def menu_broadcast(event):
    msg = (
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑩𝑹𝑶𝑨𝑫𝑪𝑨𝑺𝑻 • ☭\n"
        "★────────☭────────★\n\n"
        "• `.نشر عام` [الوقت] ⌯ النشر في **كل القنوات** التي منضم بها\n"
        "• `.نشر محدد` [الوقت] ⌯ النشر في **قنوات ملف الجاسون** فقط\n"
        "• `.اضافة قناة` [الرابط] ⌯ إضافة قناة لملف النشر المحدد\n"
        "• `.قنواتي` ⌯ عرض قنوات ملف الجاسون\n"
        "• `.ايقاف نشر عام` ⌯ إيقاف النشر في كل القنوات\n"
        "• `.ايقاف نشر محدد` ⌯ إيقاف نشر قنوات الملف\n"
        "• `.حذف القنوات` ⌯ تصفير سجل ملف الجاسون\n\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )
    await event.edit(msg)

# ==========================================
# 2. النشر العام (.نشر عام [الوقت]) - لكل قنوات الحساب
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نشر عام\s+(\d+)$"))
async def broadcast_all(event):
    if not event.is_reply: return await event.edit("⚠️ **رد على رسالة واكتب .نشر عام [الوقت]**")
    
    seconds = int(event.pattern_match.group(1))
    if seconds < 200: return await event.edit("⚠️ **للأمان، أقل وقت 200 ثانية.**")
    
    reply_msg = await event.get_reply_message()
    running_bc["all"] = True
    await event.edit("🚀 **جاري بدء النشر في جميع القنوات المنضم إليها...**")
    
    while running_bc["all"]:
        # جلب كل الحوارات وتصفية القنوات فقط
        all_chats = await client.get_dialogs()
        channels = [d for d in all_chats if d.is_channel]
        
        for ch in channels:
            if not running_bc["all"]: break
            try:
                await client.forward_messages(ch.id, reply_msg)
                await asyncio.sleep(2) # تأخير بسيط للأمان
            except: continue
            
        await event.edit(f"✅ **اكتملت موجة النشر العام!**\nالموجة القادمة بعد `{seconds}` ثانية.")
        for _ in range(seconds):
            if not running_bc["all"]: break
            await asyncio.sleep(1)

# ==========================================
# 3. النشر المحدد (.نشر محدد [الوقت]) - لقنوات الملف فقط
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نشر محدد\s+(\d+)$"))
async def broadcast_db(event):
    if not event.is_reply: return await event.edit("⚠️ **رد على رسالة واكتب .نشر محدد [الوقت]**")
    
    seconds = int(event.pattern_match.group(1))
    db = get_bc_db()
    if not db: return await event.edit("⚠️ **ملف الجاسون فارغ! أضف قنوات أولاً.**")
    
    reply_msg = await event.get_reply_message()
    running_bc["db"] = True
    await event.edit(f"🚀 **بدأ النشر في {len(db)} قناة من ملف الجاسون...**")
    
    while running_bc["db"]:
        for channel_link in db:
            if not running_bc["db"]: break
            try:
                await client.forward_messages(channel_link, reply_msg)
                await asyncio.sleep(2)
            except: continue
        
        await event.edit(f"✅ **اكتمل النشر المحدد!**\nالموجة القادمة بعد `{seconds}` ثانية.")
        for _ in range(seconds):
            if not running_bc["db"]: break
            await asyncio.sleep(1)

# ==========================================
# 4. أوامر الإدارة والإيقاف
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف نشر عام$"))
async def stop_all_bc(event):
    running_bc["all"] = False
    await event.edit("🛑 **تم إيقاف النشر العام (كل القنوات).**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف نشر محدد$"))
async def stop_db_bc(event):
    running_bc["db"] = False
    await event.edit("🛑 **تم إيقاف النشر المحدد (قنوات الملف).**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة قناة\s+(.*)$"))
async def add_to_db(event):
    link = event.pattern_match.group(1).strip()
    db = get_bc_db()
    if link not in db:
        db.append(link)
        save_bc_db(db)
        await event.edit(f"✅ **تمت إضافة القناة لملف الجاسون:**\n`{link}`")
    else: await event.edit("⚠️ موجودة مسبقاً.")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حذف القنوات$"))
async def clear_db(event):
    save_bc_db([])
    await event.edit("🗑️ **تم تصفير قنوات ملف الجاسون.**")
