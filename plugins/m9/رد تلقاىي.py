import __main__, asyncio, json, os
from telethon import events

client = getattr(__main__, 'client', None)
REPLIES_FILE = "replies.json"
SETTINGS_FILE = "reply_settings.json"

# دالات مساعدة
def get_data(file, default):
    if not os.path.exists(file): return default
    with open(file, "r") as f: return json.load(f)

def save_data(file, data):
    with open(file, "w") as f: json.dump(data, f)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة رد (.+) (.+)"))
async def add_reply(event):
    word = event.pattern_match.group(1)
    response = event.pattern_match.group(2)
    data = get_data(REPLIES_FILE, {})
    data[word] = response
    save_data(REPLIES_FILE, data)
    await event.edit(f"✅ تم إضافة الرد:\n• الكلمة: {word}\n• الرد: {response}")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حذف رد (.+)"))
async def del_reply(event):
    word = event.pattern_match.group(1)
    data = get_data(REPLIES_FILE, {})
    if word in data:
        del data[word]
        save_data(REPLIES_FILE, data)
        await event.edit(f"🗑️ تم حذف رد: {word}")
    else:
        await event.edit("⚠️ الرد غير موجود.")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.رد عام (.+)"))
async def set_general(event):
    msg = event.pattern_match.group(1)
    settings = get_data(SETTINGS_FILE, {"status": False, "general": ""})
    settings["general"] = msg
    save_data(SETTINGS_FILE, settings)
    await event.edit(f"📢 تم ضبط الرد العام:\n• النص: {msg}")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(ت|ايقاف) الردود$"))
async def toggle_replies(event):
    cmd = event.text
    settings = get_data(SETTINGS_FILE, {"status": False, "general": ""})
    settings["status"] = True if "ت" in cmd else False
    save_data(SETTINGS_FILE, settings)
    status_text = "✅ تشغيل" if settings["status"] else "❌ إيقاف"
    await event.edit(f"⚙️ تم {status_text} نظام الردود")

# --- محرك الردود الذكي ---
@client.on(events.NewMessage(incoming=True))
async def reply_handler(event):
    settings = get_data(SETTINGS_FILE, {"status": False, "general": ""})
    if not settings["status"]: return
    
    replies = get_data(REPLIES_FILE, {})
    user_msg = event.text
    
    # 1. الأولوية للرد التلقائي (كلمة محددة)
    if user_msg in replies:
        await event.reply(replies[user_msg])
    # 2. إذا ماكو رد محدد، يرد بالرد العام (إذا موجود)
    elif settings["general"]:
        await event.reply(settings["general"])

# --- قائمة الردود .م9 ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م9$"))
async def menu9(event):
    klisha = (
        "★────────☭────────★\n"
        "   ☭ • 𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 • ☭\n"
        "★────────☭────────★\n\n"
        "⚙️ أوامر الردود التلقائية:\n"
        "• `.اضافة رد` [الكلمة] [الرد]\n"
        "• `.حذف رد` [الكلمة]\n"
        "• `.رد عام` [نص الرد لكل الناس]\n"
        "• `.قائمة الردود` ➥ عرض ردودك\n"
        "• `.ت الردود` / `.ايقاف الردود` \n\n"
        "★────────☭────────★"
    )
    await event.edit(klisha)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.قائمة الردود$"))
async def list_replies(event):
    replies = get_data(REPLIES_FILE, {})
    if not replies: return await event.edit("⚠️ لا توجد ردود مضافة.")
    
    msg = "◜ جاري تحميل قائمة الردود... ◝"
    await event.edit(msg)
    await asyncio.sleep(1.5) # تأثير التحميل اللي ردته
    
    out = "📋 **قائمة الردود المضافة:**\n\n"
    for word, resp in replies.items():
        out += f"• {word} ↤ {resp}\n"
    await event.edit(out)
