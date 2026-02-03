import __main__, os, asyncio, json, re
from telethon import events, functions, types

# استخراج الكلاينت والمسارات
client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# 1. موازين القوة (الهرمية)
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

# دالة جلب المسارات
def get_paths(chat_id):
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return {
                "gp": gp,
                "ban": os.path.join(gp, "ban.json"),
                "owner": os.path.join(gp, "owner.json"),
                "ranks": os.path.join(gp, "member_rank.json"),
                "perms": os.path.join(gp, "permissions.json")
            }
    return None

# --- دالة فحص الهرمية والصلاحية (نفس سيستم الحظر والكتم) ---
async def check_hierarchy_logic(event, paths, target_id, action):
    sender_id = event.sender_id
    
    # رتبة المنفذ
    s_rank = "عضو"
    if os.path.exists(paths["owner"]):
        with open(paths["owner"], "r") as f:
            if json.load(f).get("id") == sender_id: s_rank = "owner"
    if s_rank != "owner" and os.path.exists(paths["ranks"]):
        with open(paths["ranks"], "r") as f:
            ranks = json.load(f)
            s_rank = ranks.get(str(sender_id), {}).get("rank", "عضو")

    # فحص الصلاحية (مسموح للمدير والمطور أو المالك)
    if s_rank != "owner":
        if os.path.exists(paths["perms"]):
            with open(paths["perms"], "r") as f:
                perms = json.load(f)
                if not perms.get(s_rank, {}).get("حظر", False):
                    await event.edit(f"⚠️ **رتبتك ({s_rank}) لا تملك صلاحية الحظر!**")
                    return False
        else: return False

    # رتبة الهدف
    t_rank = "عضو"
    if os.path.exists(paths["owner"]):
        with open(paths["owner"], "r") as f:
            if json.load(f).get("id") == target_id: t_rank = "owner"
    if t_rank != "owner" and os.path.exists(paths["ranks"]):
        with open(paths["ranks"], "r") as f:
            ranks = json.load(f)
            t_rank = ranks.get(str(target_id), {}).get("rank", "عضو")

    if RANK_POWER[s_rank] <= RANK_POWER[t_rank] and s_rank != "owner":
        msg = await event.edit(f"⚠️ **لا يمكنك نفي رتبة اعلى منك او مساوية لك ({t_rank})!**")
        await asyncio.sleep(10)
        await msg.delete()
        return False
    return True

# ==========================================
# أمر موقت حظر الهرمي (.موقت حظر)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.موقت حظر\s+(.*)$"))
async def timed_execution(event):
    if not event.is_group: return
    
    paths = get_paths(event.chat_id)
    if not paths: return await event.edit("⚠️ المجموعة غير مفعلة!")

    args = event.pattern_match.group(1).split()
    if not args: return await event.edit("⚠️ **مثال: .موقت حظر 1m**")

    seconds = parse_time(args[0])
    if not seconds: return await event.edit("⚠️ **وقت غير صالح! استخدم (s, m, h, d)**")

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

    # فحص الهرمية قبل بدء العد
    if not await check_hierarchy_logic(event, paths, user_id, "حظر"):
        return

    try:
        user_entity = await client.get_entity(user_id)
        name = user_entity.first_name or "المستخدم"

        # حلقة العد التنازلي
        while seconds > 0:
            step = 10 if seconds > 60 else 2
            if step > seconds: step = seconds

            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            time_left = f"{int(h)}h {int(m)}m {int(s)}s" if h > 0 else f"{int(m)}m {int(s)}s" if m > 0 else f"{int(s)}s"
            
            await event.edit(
                "★────────☭────────★\n"
                "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 𝑻𝑰𝑴𝑬𝑹 • ☭\n"
                "★────────☭────────★\n\n"
                f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
                f"• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **قرار نفي وشيك (هرمي)** ⏳\n"
                f"• 𝑻𝒊𝒎𝒆 𝑳𝒆𝒇𝒕 ⌯ `{time_left}`\n\n"
                "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
            )
            await asyncio.sleep(step)
            seconds -= step

        # التنفيذ النهائي
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري سحق الرتبة والنفي 〕 {f} ⌯")
            await asyncio.sleep(0.1)

        await client(functions.channels.EditBannedRequest(
            event.chat_id, user_id, 
            types.ChatBannedRights(until_date=None, view_messages=True)
        ))
        
        # التدوين في سجل المحظورين
        ban_list = []
        if os.path.exists(paths["ban"]):
            with open(paths["ban"], "r", encoding="utf-8") as f: ban_list = json.load(f)
        if user_id not in ban_list:
            ban_list.append(user_id)
            with open(paths["ban"], "w", encoding="utf-8") as f: json.dump(ban_list, f)
        
        await event.edit(f"• ⌯ **انتهى الوقت.. تم نفي {name} رسمياً!** 🚫")

    except Exception as e:
        await event.edit(f"⚠️ **خطأ في التنفيذ:** `{str(e)}`")
