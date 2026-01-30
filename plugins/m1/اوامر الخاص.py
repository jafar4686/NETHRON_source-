import __main__, asyncio
from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError

client = getattr(__main__, 'client', None)

# متغيرات النظام
PRIVATE_LOCKED = False
MUTED_USERS = []
CH_LINK = None       
CH_USERNAME = None   
VORTEX = ["◜", "◝", "◞", "◟"]

# --- 1. أوامر سد وفتح الخاص ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(سد|فتح) خاص$"))
async def private_lock_control(event):
    global PRIVATE_LOCKED
    cmd = event.pattern_match.group(1)
    PRIVATE_LOCKED = (cmd == "سد")
    await event.edit(f"🔒 **تم {cmd} الخاص بنجاح.**")

# --- 2. أمر إضافة قناة الاشتراك الإجباري ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة قناة اجباري (.*)"))
async def set_force_channel(event):
    global CH_LINK, CH_USERNAME
    link = event.pattern_match.group(1).strip()
    CH_LINK = link
    CH_USERNAME = link.split('/')[-1].replace("@", "")
    await event.edit(f"✅ **تم تفعيل الاشتراك الإجباري:**\n🔗 {link}")

# --- 3. أوامر الكتم والسماح ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(كتم|سماح)$"))
async def mute_system(event):
    if not event.is_private or event.chat_id == (await client.get_me()).id:
        return 
    if not event.is_reply:
        return await event.edit("**⚠️ رد على الشخص أولاً!**")
    
    user_id = (await event.get_reply_message()).sender_id
    cmd = event.pattern_match.group(1)
    
    action_text = "كتم" if cmd == "كتم" else "سماح"
    for f in VORTEX:
        await event.edit(f"{f} ⌯〔جاري {action_text} الشخص〕⌯ {f}")
        await asyncio.sleep(0.1)
    
    if cmd == "كتم":
        if user_id not in MUTED_USERS: MUTED_USERS.append(user_id)
        await event.edit("⌯〔تم كتم الشخص بنجاح〕⌯")
    else:
        if user_id in MUTED_USERS: MUTED_USERS.remove(user_id)
        await event.edit("⌯〔تم سماح الشخص بنجاح〕⌯")

# --- 4. المحرك الأساسي ---
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def private_engine(event):
    global PRIVATE_LOCKED, CH_USERNAME, CH_LINK
    user_id = event.sender_id
    
    if user_id in MUTED_USERS:
        return await event.delete()

    if PRIVATE_LOCKED:
        await event.reply("**عذراً، الخاص مغلق حالياً.**")
        return await event.delete()

    if CH_USERNAME:
        try:
            await client(GetParticipantRequest(channel=CH_USERNAME, user_id=user_id))
        except UserNotParticipantError:
            await event.reply(f"⚠️ **يجب عليك الاشتراك بقناتي أولاً لتتمكن من مراسلتي:**\n\n🔗 {CH_LINK}")
            return await event.delete()
        except Exception:
            pass
