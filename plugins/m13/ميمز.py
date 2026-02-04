import __main__, os, json, asyncio
from telethon import events

# استخراج الكلاينت والبيانات الأساسية
client = getattr(__main__, 'client', None)
MEM_FILE = "mem.json"
PENDING_FILE = "pending_memes.json" # لتخزين الطلبات المؤقتة
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
# 1. منيو الميمز (.م13)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م13$"))
async def menu_13(event):
    msg = (
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑴𝑬𝑴𝑬𝑺 • ☭\n"
        "★────────☭────────★\n\n"
        "• `.ميمز` ⌯ لعرض كافة الأصوات المتاحة\n"
        "• `.م [الاسم]` ⌯ لتشغيل بصمة محددة\n"
        "• `.اضيف بصمتي` [الاسم] ⌯ لطلب إضافة بصمتك (بالرد)\n"
        "• `.اضافة ميمز` [الرابط] [الاسم] ⌯ (للمطورين)\n"
        "• `.حذف ميمز` [الاسم] ⌯ (للمطورين)\n\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )
    await event.edit(msg)

# ==========================================
# 2. نظام طلب إضافة بصمة (للمستخدمين)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضيف بصمتي\s+(.*)$"))
async def request_meme(event):
    if not event.is_reply:
        return await event.edit("⚠️ **يجب الرد على البصمة التي تريد إضافتها!**")
    
    name = event.pattern_match.group(1).strip()
    reply_msg = await event.get_reply_message()
    
    if not reply_msg.voice:
        return await event.edit("⚠️ **يرجى الرد على بصمة صوتية فقط!**")

    await event.edit("🚀 **جاري إرسال طلبك للمطورين للمراجعة...**")
    
    # حفظ الطلب مؤقتاً (نستخدم آيدي الرسالة كمرجع)
    pending = get_db(PENDING_FILE)
    # نحتاج رابط البصمة، إذا كانت في قناة عامة أو سنقوم بإعادة توجيهها للمطور
    # للسهولة: سنرسل رسالة للمطور يوافق عليها
    
    for sudo in SUDO_IDS:
        try:
            forward = await reply_msg.forward_to(sudo)
            await client.send_message(sudo, 
                f"📥 **طلب إضافة ميمز جديد**\n"
                f"• الاسم المقترح: `{name}`\n"
                f"• من المستخدم: `{event.sender_id}`\n"
                f"• للقبول رد بـ: `موافقة {name}`\n"
                f"• للرفض رد بـ: `رفض`",
                reply_to=forward.id
            )
        except: continue
    
    await event.edit("✅ **تم إرسال طلبك بنجاح! انتظر رد المطورين.**")

# ==========================================
# 3. قبول أو رفض الطلب (للمطورين فقط)
# ==========================================
@client.on(events.NewMessage(incoming=True))
async def handle_approval(event):
    if event.sender_id not in SUDO_IDS or not event.is_reply: return
    
    text = event.text
    reply_msg = await event.get_reply_message()

    if text.startswith("موافقة"):
        try:
            name = text.replace("موافقة", "").strip()
            # استخراج الرابط (إذا كانت الرسالة بصمة)
            if reply_msg.voice:
                # هنا نفترض أن المطور يرفعها لقناة السورس أو نستخدم الميديا مباشرة
                # للتبسيط سنقوم بجلب رابط الرسالة إذا كانت في قناة
                # أو يفضل للمطور استخدام .اضافة ميمز يدوياً
                await event.reply(f"✅ تم القبول. يرجى استخدام `.اضافة ميمز [الرابط] {name}` لإتمام العملية.")
        except: pass

    elif text == "رفض":
        await event.reply("❌ تم رفض الطلب وإبلاغ المستخدم (اختيارياً).")

# ==========================================
# 4. أوامر المطورين (إضافة وحذف)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة ميمز\s+(https?://t\.me/\S+)\s+(.*)$"))
async def add_meme(event):
    if event.sender_id not in SUDO_IDS:
        return await event.edit("⚠️ **الأمر مخصص للمطورين فقط!**")
    
    link, name = event.pattern_match.group(1), event.pattern_match.group(2).strip()
    db = get_db(MEM_FILE)
    if name in db: return await event.edit("⚠️ الاسم موجود مسبقاً.")
    
    db[name] = link
    save_db(MEM_FILE, db)
    await event.edit(f"✅ **تمت إضافة ({name}) للسجل الملكي.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حذف ميمز\s+(.*)$"))
async def delete_meme(event):
    if event.sender_id not in SUDO_IDS: return
    name = event.pattern_match.group(1).strip()
    db = get_db(MEM_FILE)
    if name in db:
        del db[name]
        save_db(MEM_FILE, db)
        await event.edit(f"🗑️ **تم حذف ({name}) من السجلات.**")
    else: await event.edit("🔍 لم أجد هذا الاسم.")

# ==========================================
# 5. عرض وتشغيل الميمز (للجميع)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ميمز$"))
async def list_memes(event):
    db = get_db(MEM_FILE)
    if not db: return await event.edit("⚠️ القائمة فارغة.")
    res = "★────────☭────────★\n   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑴𝑬𝑴𝑬𝑺 • ☭\n★────────☭────────★\n\n"
    for i, name in enumerate(db.keys(), 1): res += f"{i}- `{name}`\n"
    res += "\n• للاستدعاء: `.م [الاسم]`"
    await event.edit(res)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م\s+(.*)$"))
async def play_meme(event):
    query = event.pattern_match.group(1).strip()
    db = get_db(MEM_FILE)
    found_key = next((k for k in db if query.lower() in k.lower()), None)
    if found_key:
        for f in VORTEX:
            await event.edit(f"⌯ {f} جاري سحب البصمة {f} ⌯")
            await asyncio.sleep(0.05)
        await client.send_file(event.chat_id, db[found_key], voice_note=True, reply_to=event.reply_to_msg_id)
        await event.delete()
