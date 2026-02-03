import __main__, os, json, asyncio
from telethon import events

# استخراج الكلاينت والمسارات
client = getattr(__main__, 'client', None)
DB_FILE = "memes_db.json"

# دالة جلب البيانات المصلحة (تعالج أخطاء التنسيق تلقائياً)
def get_memes_safe():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            # صلح مشكلة كلمة here إذا انوجدت بالملف
            if content.startswith("here"):
                content = content[4:].strip()
            return json.loads(content)
    except Exception:
        return {}

# ==========================================
# 1. نظام البحث والسحب المباشر (.م [الاسم])
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م\s+(.*)$"))
async def play_meme_legendary(event):
    query = event.pattern_match.group(1).strip()
    memes = get_memes_safe()
    
    if not memes:
        return await event.edit("⚠️ **قاعدة البيانات فارغة أو الملف معطوب!**")

    # نظام البحث الذكي (يبحث عن الكلمة في أي مكان بالاسم)
    found_key = None
    for name in memes.keys():
        if query.lower() in name.lower():
            found_key = name
            break
    
    if found_key:
        await event.edit(f"🚀 **جاري سحب: {found_key}...**")
        try:
            # السحب والإرسال كبصمة صوتية مباشرة
            await client.send_file(
                event.chat_id, 
                memes[found_key], 
                voice_note=True, # يحولها لبصمة
                reply_to=event.reply_to_msg_id
            )
            await event.delete() # حذف رسالة "جاري السحب"
        except Exception as e:
            await event.edit(f"❌ **الرابط معطوب أو القناة خاصة:**\n`{str(e)}`")
    else:
        await event.edit(f"🔍 **لم أجد بصمة باسم ({query})!**")

# ==========================================
# 2. عرض قائمة الميمز المتوفرة (.ميمز)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ميمز$"))
async def list_memes_legendary(event):
    memes = get_memes_safe()
    if not memes:
        return await event.edit("⚠️ **لا توجد بصمات مضافة!**")
    
    res = "★────────☭────────★\n"
    res += "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑴𝑬𝑴𝑬𝑺 • ☭\n"
    res += "★────────☭────────★\n\n"
    for name in memes.keys():
        res += f"• `{name}`\n"
    res += "\n• للاستدعاء: `.م [الاسم]`"
    await event.edit(res)
