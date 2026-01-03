import __main__
from telethon import events, functions, types
import asyncio

# الوصول للكلاينت المعرف في الملف الرئيسي
client = __main__.client

# مخازن البيانات للنشر التلقائي
AUTO_POST = {"active": False, "text": "", "interval": 600, "chats": []}

# ==========================================
# 1. قائمة الأوامر م3 (فخامة نيثرون)
# ==========================================
@client.on(events.NewMessage(pattern=r"^\.م3$"))
async def help_m3(event):
    if not event.out: return
    help_text = (
        "★────────☭────────★\n"
        "   ☭ • 𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 • ☭\n"
        "                  ☭ • سورس نيثرون • ☭\n"
        "★────────☭────────★\n\n"
        "📢 **أوامر الإذاعة والنشر:**\n\n"
        "• `.اذاعة` (بالرد) \n"
        "➥ إرسال الرسالة لكل الخاص والكروبات\n\n"
        "• `.اذاعة خاص` \n"
        "➥ إرسال الرسالة لجميع المحادثات الخاصة\n\n"
        "• `.اذاعة كروبات` \n"
        "➥ إرسال الرسالة لجميع المجموعات\n\n"
        "• `.توجيه` (بالرد) \n"
        "➥ توجيه الرسالة لكل الشاتات (بدون اسم)\n\n"
        "• `.تكرار` (العدد) (النص) \n"
        "➥ تكرار إرسال النص بعدد المرات المطلوب\n\n"
        "• `.نشر` (بالرد) | `.ايقاف النشر` \n"
        "➥ تفعيل النشر التلقائي كل 10 دقائق\n\n"
        "★────────☭────────★\n"
        "💬 **ملاحظة:** استخدم الإذاعة بحكمة لتجنب الحظر."
    )
    await event.edit(help_text)

# ==========================================
# 2. محرك الإذاعة والنشر
# ==========================================

# --- [1] الإذاعة الشاملة ---
@client.on(events.NewMessage(pattern=r"^\.اذاعة$"))
async def broadcast_all(event):
    if not event.out: return
    reply = await event.get_reply_message()
    if not reply: return await event.edit("⚠️ **رد على رسالة للإذاعة!**")
    
    await event.edit("🚀 **جاري بدء الإذاعة الشاملة...**")
    count = 0
    async for dialog in client.iter_dialogs():
        try:
            await client.send_message(dialog.id, reply)
            count += 1
            await asyncio.sleep(0.3) # تأخير لتجنب الحظر
        except: continue
    await event.edit(f"✅ **تمت الإذاعة لـ {count} محادثة.**")

# --- [2] إذاعة الخاص ---
@client.on(events.NewMessage(pattern=r"^\.اذاعة خاص$"))
async def broadcast_private(event):
    if not event.out: return
    reply = await event.get_reply_message()
    if not reply: return await event.edit("⚠️ **رد على رسالة!**")
    
    await event.edit("👤 **جاري الإذاعة للخاص...**")
    count = 0
    async for dialog in client.iter_dialogs():
        if dialog.is_user and not dialog.entity.bot:
            try:
                await client.send_message(dialog.id, reply)
                count += 1
                await asyncio.sleep(0.3)
            except: continue
    await event.edit(f"✅ **تمت الإذاعة لـ {count} مستخدم.**")

# --- [3] إذاعة الكروبات ---
@client.on(events.NewMessage(pattern=r"^\.اذاعة كروبات$"))
async def broadcast_groups(event):
    if not event.out: return
    reply = await event.get_reply_message()
    if not reply: return await event.edit("⚠️ **رد على رسالة!**")
    
    await event.edit("👥 **جاري الإذاعة للمجموعات...**")
    count = 0
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            try:
                await client.send_message(dialog.id, reply)
                count += 1
                await asyncio.sleep(0.3)
            except: continue
    await event.edit(f"✅ **تمت الإذاعة لـ {count} مجموعة.**")

# --- [4] التكرار (سبام) ---
@client.on(events.NewMessage(pattern=r"^\.تكرار (\d+) (.*)$"))
async def spammer(event):
    if not event.out: return
    times = int(event.pattern_match.group(1))
    text = event.pattern_match.group(2)
    await event.delete()
    for _ in range(times):
        await client.send_message(event.chat_id, text)
        await asyncio.sleep(0.2)

# --- [5] النشر التلقائي ---
@client.on(events.NewMessage(pattern=r"^\.نشر$"))
async def start_auto_post(event):
    if not event.out: return
    reply = await event.get_reply_message()
    if not reply: return await event.edit("⚠️ **رد على الرسالة التي تريد نشرها تلقائياً.**")
    
    AUTO_POST["active"] = True
    AUTO_POST["text"] = reply
    await event.edit("🔄 **تم تفعيل النشر التلقائي (كل 10 دقائق).**")
    
    while AUTO_POST["active"]:
        count = 0
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                try:
                    await client.send_message(dialog.id, AUTO_POST["text"])
                    count += 1
                    await asyncio.sleep(0.5)
                except: continue
        await asyncio.sleep(600) # انتظر 10 دقائق

@client.on(events.NewMessage(pattern=r"^\.ايقاف النشر$"))
async def stop_auto_post(event):
    if not event.out: return
    AUTO_POST["active"] = False
    await event.edit("🛑 **تم إيقاف النشر التلقائي.**")