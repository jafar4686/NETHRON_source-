import __main__, os, asyncio, json, re, time
from telethon import events, functions, types

# استخراج الكلاينت والمسارات
client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# دالة تحويل الوقت
def parse_time(time_str):
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    match = re.match(r"(\d+)([smhd])", time_str.lower())
    if match:
        val, unit = match.groups()
        return int(val) * units[unit]
    return None

# دالة التأكد من المالك
def get_owner_only(chat_id):
    if not os.path.exists(BASE_DIR): return None
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            owner_path = os.path.join(BASE_DIR, folder, "owner.json")
            if os.path.exists(owner_path):
                with open(owner_path, "r", encoding="utf-8") as f:
                    return json.load(f).get("id")
    return None

# ==========================================
# أمر موقت طرد (تحديث كل 10 ثواني + طرد)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.موقت طرد\s+(.*)$"))
async def timed_kick(event):
    if not event.is_group: return
    owner_id = get_owner_only(event.chat_id)
    if not owner_id or event.sender_id != owner_id: return

    args = event.pattern_match.group(1).split()
    if not args:
        return await event.edit("⚠️ **مثال: .موقت طرد 1m**")

    seconds = parse_time(args[0])
    if not seconds or seconds < 60:
        return await event.edit("⚠️ **أقل مدة للطرد هي دقيقة واحدة (1m)!**")

    user_id = None
    if event.is_reply:
        reply = await event.get_reply_message()
        user_id = reply.sender_id
    elif len(args) > 1:
        try:
            u = await client.get_entity(args[1])
            user_id = u.id
        except: return await event.edit("⚠️ **المستخدم غير موجود!**")
    else:
        return await event.edit("⚠️ **رد على الشخص أو أرسل يوزره!**")

    if user_id == event.sender_id: return await event.edit("⚠️ **لا يمكن طرد الملك!**")

    try:
        target = await client.get_entity(user_id)
        name = target.first_name or "المستخدم"
        
        # 1. حلقة العد التنازلي (تحديث ثابت كل 10 ثواني)
        while seconds > 0:
            # التحديث ثابت كل 10 ثواني مثل ما ردت
            step = 10 
            if step > seconds: step = seconds
            
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            t_left = f"{int(h)}h {int(m)}m {int(s)}s" if h > 0 else f"{int(m)}m {int(s)}s" if m > 0 else f"{int(s)}s"
            
            await event.edit(
                "★────────☭────────★\n"
                "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
                "★────────☭────────★\n\n"
                f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
                f"• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **قرار استبعاد مؤجل** ⏳\n"
                f"• 𝑻𝒊𝒎𝒆 𝑳𝒆𝒇𝒕 ⌯ `{t_left}`\n\n"
                "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
            )
            await asyncio.sleep(step)
            seconds -= step

        # 2. حركات الدوامة قبل الطرد النهائي
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري تنفيذ أمر الطرد لـ {name} 〕 {f} ⌯")
            await asyncio.sleep(0.1)

        # 3. تنفيذ الطرد (Kick)
        await client.kick_participant(event.chat_id, user_id)
        
        await event.edit(f"• ⌯ **انتهى الوقت.. تم طرد {name} من المملكة بنجاح!** ✅")

    except Exception as e:
        await event.edit(f"⚠️ **حدث خطأ:** `{str(e)}`")
