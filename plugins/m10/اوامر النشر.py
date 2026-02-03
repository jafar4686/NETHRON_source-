import __main__, os, json, asyncio
from telethon import events

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
BC_FILE = "broadcast.json"
VORTEX = ["◜", "◝", "◞", "◟"]

# متغيرات السيطرة في الرام
running_bc = {"general": False, "specific": {}}

def get_bc_db():
    if not os.path.exists(BC_FILE):
        with open(BC_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []
    try:
        with open(BC_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_bc_db(data):
    with open(BC_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# ==========================================
# 1. قائمة الأوامر (.م10)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م10$"))
async def menu_broadcast(event):
    for f in VORTEX:
        await event.edit(f"⌯ {f} جاري فتح قائمة النشر {f} ⌯")
        await asyncio.sleep(0.05)
    
    msg = (
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑩𝑹𝑶𝑨𝑫𝑪𝑨𝑺𝑻 • ☭\n"
        "★────────☭────────★\n\n"
        "• `.اضافة قناة` [الرابط] ⌯ لإضافة قناة للسجل\n"
        "• `.قنواتي` ⌯ لعرض القنوات المضافة\n"
        "• `.نشر` [الثواني] ⌯ للنشر التلقائي (بالرد)\n"
        "• `.نشر محدد` [الثواني] [الرابط] ⌯ نشر لقناة وحدة\n"
        "• `.ايقاف نشر` ⌯ لإيقاف النشر العام\n"
        "• `.ايقاف نشر محدد` ⌯ لإيقاف المحدد\n"
        "• `.حذف القنوات` ⌯ لتصفير سجل القنوات\n\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )
    await event.edit(msg)

# ==========================================
# 2. إضافة قناة (.اضافة قناة [الرابط])
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة قناة\s+(.*)$"))
async def add_ch(event):
    link = event.pattern_match.group(1).strip()
    db = get_bc_db()
    if link not in db:
        db.append(link)
        save_bc_db(db)
        await event.edit(f"✅ **تمت إضافة القناة بنجاح:**\n`{link}`")
    else:
        await event.edit("⚠️ **هذه القناة مضافة مسبقاً!**")

# ==========================================
# 3. النشر العام (.نشر [الوقت])
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نشر\s+(\d+)$"))
async def start_broadcast(event):
    if not event.is_reply:
        return await event.edit("⚠️ **يجب الرد على الرسالة التي تريد نشرها!**")
    
    seconds = int(event.pattern_match.group(1))
    if seconds < 200:
        return await event.edit("⚠️ **للأمان، أقل وقت مسموح هو 200 ثانية.**")
    
    db = get_bc_db()
    if not db:
        return await event.edit("⚠️ **سجل القنوات فارغ! أضف قناة أولاً.**")
    
    reply_msg = await event.get_reply_message()
    running_bc["general"] = True
    
    await event.edit("🚀 **بدأت الإذاعة الملكية.. سيتم النشر وتكراره تلقائياً.**")
    
    while running_bc["general"]:
        # حركات الدوامة عند كل موجة نشر
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري النشر الآن في {len(db)} قناة 〕 {f} ⌯")
            await asyncio.sleep(0.1)

        for channel in db:
            if not running_bc["general"]: break
            try:
                await client.forward_messages(channel, reply_msg)
                await asyncio.sleep(1.5) # تأخير بسيط للأمان بين قناة وأخرى
            except:
                continue
        
        # انتظار الوقت مع عداد بسيط
        await event.edit(f"✅ **اكتملت موجة النشر!**\nالموجة القادمة بعد `{seconds}` ثانية.")
        
        count = seconds
        while count > 0 and running_bc["general"]:
            await asyncio.sleep(1)
            count -= 1

# ==========================================
# 4. نشر محدد (.نشر محدد [الوقت] [الرابط])
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نشر محدد\s+(\d+)\s+(.*)$"))
async def start_specific_bc(event):
    if not event.is_reply:
        return await event.edit("⚠️ **رد على الرسالة أولاً!**")
    
    seconds = int(event.pattern_match.group(1))
    target = event.pattern_match.group(2).strip()
    if seconds < 200:
        return await event.edit("⚠️ **أقل وقت هو 200 ثانية.**")
    
    reply_msg = await event.get_reply_message()
    running_bc["specific"][target] = True
    
    await event.edit(f"🎯 **بدأ النشر المحدد في القناة:** `{target}`")
    
    while running_bc["specific"].get(target):
        try:
            await client.forward_messages(target, reply_msg)
            await asyncio.sleep(seconds)
        except:
            await event.edit(f"❌ **فشل النشر في:** `{target}`")
            break

# ==========================================
# 5. أوامر الإيقاف والحذف
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف نشر$"))
async def stop_general(event):
    running_bc["general"] = False
    await event.edit("🛑 **تم إيقاف النشر العام بنجاح.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف نشر محدد$"))
async def stop_specific(event):
    running_bc["specific"].clear()
    await event.edit("🛑 **تم إيقاف جميع عمليات النشر المحدد.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حذف القنوات$"))
async def clear_database(event):
    save_bc_db([])
    await event.edit("🗑️ **تم تصفير سجل القنوات بنجاح.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.قنواتي$"))
async def list_ch(event):
    db = get_bc_db()
    if not db: return await event.edit("⚠️ القائمة فارغة.")
    res = "📢 **قنوات النشر المضافة:**\n\n"
    for i, link in enumerate(db, 1):
        res += f"{i}- `{link}`\n"
    await event.edit(res)
