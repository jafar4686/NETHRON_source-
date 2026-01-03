import __main__
from telethon import events, functions, types
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.account import UpdateProfileRequest
import asyncio

# الوصول للكلاينت المعرف في الملف الرئيسي
client = __main__.client

# مخازن البيانات والتحكم
DARK_CONFIG = {"radar_active": False, "target_id": None}
GHOST_BACKUP = {"name": "", "bio": "", "has_data": False}
ANNOY_CHATS = set()

# ==========================================
# 1. قائمة الأوامر م2 المنسقة (بنفس ستايل م1)
# ==========================================
@client.on(events.NewMessage(pattern=r"^\.م2$"))
async def m2_command(event):
    if not event.out: return
    m2_text = (
        "★────────☭────────★\n"
        "   ☭ • 𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 • ☭\n"
        "                  ☭ • سورس نيثرون • ☭\n"
        "★────────☭────────★\n\n"
        "🧨 **أوامر النرفزة والتمويه:**\n\n"
        "• `.نرفزة` | `.ايقاف نرفزة` \n"
        "➥ قراءة فورية ومستمرة لكل رسائل الخصم\n\n"
        "• `.رادار` | `.ايقاف رادار` \n"
        "➥ تنبيهك فور دخول الشخص للمحادثة\n\n"
        "• `.قنبلة` (النص) \n"
        "➥ إرسال رسالة تدمير ذاتي بعد رؤيتها\n\n"
        "• `.تحميل وهمي` | `.كلام وهمي` \n"
        "➥ إيهام الخصم بحالات رفع ملفات أو كتابة\n\n"
        "• `.بصمة وهمية` | `.فيديو وهمي` \n"
        "➥ إظهار جاري تسجيل صوت أو فيديو\n\n"
        "• `.تاغ مخفي` (بالرد) | `.مقلب` \n"
        "➥ إرسال إشعار صامت أو انتحال سريع\n\n"
        "• `.تمويه` | `.رجوع` \n"
        "➥ قلب الحساب لمحذوف أو العودة للأصل\n\n"
        "★────────☭────────★\n"
        "💬 **ملاحظة:** لعرض الأوامر العامة أرسل `.الاوامر`"
    )
    await event.edit(m2_text)

# ==========================================
# 2. محرك الأوامر الوهمية (المصلح)
# ==========================================

# أمر تحميل وهمي
@client.on(events.NewMessage(pattern=r"^\.تحميل وهمي$"))
async def fake_doc(event):
    if not event.out: return
    await event.delete()
    async with client.action(event.chat_id, 'document'):
        await asyncio.sleep(100)

# أمر كلام وهمي
@client.on(events.NewMessage(pattern=r"^\.كلام وهمي$"))
async def fake_typing(event):
    if not event.out: return
    await event.delete()
    async with client.action(event.chat_id, 'typing'):
        await asyncio.sleep(100)

# أمر بصمة وهمية
@client.on(events.NewMessage(pattern=r"^\.بصمة وهمية$"))
async def fake_audio(event):
    if not event.out: return
    await event.delete()
    async with client.action(event.chat_id, 'record-audio'):
        await asyncio.sleep(100)

# أمر فيديو وهمي
@client.on(events.NewMessage(pattern=r"^\.فيديو وهمي$"))
async def fake_video(event):
    if not event.out: return
    await event.delete()
    async with client.action(event.chat_id, 'record-video'): # تم تصحيح النوع هنا
        await asyncio.sleep(100)

# ==========================================
# 3. بقية أوامر النرفزة والخباثة
# ==========================================

@client.on(events.NewMessage(pattern=r"^\.نرفزة$"))
async def annoy_on(event):
    if not event.out: return
    ANNOY_CHATS.add(event.chat_id)
    await event.edit("🧨 **تم تفعيل النرفزة..**")

@client.on(events.NewMessage(pattern=r"^\.ايقاف نرفزة$"))
async def annoy_off(event):
    if not event.out: return
    ANNOY_CHATS.discard(event.chat_id)
    await event.edit("✅ **تم إيقاف النرفزة.**")

@client.on(events.NewMessage(incoming=True))
async def auto_read_handler(event):
    if event.chat_id in ANNOY_CHATS:
        await event.mark_read()

@client.on(events.NewMessage(pattern=r"^\.رادار$"))
async def radar_on(event):
    if not event.out: return
    DARK_CONFIG.update({"target_id": event.chat_id, "radar_active": True})
    await event.edit("📡 **تم تفعيل الرادار..**")

@client.on(events.NewMessage(pattern=r"^\.ايقاف رادار$"))
async def radar_off(event):
    if not event.out: return
    DARK_CONFIG["radar_active"] = False
    await event.edit("✅ **تم إيقاف الرادار.**")

@client.on(events.Raw(types.UpdateReadHistoryOutbox))
async def watch_read(e):
    if DARK_CONFIG["radar_active"] and isinstance(e.peer, types.PeerUser):
        if e.peer.user_id == DARK_CONFIG["target_id"]:
            await client.send_message("me", "🚨 **رادار نيثرون:** الخصم دخل المحادثة!")

@client.on(events.NewMessage(pattern=r"^\.قنبلة (.*)$"))
async def bomb_msg(event):
    if not event.out: return
    text = event.pattern_match.group(1)
    msg = await event.edit(text)
    while True:
        await asyncio.sleep(0.5)
        try:
            m = await client.get_messages(event.chat_id, ids=msg.id)
            if m and m.read_date:
                await msg.delete(revoke=True); break
        except: break

@client.on(events.NewMessage(pattern=r"^\.تاغ مخفي$"))
async def hidden_tag(event):
    if not event.out: return
    reply = await event.get_reply_message()
    if reply: await event.edit(f"[\u2063](tg://user?id={reply.sender_id}).")

@client.on(events.NewMessage(pattern=r"^\.مقلب$"))
async def fast_clone(event):
    if not event.out: return
    reply = await event.get_reply_message()
    if not reply: return
    user = await client.get_entity(reply.sender_id)
    me = await client.get_me()
    oname = me.first_name
    await client(UpdateProfileRequest(first_name=user.first_name))
    await event.edit(f"🎭 **انتحال مؤقت لـ {user.first_name}...**")
    await asyncio.sleep(10)
    await client(UpdateProfileRequest(first_name=oname))
    await event.edit("✅ **انتهى المقلب.**")

@client.on(events.NewMessage(pattern=r"^\.تمويه$"))
async def ghost_start(event):
    global GHOST_BACKUP
    if not event.out: return
    if not GHOST_BACKUP["has_data"]:
        me = await client.get_me(); full = await client(GetFullUserRequest('me'))
        GHOST_BACKUP.update({"name": me.first_name, "bio": full.full_user.about or "", "has_data": True})
    await client(UpdateProfileRequest(first_name="Deleted Account", about=""))
    await event.edit("🥷 **تم التمويه!**")

@client.on(events.NewMessage(pattern=r"^\.رجوع$"))
async def ghost_back(event):
    if not event.out: return
    if not GHOST_BACKUP["has_data"]: return
    await client(UpdateProfileRequest(first_name=GHOST_BACKUP["name"], about=GHOST_BACKUP["bio"]))
    await event.edit("✅ **تمت الاستعادة.**")
