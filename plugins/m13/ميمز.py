import __main__, os, json
from telethon import events

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
MEM_FILE = "mem.json"
SUDO_ID = 5580918933  # آيدي المطور المسموح له بالإضافة

# دالة جلب البيانات من الملف
def get_mem_db():
    if not os.path.exists(MEM_FILE):
        return {}
    try:
        with open(MEM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# دالة حفظ البيانات للملف
def save_mem_db(data):
    with open(MEM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 1. أمر إضافة صوت (للمطور فقط)
# الصيغة: .اضافة ميمز [الرابط] [الاسم]
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة ميمز\s+(https?://t\.me/\S+)\s+(.*)$"))
async def add_meme_sudo(event):
    if event.sender_id != SUDO_ID:
        return await event.edit("⚠️ **هذا الأمر مخصص للمطور فقط!**")
    
    link = event.pattern_match.group(1)
    name = event.pattern_match.group(2).strip()
    
    db = get_mem_db()
    db[name] = link
    save_mem_db(db)
    
    await event.edit(f"✅ **تمت إضافة الصوت بنجاح!**\n• الاسم: `{name}`\n• الرابط: [اضغط هنا]({link})", link_preview=False)

# ==========================================
# 2. أمر عرض قائمة الأصوات (.ميمز)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ميمز$"))
async def list_memes_dynamic(event):
    db = get_mem_db()
    if not db:
        return await event.edit("⚠️ **قائمة الميمز فارغة! استخدم أمر الإضافة أولاً.**")
    
    res = "★────────☭────────★\n"
    res += "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑴𝑬𝑴𝑬𝑺 • ☭\n"
    res += "★────────☭────────★\n\n"
    res += "• **الأصوات المضافة حالياً:**\n\n"
    
    for i, name in enumerate(db.keys(), 1):
        res += f"{i}- `{name}`\n"
        
    res += "\n• للاستدعاء أرسل: `.م [اسم الصوت]`\n"
    res += "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    await event.edit(res)

# ==========================================
# 3. أمر تشغيل الصوت (.م [الاسم])
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م\s+(.*)$"))
async def play_meme_dynamic(event):
    query = event.pattern_match.group(1).strip()
    db = get_mem_db()
    
    # البحث الذكي عن الاسم
    found_key = next((k for k in db if query.lower() in k.lower()), None)
    
    if found_key:
        await event.edit(f"🚀 **جاري سحب: {found_key}...**")
        try:
            await client.send_file(
                event.chat_id, 
                db[found_key], 
                voice_note=True, # يرسلها بصمة
                reply_to=event.reply_to_msg_id
            )
            await event.delete()
        except Exception as e:
            await event.edit(f"❌ **فشل السحب! تأكد أن الرابط شغال والقناة عامة.**\n`{str(e)}`")
    else:
        await event.edit(f"🔍 لم أجد صوت باسم `{query}` في القائمة.")
