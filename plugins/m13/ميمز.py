import __main__, os, json, asyncio
from telethon import events, functions, types

# استخراج الكلاينت والبيانات الأساسية
client = getattr(__main__, 'client', None)
MEM_FILE = "mem.json"
SUDO_IDS = [5580918933, 7273666832]  # المطورين المعتمدين
VORTEX = ["◜", "◝", "◞", "◟"]

# --- دالات قاعدة البيانات ---
def get_db():
    if not os.path.exists(MEM_FILE): return {}
    try:
        with open(MEM_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_db(data):
    with open(MEM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 1. قائمة الأوامر الموحدة (.م13)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م13$"))
async def menu_13(event):
    for f in VORTEX:
        await event.edit(f"⌯ {f} جاري فتح قائمة الميمز {f} ⌯")
        await asyncio.sleep(0.05)
    msg = (
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑴𝑬𝑴𝑬𝑺 • ☭\n"
        "★────────☭────────★\n\n"
        "• `.ميمز` ⌯ عرض الأصوات (50 بصمة بالصفحة)\n"
        "• `.م` [الاسم] ⌯ لتشغيل البصمة المطلوبة\n"
        "• `.تجميع بصمات` [الرابط] [العدد] ⌯ سحب آلي\n"
        "• `.بحث` [الاسم] ⌯ بحث مطور (بالرد على القائمة)\n"
        "• `.اضافة ميمز` [الرابط] [الاسم] ⌯ إضافة يدوية\n"
        "• `.حذف ميمز` [الاسم] ⌯ حذف بصمة\n\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )
    await event.edit(msg)

# ==========================================
# 2. نظام الصفحات المطور (50 بصمة لكل صفحة)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ميمز$"))
async def list_memes_paged(event):
    db = get_db()
    if not db: return await event.edit("⚠️ القائمة فارغة حالياً!")
    keys = list(db.keys())
    page = 1
    start, end = 0, 50
    text = "★────────☭────────★\n   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑴𝑬𝑴𝑬𝑺 • ☭\n★────────☭────────★\n\n"
    for i, name in enumerate(keys[start:end], 1):
        text += f"{i}- `{name}`\n"
    text += f"\n• الصفحة: {page} | المجموع: {len(keys)}\n• للتقليب رد بـ `.التالي` أو `.السابق`\n• للبحث رد بـ `.بحث [الاسم]`"
    await event.edit(text)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(التالي|السابق)$"))
async def change_page(event):
    if not event.is_reply: return
    reply = await event.get_reply_message()
    if "𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑴𝑬𝑴𝑬𝑺" not in reply.text: return
    
    cmd = event.pattern_match.group(1)
    db = get_db()
    keys = list(db.keys())
    try:
        curr_page = int(reply.text.split("الصفحة: ")[1].split(" |")[0])
    except: curr_page = 1
    
    page = curr_page + 1 if cmd == "التالي" else curr_page - 1
    start = (page - 1) * 50
    if start < 0 or start >= len(keys): return await event.delete()
    
    text = "★────────☭────────★\n   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑴𝑬𝑴𝑬𝑺 • ☭\n★────────☭────────★\n\n"
    for i, name in enumerate(keys[start:start+50], start + 1):
        text += f"{i}- `{name}`\n"
    text += f"\n• الصفحة: {page} | المجموع: {len(keys)}\n• للتقليب رد بـ `.التالي` أو `.السابق`"
    await reply.edit(text)
    await event.delete()

# ==========================================
# 3. نظام البحث الذكي (بالتعديل الفوري)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.بحث\s+(.*)$"))
async def search_memes(event):
    if not event.is_reply: return await event.edit("⚠️ **رد على رسالة قائمة الميمز واكتب .بحث [الاسم]**")
    
    query = event.pattern_match.group(1).strip().lower()
    reply = await event.get_reply_message()
    db = get_db()
    
    matches = [name for name in db.keys() if query in name.lower()]
    
    if not matches:
        return await event.edit(f"🔍 لا توجد نتائج لـ: `{query}`")
    
    text = f"★────────☭────────★\n   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑺𝑬𝑨𝑹𝑪𝑯 • ☭\n★────────☭────────★\n\n🔎 نتائج البحث عن: `{query}`\n\n"
    for i, name in enumerate(matches[:20], 1):
        text += f"{i}- `{name}`\n"
    
    if len(matches) > 20:
        text += f"\n... وهناك {len(matches)-20} نتائج أخرى."
    text += "\n• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    
    await reply.edit(text)
    await event.delete()

# ==========================================
# 4. تجميع البصمات تلقائياً مع منع التكرار
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تجميع بصمات\s+(https?://t\.me/\S+)\s+(\d+)$"))
async def scrape_memes(event):
    if event.sender_id not in SUDO_IDS: return
    link, limit = event.pattern_match.group(1), int(event.pattern_match.group(2))
    db = get_db()
    added, skipped = 0, 0
    await event.edit("⚙️ **جاري الزحف وسحب البصمات.. انتظر قليلاً.**")
    
    async for msg in client.iter_messages(link, filter=types.InputMessagesFilterVoice()):
        if added >= limit: break
        name = msg.text.strip() if msg.text else f"بصمة_{msg.id}"
        file_link = f"{link}/{msg.id}"
        if name in db or file_link in db.values():
            skipped += 1
            continue
        db[name] = file_link
        added += 1
    save_db(db)
    await event.edit(f"★────────☭────────★\n✅ **اكتمل التجميع الملكي**\n• المضاف: `{added}`\n• المكرر: `{skipped}`\n★────────☭────────★")

# ==========================================
# 5. أمر التشغيل (.م [الاسم]) مع الدوامة
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م\s+(.*)$"))
async def play_meme(event):
    query = event.pattern_match.group(1).strip()
    db = get_db()
    found_key = next((k for k in db if query.lower() in k.lower()), None)
    
    if found_key:
        try:
            for f in VORTEX:
                await event.edit(f"⌯ {f} جاري سحب البصمة: `{found_key}` {f} ⌯")
                await asyncio.sleep(0.05)
            await client.send_file(event.chat_id, db[found_key], voice_note=True, reply_to=event.reply_to_msg_id)
            await event.delete()
        except: await event.edit("❌ فشل في جلب البصمة!")
    else: await event.edit(f"🔍 لم أجد بصمة باسم: `{query}`")

# ==========================================
# 6. إضافة وحذف يدوي (للمطورين)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة ميمز\s+(https?://t\.me/\S+)\s+(.*)$"))
async def add_manual(event):
    if event.sender_id not in SUDO_IDS: return
    link, name = event.pattern_match.group(1), event.pattern_match.group(2).strip()
    db = get_db()
    if name in db or link in db.values(): return await event.edit("⚠️ موجود مسبقاً!")
    db[name] = link
    save_db(db)
    await event.edit(f"✅ **تمت إضافة ({name}) للسجلات.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حذف ميمز\s+(.*)$"))
async def del_manual(event):
    if event.sender_id not in SUDO_IDS: return
    name = event.pattern_match.group(1).strip()
    db = get_db()
    if name in db:
        del db[name]
        save_db(db)
        await event.edit(f"🗑️ **تم حذف ({name}) من السجلات.**")
