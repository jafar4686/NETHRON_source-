import __main__, os, json
from telethon import events

client = getattr(__main__, 'client', None)
DB_FILE = "memes_db.json"

def get_memes():
    if not os.path.exists(DB_FILE): return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            # لتجاوز خطأ كلمة here إذا نسيتها
            if content.startswith("here"): content = content[4:]
            return json.loads(content)
    except: return {}

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م\s+(.*)$"))
async def play_meme(event):
    query = event.pattern_match.group(1).strip()
    memes = get_memes()
    
    found_key = next((k for k in memes if query in k), None)
    
    if found_key:
        await event.edit("🚀 **جاري الاستدعاء...**")
        try:
            # سحب وإرسال كبصمة
            await client.send_file(
                event.chat_id, 
                memes[found_key], 
                voice_note=True,
                reply_to=event.reply_to_msg_id
            )
            await event.delete()
        except Exception as e:
            await event.edit(f"❌ **الخلل بالرابط أو القناة خاصة:**\n`{str(e)}`")
    else:
        await event.edit(f"🔍 لم أجد بصمة باسم `{query}`")
