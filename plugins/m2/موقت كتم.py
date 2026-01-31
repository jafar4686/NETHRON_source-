import __main__, os, asyncio, json, re
from telethon import events, functions, types

# استخراج الكلاينت
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
            return os.path.join(gp, "mute.json"), os.path.join(gp, "owner.json")
    return None, None

# ==========================================
# 14. أمر موقت كتم (تحديث ذكي + فك تلقائي)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.موقت كتم\s+(.*)$"))
async def timed_mute(event):
    if not event.is_group: return
    
    mute_file, owner_file = get_paths(event.chat_id)
    if not owner_file: return
    
    with open(owner_file, "r", encoding="utf-8") as f:
        if json.load(f).get("id") != event.sender_id: return

    args = event.pattern_match.group(1).split()
    if not args: return await event.edit("⚠️ **مثال: .موقت كتم 10m**")

    time_val = args[0]
    seconds = parse_time(time_val)
    
    if not seconds or seconds < 60:
        return await event.edit("⚠️ **أقل مدة للكتم هي دقيقة واحدة (1m)!**")

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

    try:
        # 1. إضافة الشخص لملف المكتومين (JSON)
        mute_list = []
        if os.path.exists(mute_file):
            with open(mute_file, "r", encoding="utf-8") as f: mute_list = json.load(f)
        if user_id not in mute_list:
            mute_list.append(user_id)
            with open(mute_file, "w", encoding="utf-8") as f: json.dump(mute_list, f)

        user_entity = await client.get_entity(user_id)
        name = user_entity.first_name or "المستخدم"

        # 2. حلقة العد التنازلي (تحديث كل 30 ثانية أو 10 ثواني)
        while seconds > 0:
            if seconds > 300: step = 30
            else: step = 10
            if step > seconds: step = seconds

            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            time_left = f"{int(h)}h {int(m)}m {int(s)}s" if h > 0 else f"{int(m)}m {int(s)}s" if m > 0 else f"{int(s)}s"
            
            await event.edit(
                "★────────☭────────★\n"
                "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
                "★────────☭────────★\n\n"
                f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
                f"• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **مكتوم مؤقتاً في المملكة** 🤫\n"
                f"• 𝑻𝒊𝒎𝒆 𝑳𝒆𝒇𝒕 ⌯ `{time_left}`\n\n"
                "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
            )
            await asyncio.sleep(step)
            seconds -= step

        # 3. مرحلة انتهاء الوقت وفك الكتم مع التحميل
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري إصدار عفو ملكي عن {name} 〕 {f} ⌯")
            await asyncio.sleep(0.2)

        # مسحه من الملف نهائياً ليرجع يحجي
        if os.path.exists(mute_file):
            with open(mute_file, "r", encoding="utf-8") as f: mute_list = json.load(f)
            if user_id in mute_list:
                mute_list.remove(user_id)
                with open(mute_file, "w", encoding="utf-8") as f: json.dump(mute_list, f)
        
        await event.edit(f"• ⌯ **انتهى الوقت.. تم فك كتم {name} ويمكنه التحدث الآن!** ✅")

    except Exception as e:
        await event.edit(f"⚠️ **خطأ:** `{str(e)}`")

# محرك الحذف (المسؤول عن مسح رسائل المكتومين)
@client.on(events.NewMessage(incoming=True))
async def mute_watcher(event):
    if not event.is_group: return
    mute_file, _ = get_paths(event.chat_id)
    if mute_file and os.path.exists(mute_file):
        with open(mute_file, "r", encoding="utf-8") as f:
            if event.sender_id in json.load(f):
                await event.delete()
