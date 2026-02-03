import __main__, os, json
from telethon import events

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
MEM_FILE = "mem.json"

# دالة لجلب البيانات من ملف الـ JSON بشكل آمن
def get_mem_db():
    if not os.path.exists(MEM_FILE):
        return {}
    try:
        with open(MEM_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            # إذا الملف يبدأ بكلمات غريبة مثل here، نقوم بتنظيفه
            if "{" in data:
                data = data[data.find("{"):]
            return json.loads(data)
    except:
        return {}

# ==========================================
# 1. أمر عرض كل الأصوات المضافة (.ميمز)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ميمز$"))
async def list_all_memes(event):
    db = get_mem_db()
    if not db:
        return await event.edit("⚠️ **قائمة الملف فارغة أو الملف غير موجود!**")
    
    res = "★────────☭────────★\n"
    res += "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑴𝑬𝑴𝑬𝑺 • ☭\n"
    res += "★────────☭────────★\n\n"
    
    for i, name in enumerate(db.keys(), 1):
        res += f"{i}- `{name}`\n"
        
    res += "\n• للاستدعاء: `.م [اسم الصوت]`\n"
    res += "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    await event.edit(res)

# ==========================================
# 2. أمر البحث والسحب (.م [الاسم])
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م\s+(.*)$"))
async def play_from_file(event):
    query = event.pattern_match.group(1).strip()
    db = get_mem_db()
    
    # البحث عن الاسم داخل القائمة (بحث جزئي ذكي)
    found_key = next((k for k in db if query.lower() in k.lower()), None)
    
    if found_key:
        await event.edit(f"📥 **جاري سحب: {found_key}...**")
        try:
            # السحب والإرسال كبصمة (Voice Note)
            await client.send_file(
                event.chat_id, 
                db[found_key], 
                voice_note=True,
                reply_to=event.reply_to_msg_id
            )
            await event.delete()
        except Exception as e:
            await event.edit(f"❌ **فشل السحب من الرابط!**\nالسبب: `{str(e)}`")
    else:
        await event.edit(f"🔍 لم أجد صوت باسم `{query}` في ملف التخزين.")
