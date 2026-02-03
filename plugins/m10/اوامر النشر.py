import __main__, os, json, asyncio
from telethon import events

client = getattr(__main__, 'client', None)
BC_FILE = "broadcast.json"
VORTEX = ["◜", "◝", "◞", "◟"]

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
    for f in VORTEX:
        await event.edit(f"⌯ {f} جاري فتح الإذاعة الملكية {f} ⌯")
        await asyncio.sleep(0.05)
    
    msg = (
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑩𝑹𝑶𝑨𝑫𝑪𝑨𝑺𝑻 • ☭\n"
        "★────────☭────────★\n\n"
        "• `.نشر عام` [وقت] ⌯ نشر في **كل القنوات** المنضم بها\n"
        "• `.نشر محدد` [وقت] ⌯ نشر في **قنوات الجاسون** فقط\n"
        "• `.اضافة قناة` [رابط] ⌯ إضافة قناة لسجل الجاسون\n"
        "• `.قنواتي` ⌯ عرض قنوات سجل الجاسون\n"
        "• `.ايقاف نشر عام` ⌯ إيقاف النشر الشامل\n"
        "• `.ايقاف نشر محدد` ⌯ إيقاف نشر سجل الجاسون\n"
        "• `.حذف القنوات` ⌯ تصفير سجل الجاسون\n\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )
    await event.edit(msg)

# ==========================================
# 2. النشر العام (كل قنوات الحساب)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نشر عام\s+(\d+)$"))
async def broadcast_all(event):
    if not event.is_reply: return await event.edit("⚠️ **عذراً، يجب الرد على رسالة لبدء النشر!**")
    
    seconds = int(event.pattern_match.group(1))
    if seconds < 200: return await event.edit("⚠️ **للأمان، أقل وقت هو 200 ثانية.**")
    
    reply_msg = await event.get_reply_message()
    running_bc["all"] = True
    
    while running_bc["all"]:
        all_chats = await client.get_dialogs()
        channels = [d for d in all_chats if d.is_channel]
        total = len(channels)
        success, fail = 0, 0
        
        await event.edit(f"🚀 **بدأ النشر العام في ({total}) قناة...**")
        
        for ch in channels:
            if not running_bc["all"]: break
            try:
                await client.forward_messages(ch.id, reply_msg)
                success += 1
            except: fail += 1
            await asyncio.sleep(1.5) # تأخير بسيط للأمان
            
        status_msg = (
            "★────────☭────────★\n"
            "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑩𝑹𝑶𝑨𝑫𝑪𝑨𝑺𝑻 • ☭\n"
            "★────────☭────────★\n\n"
            "• 𝑻𝒚𝒑𝒆 ⌯ **نشر عام شامل** 🌐\n"
            f"• 𝑻𝒐𝒕𝒂𝒍 𝑪𝒉𝒂𝒏𝒏𝒆𝒍𝒔 ⌯ `{total}`\n"
            f"• 𝑺𝒖𝒄𝒄𝒆𝒔𝒔 ⌯ `{success}` ✅\n"
            f"• 𝑭𝒂𝒊𝒍𝒆𝒅 ⌯ `{fail}` ❌\n\n"
            f"• سيتم التكرار بعد `{seconds}` ثانية.\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
        )
        await event.edit(status_msg)
        
        for _ in range(seconds):
            if not running_bc["all"]: break
            await asyncio.sleep(1)

# ==========================================
# 3. النشر المحدد (قنوات سجل الجاسون)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نشر محدد\s+(\d+)$"))
async def broadcast_db(event):
    if not event.is_reply: return await event.edit("⚠️ **عذراً، يجب الرد على رسالة أولاً!**")
    
    seconds = int(event.pattern_match.group(1))
    db = get_bc_db()
    if not db: return await event.edit("⚠️ **سجل الجاسون فارغ! أضف قنوات أولاً.**")
    
    reply_msg = await event.get_reply_message()
    running_bc["db"] = True
    
    while running_bc["db"]:
        total = len(db)
        success, fail = 0, 0
        await event.edit(f"🚀 **بدأ النشر المحدد في ({total}) قناة...**")
        
        for channel_link in db:
            if not running_bc["db"]: break
            try:
                await client.forward_messages(channel_link, reply_msg)
                success += 1
            except: fail += 1
            await asyncio.sleep(1.5)
        
        status_msg = (
            "★────────☭────────★\n"
            "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑩𝑹𝑶𝑨𝑫𝑪𝑨𝑺𝑻 • ☭\n"
            "★────────☭────────★\n\n"
            "• 𝑻𝒚𝒑𝒆 ⌯ **نشر محدد (جاسون)** 🎯\n"
            f"• 𝑻𝒐𝒕𝒂𝒍 𝑪𝒉𝒂𝒏𝒏𝒆𝒍𝒔 ⌯ `{total}`\n"
            f"• 𝑺𝒖𝒄𝒄𝒆𝒔𝒔 ⌯ `{success}` ✅\n"
            f"• 𝑭𝒂𝒊𝒍𝒆𝒅 ⌯ `{fail}` ❌\n\n"
            f"• سيتم التكرار بعد `{seconds}` ثانية.\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
        )
        await event.edit(status_msg)
        
        for _ in range(seconds):
            if not running_bc["db"]: break
            await asyncio.sleep(1)

# ==========================================
# 4. أوامر الإدارة والإيقاف (تنسيق ملكي)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف نشر عام$"))
async def stop_all_bc(event):
    running_bc["all"] = False
    await event.edit("🛑 **تم إيقاف النشر العام بنجاح.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف نشر محدد$"))
async def stop_db_bc(event):
    running_bc["db"] = False
    await event.edit("🛑 **تم إيقاف النشر المحدد بنجاح.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة قناة\s+(.*)$"))
async def add_to_db(event):
    link = event.pattern_match.group(1).strip()
    db = get_bc_db()
    if link not in db:
        db.append(link)
        save_bc_db(db)
        await event.edit(f"✅ **تمت إضافة القناة للسجل الملكي:**\n`{link}`")
    else: await event.edit("⚠️ **القناة مضافة مسبقاً!**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حذف القنوات$"))
async def clear_db(event):
    save_bc_db([])
    await event.edit("🗑️ **تم تصفير سجل الجاسون بالكامل.**")
