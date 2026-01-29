import __main__, asyncio
from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError

client = getattr(__main__, 'client', None)

# متغيرات النظام
PRIVATE_LOCKED = False
MUTED_USERS = []
CH_ID = None  # يوزر القناة للاشتراك الإجباري
VORTEX = ["◜", "◝", "◞", "◟"]

# --- 1. أوامر سد وفتح الخاص (تعديل فوري) ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(سد|فتح) خاص$"))
async def private_control(event):
    global PRIVATE_LOCKED
    cmd = event.pattern_match.group(1)
    if cmd == "سد":
        PRIVATE_LOCKED = True
        await event.edit("🔒 **تم قفل الخاص بنجاح.**")
    else:
        PRIVATE_LOCKED = False
        await event.edit("🔓 **تم فتح الخاص بنجاح.**")

# --- 2. أمر إضافة قناة الاشتراك الإجباري ---
# تكتب: .اضافة قناة @يوزر_القناة
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة قناة (.*)"))
async def set_channel(event):
    global CH_ID
    ch_user = event.pattern_match.group(1).replace("@", "")
    CH_ID = ch_user
    await event.edit(f"✅ **تم تحديد القناة [@{ch_user}] للاشتراك الإجباري.**")

# --- 3. أوامر الكتم والسماح (خاص فقط + لا للمحفوظات) ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(كتم|سماح)$"))
async def mute_control(event):
    if not event.is_private:
        return await event.edit("**⚠️ هذا الأمر يستخدم في الخاص حصراً!**")
    if event.chat_id == (await client.get_me()).id:
        return await event.edit("**⚠️ لا يمكنك استخدام هذا الأمر في المحفوظات!**")
    if not event.is_reply:
        return await event.edit("**⚠️ يجب الرد على الشخص أولاً!**")
    
    reply_msg = await event.get_reply_message()
    user_id = reply_msg.sender_id
    cmd = event.pattern_match.group(1)
    
    action_text = "كتم" if cmd == "كتم" else "سماح"
    for i in range(4):
        f = VORTEX[i % 4]
        await event.edit(f"{f} ⌯〔جاري {action_text} الشخص〕⌯ {f}")
        await asyncio.sleep(0.1)
    
    if cmd == "كتم":
        if user_id not in MUTED_USERS: MUTED_USERS.append(user_id)
        await event.edit("⌯〔تم كتم الشخص〕⌯")
    else:
        if user_id in MUTED_USERS: MUTED_USERS.remove(user_id)
        await event.edit("⌯〔تم سماح الشخص〕⌯")

# --- 4. المحرك الأساسي (حذف المكتومين + السد + الاشتراك الإجباري) ---
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def private_checker(event):
    global PRIVATE_LOCKED, CH_ID
    user_id = event.sender_id
    
    # أولاً: التحقق من المكتومين
    if user_id in MUTED_USERS:
        return await event.delete()

    # ثانياً: التحقق من قفل الخاص
    if PRIVATE_LOCKED:
        await event.reply("**صاحب الحساب غير موجود حالياً، الخاص مغلق.**")
        return await event.delete()

    # ثالثاً: التحقق من الاشتراك الإجباري
    if CH_ID:
        try:
            await client(GetParticipantRequest(channel=CH_ID, user_id=user_id))
        except UserNotParticipantError:
            await event.reply(f"⚠️ **عذراً عزيزي، يجب عليك الاشتراك بقناة السورس أولاً لتتمكن من مراسلتي:**\n\n👉 @{CH_ID}")
            return await event.delete()
        except Exception:
            pass # في حال كانت القناة خاصة أو اليوزر غلط
