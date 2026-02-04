import __main__, os, json, asyncio
from telethon import events

# استخراج الكلاينت والبيانات الأساسية
client = getattr(__main__, 'client', None)
MEM_FILE = "mem.json"
SUDO_IDS = [5580918933, 7273666832]  # قائمة المطورين
VORTEX = ["◜", "◝", "◞", "◟"]

# --- دالات قاعدة البيانات ---
def get_db(file):
    if not os.path.exists(file): return {}
    try:
        with open(file, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_db(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 1. منيو الميمز الملكي (.م13)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م13$"))
async def menu_13(event):
    for f in VORTEX:
        await event.edit(f"⌯ {f} جاري فتح سستم الميمز {f} ⌯")
        await asyncio.sleep(0.05)
        
    msg = (
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑴𝑬𝑴𝑬𝑺 • ☭\n"
        "★────────☭────────★\n\n"
        "• `.ميمز` ⌯ لعرض كافة الأصوات المتاحة\n"
        "• `.م [الاسم]` ⌯ لتشغيل بصمة محددة\n"
        "• `.اضافة ميمز` [الرابط] [الاسم] ⌯ (للمطورين)\n"
        "• `.حذف ميمز` [الاسم] ⌯ (للمطورين)\n\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )
    await event.edit(msg)

# ==========================================
# 2. إضافة بصمة (تحقق من الاسم والرابط)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة ميمز\s+(https?://t\.me/\S+)\s+(.*)$"))
async def add_meme(event):
    if event.sender_id not in SUDO_IDS:
        return await event.edit("⚠️ **هذا الأمر مخصص للمطورين المعتمدين فقط!**")
    
    link = event.pattern_match.group(1).strip()
    name = event.pattern_match.group(2).strip()
    db = get_db(MEM_FILE)
    
    # 1. التحقق من تكرار الاسم
    if name in db:
        return await event.edit(f"⚠️ **الاسم ({name}) موجود مسبقاً في القائمة!**")
    
    # 2. التحقق من تكرار الرابط
    if link in db.values():
        # إذا الرابط موجود، نطلع الاسم المرتبط بيه حتى يعرف المستخدم
        existing_name = [k for k, v in db.items() if v == link][0]
        return await event.edit(f"⚠️ **هذا الرابط مضاف مسبقاً باسم:** `{existing_name}`")
    
    # الإضافة بعد النجاح في التحقق
    db[name] = link
    save_db(MEM_FILE, db)
    
    await event.edit(
        "★────────☭────────★\n"
        "✅ **تمت الإضافة للملكية بنجاح**\n"
        f"• الاسم: `{name}`\n"
        "• الحالة: تم التحقق والحفظ 💾\n"
        "★────────☭────────★"
    )

# ==========================================
# 3. حذف بصمة
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حذف ميمز\s+(.*)$"))
async def delete_meme(event):
    if event.sender_id not in SUDO_IDS: return
    name = event.pattern_match.group(1).strip()
    db = get_db(MEM_FILE)
    
    if name in db:
        del db[name]
        save_db(MEM_FILE, db)
        await event.edit(f"🗑️ **تم حذف البصمة ({name}) نهائياً.**")
    else:
        await event.edit(f"🔍 لم يتم العثور على الاسم `{name}`!")

# ==========================================
# 4. عرض القائمة والتشغيل
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ميمز$"))
async def list_memes(event):
    db = get_db(MEM_FILE)
    if not db: return await event.edit("⚠️ القائمة فارغة!")
    
    res = "★────────☭────────★\n   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑴𝑬𝑴𝑬𝑺 • ☭\n★────────☭────────★\n\n"
    for i, name in enumerate(db.keys(), 1):
        res += f"{i}- `{name}`\n"
    res += "\n• للاستدعاء: `.م [الاسم]`"
    await event.edit(res)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م\s+(.*)$"))
async def play_meme(event):
    query = event.pattern_match.group(1).strip()
    db = get_db(MEM_FILE)
    found_key = next((k for k in db if query.lower() in k.lower()), None)
    
    if found_key:
        try:
            for f in VORTEX:
                await event.edit(f"⌯ {f} جاري سحب البصمة {f} ⌯")
                await asyncio.sleep(0.05)
            await client.send_file(event.chat_id, db[found_key], voice_note=True, reply_to=event.reply_to_msg_id)
            await event.delete()
        except: await event.edit("❌ خطأ في السحب.")
    else: await event.edit(f"🔍 لم أجد: `{query}`")
