import __main__, os, json, asyncio
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
BASE_DIR = "group"

# 1. موازين القوة (الهرمية)
RANK_POWER = {
    "عضو": 0, "مميز": 1, "ادمن": 2, "مدير": 3, "مطور": 4, "owner": 5
}

# --- دالة جلب المسارات الموحدة ---
def get_group_paths(chat_id):
    if not os.path.exists(BASE_DIR): return None
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return {
                "owner": os.path.join(gp, "owner.json"),
                "ranks": os.path.join(gp, "member_rank.json"),
                "stats": os.path.join(gp, "stats.json"),
                "perms": os.path.join(gp, "permissions.json")
            }
    return None

# ==========================================
# أمر الكشف الهرمي (.كشف بالرد)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كشف$"))
async def detect_user(event):
    if not event.is_group: return
    
    paths = get_group_paths(event.chat_id)
    if not paths: return

    # 1. فحص رتبة المنفذ وصلاحيته للكشف
    sender_id = event.sender_id
    s_rank = "عضو"
    if os.path.exists(paths["owner"]):
        with open(paths["owner"], "r") as f:
            if json.load(f).get("id") == sender_id: s_rank = "owner"
    
    if s_rank != "owner" and os.path.exists(paths["ranks"]):
        with open(paths["ranks"], "r") as f:
            ranks_data = json.load(f)
            s_rank = ranks_data.get(str(sender_id), {}).get("rank", "عضو")

    # فحص الصلاحية من permissions.json
    if s_rank != "owner":
        if os.path.exists(paths["perms"]):
            with open(paths["perms"], "r") as f:
                perms = json.load(f)
                if not perms.get(s_rank, {}).get("كشف", False):
                    warn = await event.edit(f"⚠️ **رتبتك ({s_rank}) لا تملك صلاحية الكشف!**")
                    await asyncio.sleep(7)
                    return await warn.delete()
        else: return

    if not event.is_reply:
        return await event.edit("⚠️ **يرجى الرد على الشخص لكشف حسابه!**")

    reply_msg = await event.get_reply_message()
    target_id = reply_msg.sender_id
    
    await event.edit("⌯ 〔 جاري استخراج البيانات من سجلات المملكة... 〕 ⌯")

    try:
        # جلب معلومات الحساب
        user = await client.get_entity(target_id)
        full_user = await client(functions.users.GetFullUserRequest(user.id))
        
        # 2. تحديد رتبة الهدف في السورس
        t_rank = "عضو"
        if os.path.exists(paths["owner"]):
            with open(paths["owner"], "r") as f:
                if json.load(f).get("id") == target_id: t_rank = "المالك 👑"
        
        if t_rank == "عضو" and os.path.exists(paths["ranks"]):
            with open(paths["ranks"], "r") as f:
                r_data = json.load(f)
                t_rank = r_data.get(str(target_id), {}).get("rank", "عضو")

        # 3. جلب الإحصائيات من stats.json
        count_msg = 0
        if os.path.exists(paths["stats"]):
            with open(paths["stats"], "r", encoding="utf-8") as f:
                stats_data = json.load(f)
                count_msg = stats_data.get(str(target_id), {}).get("count", 0)

        # تنسيق البيانات
        name = user.first_name or "بدون اسم"
        username = f"@{user.username}" if user.username else "لا يوجد"
        bio = full_user.full_user.about or "لا يوجد بايو"
        
        final_text = (
            "★────────☭────────★\n"
            "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
            f"• 𝑼𝒔𝒆𝒓 ⌯ {username}\n"
            f"• 𝑩𝒊𝒐 ⌯ {bio}\n"
            f"• 𝑴𝒆𝒔𝒔𝒂𝒈𝒆𝒔 ⌯ {count_msg}\n"
            f"• 𝑹𝒂𝒏𝒌 ⌯ {t_rank}\n"
            f"• 𝑰𝒅 ⌯ `{user.id}`\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )

        await event.edit(final_text, link_preview=False)

    except Exception as e:
        await event.edit(f"⚠️ **فشل الكشف:** `{str(e)}`")
