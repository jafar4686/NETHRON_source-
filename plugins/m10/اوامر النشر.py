import __main__, os, json, asyncio
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
BC_FILE = "broadcast.json"
VORTEX = ["◜", "◝", "◞", "◟"]

# متغيرات السيطرة (في الرام لضمان السرعة)
running_broadcasts = {} # للنشر العام
running_specific = {}    # للنشر المحدد

def get_bc_db():
    if not os.path.exists(BC_FILE): return []
    try:
        with open(BC_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def save_bc_db(data):
    with open(BC_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

# ==========================================
# 1. إضافة قناة للسجل (.اضافة قناة [الرابط])
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة قناة\s+(.*)$"))
async def add_channel(event):
    link = event.pattern_match.group(1).strip()
    db = get_bc_db()
    if link not in db:
        db.append(link)
        save_bc_db(db)
        await event.edit(
            "★────────☭────────★\n"
            "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑩𝑹𝑶𝑨𝑫𝑪𝑨𝑺𝑻 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑳𝒊𝒏𝒌 ⌯ {link}\n"
            "• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **تمت الإضافة بنجاح** ✅\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
        )
    else:
        await event.edit("⚠️ **هذه القناة مضافة مسبقاً!**")

# ==========================================
# 2. النشر العام (.نشر [الوقت])
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نشر\s+(\d+)$"))
async def start_broadcast(event):
    if not event.is_reply:
        return await event.edit("⚠️ **يرجى الرد على الرسالة لتحديد محتوى النشر!**")
    
    seconds = int(event.pattern_match.group(1))
    if seconds < 200: return await event.edit("⚠️ **للأمان، أقل وقت هو 200 ثانية!**")
    
    db = get_bc_db()
    if not db: return await event.edit("⚠️ **قائمة القنوات فارغة! أضف قنوات أولاً.**")
    
    reply_msg = await event.get_reply_message()
    running_broadcasts[event.chat_id] = True
    
    await event.edit("🚀 **جاري بدء الإذاعة الملكية في جميع القنوات...**")
    
    while running_broadcasts.get(event.chat_id):
        # دوامة قبل كل عملية نشر كاملة
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري النشر العام الآن 〕 {f} ⌯")
            await asyncio.sleep(0.1)

        for channel in db:
            if not running_broadcasts.get(event.chat_id): break
            try:
                await client.forward_messages(channel, reply_msg)
            except: continue
        
        # انتظار الوقت المحدد مع تحديث بسيط
        await event.edit(f"✅ **تم النشر!**\nالموجة القادمة بعد `{seconds}` ثانية.")
        await asyncio.sleep(seconds)

# ==========================================
# 3. نشر محدد (.نشر محدد [الوقت] [الرابط])
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نشر محدد\s+(\d+)\s+(.*)$"))
async def start_specific(event):
    if not event.is_reply: return await event.edit("⚠️ **رد على رسالة النشر أولاً!**")
    
    seconds = int(event.pattern_match.group(1))
    target = event.pattern_match.group(2).strip()
    if seconds < 200: return await event.edit("⚠️ **للأمان، أقل وقت هو 200 ثانية!**")
    
    reply_msg = await event.get_reply_message()
    running_specific[target] = True
    
    await event.edit(f"🎯 **بدأ النشر المحدد في القناة:**\n`{target}`")
    
    while running_specific.get(target):
        try:
            for f in VORTEX:
                await event.edit(f"⌯ {f} 〔 جاري النشر المحدد 〕 {f} ⌯")
                await asyncio.sleep(0.1)
                
            await client.forward_messages(target, reply_msg)
            await event.edit(f"✅ **نشر محدد ناجح!**\nالوقت: `{seconds}s` | القناة: `{target}`")
        except: 
            await event.edit(f"❌ **فشل النشر في القناة:** `{target}`")
            break
        await asyncio.sleep(seconds)

# ==========================================
# 4. أوامر الإيقاف (.ايقاف نشر / .ايقاف نشر محدد)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف نشر$"))
async def stop_bc(event):
    running_broadcasts[event.chat_id] = False
    await event.edit(
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑩𝑹𝑶𝑨𝑫𝑪𝑨𝑺𝑻 • ☭\n"
        "★────────☭────────★\n\n"
        "• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **تم إيقاف النشر العام** 🛑\n\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف نشر محدد$"))
async def stop_spec(event):
    running_specific.clear()
    await event.edit("🛑 **تم إيقاف جميع عمليات النشر المحدد بنجاح.**")

# ==========================================
# 5. عرض القنوات (.قنواتي)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.قنواتي$"))
async def list_channels(event):
    db = get_bc_db()
    if not db: return await event.edit("⚠️ **لا توجد قنوات مضافة للنشر!**")
    
    res = (
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑩𝑹𝑶𝑨𝑫𝑪𝑨𝑺𝑻 • ☭\n"
        "★────────☭────────★\n\n"
    )
    for i, link in enumerate(db, 1):
        res += f"{i}- {link}\n"
    res += "\n• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    await event.edit(res)
