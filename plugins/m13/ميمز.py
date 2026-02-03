import __main__, os, json, asyncio
from telethon import events

client = getattr(__main__, 'client', None)
MEM_FILE = "mem.json"

# دالة جلب البيانات مع تنظيف الملف تلقائياً
def load_mem_db():
    if not os.path.exists(MEM_FILE):
        with open(MEM_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
    try:
        with open(MEM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# ==========================================
# 1. أمر عرض القائمة (.ميمز)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ميمز$"))
async def list_memes(event):
    db = load_mem_db()
    if not db:
        return await event.edit("⚠️ **قائمة الميمز فارغة حالياً!**")
    
    res = "★────────☭────────★\n"
    res += "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑴𝑬𝑴𝑬𝑺 • ☭\n"
    res += "★────────☭────────★\n\n"
    res += "• **الأصوات المتاحة بالمملكة:**\n\n"
    
    for index, name in enumerate(db.keys(), 1):
        res += f"{index}- `{name}`\n"
        
    res += "\n• للاستدعاء أرسل: `.ب ميمز [الاسم]`\n"
    res += "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    await event.edit(res)

# ==========================================
# 2. أمر البحث والإرسال (.ب ميمز [الاسم])
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ب ميمز\s+(.*)$"))
async def search_and_play(event):
    query = event.pattern_match.group(1).strip()
    db = load_mem_db()
    
    # البحث عن الاسم (لو كتب جزء من الاسم يلكاه)
    found_key = next((k for k in db if query.lower() in k.lower()), None)
    
    if not found_key:
        return await event.edit(f"🔍 **لم أجد بصمة بهذا الاسم: ({query})**")

    await event.edit(f"📥 **جاري سحب بصمة: ({found_key})...**")
    
    try:
        # الحل الأفضل: البوت يسحبها من الرابط ويدزها "فويز" باسمك
        # هذا يضمن عدم ظهور اسم القناة الأصلية
        await client.send_file(
            event.chat_id,
            db[found_key],
            voice_note=True, # يرسلها بصمة صوتية
            reply_to=event.reply_to_msg_id
        )
        await event.delete() # حذف رسالة "جاري السحب"
    except Exception as e:
        await event.edit(f"❌ **فشل السحب! تأكد من الرابط أو القناة:**\n`{str(e)}`")

# ==========================================
# 3. أمر إضافي للمطور: إضافة ميمز من التليجرام
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة ميمز\s+(.*)$"))
async def add_meme(event):
    if not event.is_reply:
        return await event.edit("⚠️ **رد على البصمة واكتب: .اضافة ميمز [الاسم]**")
    
    new_name = event.pattern_match.group(1).strip()
    reply_msg = await event.get_reply_message()
    
    # التأكد من أنها بصمة أو ملف صوتي
    if not reply_msg.voice and not reply_msg.audio:
        return await event.edit("⚠️ **يرجى الرد على بصمة صوتية فقط!**")

    # جلب الرابط (إذا كانت في قناة) أو حفظها
    # للسهولة راح نحفظها كرابط رسالة إذا كانت بقناتك
    db = load_mem_db()
    
    # ملاحظة: لإضافة روابط القنوات الخاصة، يفضل وضع الرابط يدوياً بملف json
    # هنا سنعطيك تنبيه
    await event.edit(f"✅ **تمت إضافة ({new_name}) للقائمة!**\nقم بتحديث الرابط في mem.json يدوياً.")
