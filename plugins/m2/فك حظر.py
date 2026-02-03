import __main__, os, asyncio, json
from telethon import events, functions, types

client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# 1. موازين القوة (الهرمية الأساسية)
RANK_POWER = {
    "عضو": 0, "مميز": 1, "ادمن": 2, "مدير": 3, "مطور": 4, "owner": 5
}

# --- دالة جلب المسارات الموحدة ---
def get_group_paths(chat_id):
    if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return {
                "owner": os.path.join(gp, "owner.json"),
                "ranks": os.path.join(gp, "member_rank.json"),
                "perms": os.path.join(gp, "permissions.json"),
                "ban_file": os.path.join(gp, "ban.json")
            }
    return None

# --- العقل المدبر: فحص الهرمية لفك الحظر ---
async def check_unban_logic(event, paths, target_id):
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

    # 1. فحص الصلاحية من لوحة التحكم
    if s_rank != "owner":
        if os.path.exists(paths["perms"]):
            with open(paths["perms"], "r") as f:
                perms = json.load(f)
                if not perms.get(s_rank, {}).get("حظر", False):
                    await event.edit(f"⚠️ **رتبتك ({s_rank}) لا تملك صلاحية إلغاء الحظر!**")
                    return False
        else: return False

    # 2. فحص رتبة الشخص المطلوب فك حظره (لمنع التجاوز الهرمي)
    t_rank = "عضو"
    if os.path.exists(paths["owner"]):
        with open(paths["owner"], "r") as f:
            if json.load(f).get("id") == target_id: t_rank = "owner"
    if t_rank != "owner" and os.path.exists(paths["ranks"]):
        with open(paths["ranks"], "r") as f:
            ranks = json.load(f)
            t_rank = ranks.get(str(target_id), {}).get("rank", "عضو")

    if RANK_POWER[s_rank] <= RANK_POWER[t_rank] and s_rank != "owner":
        msg = await event.edit(f"⚠️ **لا يمكنك فك حظر رتبة أعلى منك أو مساوية لك ({t_rank})!**")
        await asyncio.sleep(10)
        await msg.delete()
        return False
        
    return True

# ==========================================
# أمر إلغاء الحظر الهرمي (.الغاء حظر)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.الغاء حظر(?:\s+(.*))?$"))
async def unban_user(event):
    if not event.is_group: return
    
    paths = get_group_paths(event.chat_id)
    if not paths: return

    input_str = event.pattern_match.group(1)
    target_id = None

    # تحديد الهدف (رد، يوزر، أو آيدي)
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        target_id = reply_msg.sender_id
    elif input_str:
        try:
            user_entity = await client.get_entity(input_str)
            target_id = user_entity.id
        except: return await event.edit("⚠️ **المستخدم غير موجود في سجلات التليجرام!**")
    else:
        return await event.edit("⚠️ **يرجى الرد على الشخص أو إرسال يوزره لفك حظره!**")

    # تشغيل منطق الهرمية
    if not await check_unban_logic(event, paths, target_id):
        return

    try:
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري إصدار العفو الملكي 〕 {f} ⌯")
            await asyncio.sleep(0.1)

        # 1. فك الحظر تقنياً في تليجرام
        await client(functions.channels.EditBannedRequest(
            event.chat_id, target_id, 
            types.ChatBannedRights(until_date=None, view_messages=False)
        ))

        # 2. المسح من سجل "المنفيين" (ban.json) لتعطيل الرادار عنه
        if os.path.exists(paths["ban_file"]):
            with open(paths["ban_file"], "r", encoding="utf-8") as f:
                ban_list = [str(i) for i in json.load(f)]
            
            if str(target_id) in ban_list:
                ban_list.remove(str(target_id))
                with open(paths["ban_file"], "w", encoding="utf-8") as f:
                    json.dump(ban_list, f)

        user = await client.get_entity(target_id)
        name = user.first_name or "المستخدم"

        final_text = (
            "★────────☭────────★\n"
            "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑼𝑵𝑩𝑨𝑵 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
            f"• 𝑰𝒅 ⌯ `{target_id}`\n"
            "• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **تم فك القيد وإصدار العفو الملكي** ✅\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
        )
        await event.edit(final_text)

    except Exception as e:
        await event.edit(f"⚠️ **فشل إلغاء الحظر:** `{str(e)}`")
