import __main__, os, asyncio, json, re
from telethon import events, functions, types

# استخراج الكلاينت والمسارات
client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# 1. موازين القوة (الهرمية الأساسية)
RANK_POWER = {
    "عضو": 0, "مميز": 1, "ادمن": 2, "مدير": 3, "مطور": 4, "owner": 5
}

# دالة تحويل الوقت
def parse_time(time_str):
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    match = re.match(r"(\d+)([smhd])", time_str.lower())
    if match:
        val, unit = match.groups()
        return int(val) * units[unit]
    return None

# دالة جلب المسارات الموحدة
def get_all_paths(chat_id):
    if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return {
                "owner": os.path.join(gp, "owner.json"),
                "ranks": os.path.join(gp, "member_rank.json"),
                "perms": os.path.join(gp, "permissions.json"),
                "mute": os.path.join(gp, "mute.json")
            }
    return None

# --- العقل المدبر: فحص الهرمية للكتم ---
async def check_mute_hierarchy(event, paths, target_id):
    sender_id = event.sender_id
    
    # تحديد رتبة المنفذ
    s_rank = "عضو"
    if os.path.exists(paths["owner"]):
        with open(paths["owner"], "r") as f:
            if json.load(f).get("id") == sender_id: s_rank = "owner"
    if s_rank != "owner" and os.path.exists(paths["ranks"]):
        with open(paths["ranks"], "r") as f:
            ranks = json.load(f)
            s_rank = ranks.get(str(sender_id), {}).get("rank", "عضو")

    # 1. فحص الصلاحية من ملف permissions.json
    if s_rank != "owner":
        if os.path.exists(paths["perms"]):
            with open(paths["perms"], "r") as f:
                perms = json.load(f)
                if not perms.get(s_rank, {}).get("كتم", False):
                    await event.edit(f"⚠️ **رتبتك ({s_rank}) لا تملك صلاحية الكتم!**")
                    return False
        else: return False

    # 2. فحص الهرمية للهدف
    t_rank = "عضو"
    if os.path.exists(paths["owner"]):
        with open(paths["owner"], "r") as f:
            if json.load(f).get("id") == target_id: t_rank = "owner"
    if t_rank != "owner" and os.path.exists(paths["ranks"]):
        with open(paths["ranks"], "r") as f:
            ranks = json.load(f)
            t_rank = ranks.get(str(target_id), {}).get("rank", "عضو")

    if RANK_POWER[s_rank] <= RANK_POWER[t_rank] and s_rank != "owner":
        msg = await event.edit(f"⚠️ **لا يمكنك كتم رتبة أعلى منك أو مساوية لك ({t_rank})!**")
        await asyncio.sleep(10)
        await msg.delete()
        return False
    return True

# ==========================================
# أمر موقت كتم الهرمي (.موقت كتم)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.موقت كتم\s+(.*)$"))
async def timed_mute(event):
    if not event.is_group: return
    
    paths = get_all_paths(event.chat_id)
    if not paths: return await event.edit("⚠️ **المجموعة غير مفعلة!**")

    args = event.pattern_match.group(1).split()
    if not args: return await event.edit("⚠️ **مثال: .موقت كتم 10m**")

    seconds = parse_time(args[0])
    if not seconds or seconds < 60:
        return await event.edit("⚠️ **أقل مدة للكتم هي دقيقة واحدة (1m)!**")

    # تحديد الهدف
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

    # فحص الهرمية
    if not await check_mute_hierarchy(event, paths, user_id):
        return

    try:
        # 1. إضافة الشخص لملف المكتومين (ليدخل حيز محرك الحذف)
        mute_list = []
        if os.path.exists(paths["mute"]):
            with open(paths["mute"], "r", encoding="utf-8") as f: mute_list = json.load(f)
        
        if str(user_id) not in [str(i) for i in mute_list]:
            mute_list.append(str(user_id))
            with open(paths["mute"], "w", encoding="utf-8") as f: json.dump(mute_list, f, indent=4)

        user_entity = await client.get_entity(user_id)
        name = user_entity.first_name or "المستخدم"

        # 2. حلقة العد التنازلي وتحديث الرسالة
        while seconds > 0:
            step = 30 if seconds > 300 else 10 # سرعة التحديث
            if step > seconds: step = seconds

            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            t_left = f"{int(h)}h {int(m)}m {int(s)}s" if h > 0 else f"{int(m)}m {int(s)}s" if m > 0 else f"{int(s)}s"
            
            await event.edit(
                "★────────☭────────★\n"
                "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑴𝑼𝑻𝑬𝑹 • ☭\n"
                "★────────☭────────★\n\n"
                f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
                f"• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **قرار خرخرة مؤقت (هرمي)** 🤫\n"
                f"• 𝑻𝒊𝒎𝒆 𝑳𝒆𝒇𝒕 ⌯ `{t_left}`\n\n"
                "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
            )
            await asyncio.sleep(step)
            seconds -= step

        # 3. العفو الملكي بعد انتهاء الوقت
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري إصدار عفو ملكي وفك الخرخرة 〕 {f} ⌯")
            await asyncio.sleep(0.2)

        # حذف من ملف المكتومين
        if os.path.exists(paths["mute"]):
            with open(paths["mute"], "r", encoding="utf-8") as f: mute_list = json.load(f)
            if str(user_id) in [str(i) for i in mute_list]:
                mute_list.remove(str(user_id))
                with open(paths["mute"], "w", encoding="utf-8") as f: json.dump(mute_list, f, indent=4)
        
        await event.edit(f"• ⌯ **انتهى الوقت.. تم فك كتم {name} بنجاح!** ✅")

    except Exception as e:
        await event.edit(f"⚠️ **خطأ في التنفيذ:** `{str(e)}`")
