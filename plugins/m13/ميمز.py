import __main__, os, json, asyncio
from telethon import events

client = getattr(__main__, 'client', None)
DB_FILE = "memes_db.json"

# دالة ذكية تقرأ الملف حتى لو بيه "زبالة" برمجية
def load_memes_fixed():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            # تنظيف كلمة here أو أي كتابة قبل القوس {
            if "{" in data:
                data = data[data.find("{"):] 
            return json.loads(data)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return {}

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م\s+(.*)$"))
async def play_meme_v3(event):
    query = event.pattern_match.group(1).strip()
    memes = load_memes_fixed()
    
    if not memes:
        return await event.edit("⚠️ **الملف بعده معطوب! امسح كلمة here وخلي بس الأقواس { }**")

    # البحث عن الاسم
    found_key = next((k for k in memes if query in k), None)
    
    if found_key:
        await event.edit(f"📥 **جاري جلب البصمة: {found_key}...**")
        try:
            # الحل اللي ردته: تنزيل الملف مؤقتاً بجهاز البوت ثم إرساله
            # نستخدم الرابط كملف، تليجرام راح يحمله ويرسله بصمة
            file_to_send = memes[found_key]
            
            await client.send_file(
                event.chat_id, 
                file_to_send, 
                voice_note=True, # يخليها بصمة
                reply_to=event.reply_to_msg_id
            )
            await event.delete()
        except Exception as e:
            await event.edit(f"❌ **الرابط غلط أو القناة خاصة:**\n`{str(e)}`")
    else:
        await event.edit(f"🔍 لم أجد بصمة باسم `{query}`")
