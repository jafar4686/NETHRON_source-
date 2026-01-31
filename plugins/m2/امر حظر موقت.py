import __main__, os, asyncio, json, re
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

# دالة جلب المسارات
def get_paths(chat_id):
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return gp, os.path.join(gp, "ban.json"), os.path.join(gp, "owner.json")
    return None, None, None

# ==========================================
# أمر موقت حظر (عد تنازلي ينتهي بالطرد والحظر)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.موقت حظر\s+(.*)$"))
async def timed_execution(event):
    if not event.is_group: return
    
    gp_path, ban_file, owner_file = get_paths(event.chat_id)
    if not owner_file: return
    
    # التحقق من المالك
    with open(owner_file, "r", encoding="utf-8") as f:
        if json.load(f).get("id") != event.sender_id: return

    args = event.pattern_match.group(1).split()
    if not args: return await event.edit("⚠️ **مثال: .موقت حظر 1m**")

    seconds = parse_time(args[0])
    if not seconds: return await event.edit("⚠️ **وقت غير صالح! استخدم (s, m, h, d)**")

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

    if user_id == event.sender_id: return await event.edit("⚠️ **لا يمكن نفي الملك!**")

    try:
        user_entity = await client.get_entity(user_id)
        name = user_entity.first_name or "المستخدم"

        # 1. حلقة العد التنازلي قبل التنفيذ
        while seconds > 0:
            step = 10 if seconds > 60 else 2 # تسريع التحديث بالثواني الأخيرة
            if step > seconds: step = seconds

            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            time_left = f"{int(h)}h {int(m)}m {int(s)}s" if h > 0 else f"{int(m)}m {int(s)}s" if m > 0 else f"{int(s)}s"
            
            await event.edit(
                "★────────☭────────★\n"
                "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
                "★────────☭────────★\n\n"
                f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
                f"• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **صدر قرار النفي الوشيك** ⏳\n"
                f"• 𝑻𝒊𝒎𝒆 𝑳𝒆𝒇𝒕 ⌯ `{time_left}`\n\n"
                "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
            )
            await asyncio.sleep(step)
            seconds -= step

        # 2. مرحلة التنفيذ (الحظر الفعلي)
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري التنفيذ ونفي {name} نهائياً 〕 {f} ⌯")
            await asyncio.sleep(0.1)

        # تنفيذ الحظر في تليجرام
        await client(functions.channels.EditBannedRequest(
            event.chat_id, user_id, 
            types.ChatBannedRights(until_date=None, view_messages=True)
        ))
        
        # تدوينه في ملف المحظورين لضمان عدم رجوعه
        ban_list = []
        if os.path.exists(ban_file):
            with open(ban_file, "r", encoding="utf-8") as f: ban_list = json.load(f)
        if user_id not in ban_list:
            ban_list.append(user_id)
            with open(ban_file, "w", encoding="utf-8") as f: json.dump(ban_list, f)
        
        await event.edit(f"• ⌯ **انتهى الوقت.. تم نفي {name} من المملكة بنجاح!** 🚫")

    except Exception as e:
        await event.edit(f"⚠️ **خطأ في التنفيذ:** `{str(e)}`")
