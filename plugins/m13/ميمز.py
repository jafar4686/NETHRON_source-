import __main__, os, json
from telethon import events

client = getattr(__main__, 'client', None)
DB_FILE = "memes_db.json"

# دالة جلب البيانات مع ضمان اللغة العربية
def get_memes():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# ==========================================
# أمر الاستدعاء المصلح (.م [الاسم])
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م\s+(.*)$"))
async def play_meme(event):
    # تنظيف النص المكتوب من المسافات الزايدة
    search_query = event.pattern_match.group(1).strip()
    memes = get_memes()
    
    if not memes:
        return await event.edit("⚠️ **قاعدة البيانات فارغة! ضيف أصوات بالملف أولاً.**")

    found_key = None
    # بحث دقيق (Exact Match) أو بحث جزئي
    for name in memes.keys():
        if search_query == name or search_query in name:
            found_key = name
            break
    
    if found_key:
        try:
            # محاولة جلب الرابط وإرساله
            link = memes[found_key]
            await event.edit("🚀 **جاري سحب البصمة...**")
            
            await client.send_file(
                event.chat_id, 
                link, 
                voice_note=True, # إرسال كبصمة
                reply_to=event.reply_to_msg_id
            )
            await event.delete() # حذف كلمة "جاري سحب البصمة" بعد النجاح
        except Exception as e:
            await event.edit(f"❌ **فشل سحب البصمة من الرابط!**\nتأكد أن القناة عامة أو البوت موجود فيها.\n`{str(e)}`")
    else:
        # إذا ما لقى الاسم، يعرض المتاح حتى تراجع إملاءك
        all_names = "، ".join(memes.keys())
        await event.edit(f"🔍 **لم أجد: ({search_query})**\n\n✅ **المتوفر حالياً:**\n`{all_names}`")
