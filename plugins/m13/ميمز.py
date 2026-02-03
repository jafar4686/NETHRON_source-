import __main__, os, json
from telethon import events

client = getattr(__main__, 'client', None)
DB_FILE = "memes_db.json"

# دالة لجلب البيانات من ملف الـ JSON
def get_memes():
    if not os.path.exists(DB_FILE):
        # إذا الملف مو موجود نسوي واحد فارغ
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ==========================================
# 1. أمر البحث والاستدعاء (.م [اسم البصمة])
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م\s+(.*)$"))
async def play_meme(event):
    search_query = event.pattern_match.group(1).strip()
    memes = get_memes()
    
    # البحث عن أقرب اسم (البحث الذكي)
    found_key = None
    for name in memes.keys():
        if search_query in name: # إذا الكلمة موجودة ضمن الاسم
            found_key = name
            break
    
    if found_key:
        # حذف رسالة الأمر لإرسال البصمة بدالها
        await event.delete()
        # إرسال البصمة مباشرة من الرابط
        await client.send_file(
            event.chat_id, 
            memes[found_key], 
            voice_note=True, # لإرسالها كبصمة
            reply_to=event.reply_to_msg_id
        )
    else:
        await event.edit(f"⚠️ **لم أجد بصمة باسم ({search_query}) في القائمة!**")

# ==========================================
# 2. عرض كل قائمة الميمز (.ميمز)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ميمز$"))
async def list_memes(event):
    memes = get_memes()
    if not memes:
        return await event.edit("⚠️ **قائمة الميمز فارغة حالياً!**")
    
    menu = (
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑴𝑬𝑴𝑬𝑺 • ☭\n"
        "★────────☭────────★\n\n"
        "• للاستدعاء أرسل: `.م + اسم البصمة`\n\n"
    )
    
    for name in memes.keys():
        menu += f"• `{name}`\n"
        
    menu += "\n• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    await event.edit(menu)
