import __main__, os, asyncio, json
from telethon import events, functions, types

client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# 1. موازين القوة الهرمية (المرجع الأساسي)
RANK_POWER = {
    "عضو": 0, "مميز": 1, "ادمن": 2, "مدير": 3, "مطور": 4, "owner": 5
}

# --- دالة جلب المسارات ---
def get_group_paths(chat_id):
    if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return {
                "owner": os.path.join(gp, "owner.json"),
                "ranks": os.path.join(gp, "member_rank.json"),
                "perms": os.path.join(gp, "permissions.json")
            }
    return None

# --- العقل المدبر: فحص الهرمية والصلاحية للطرد ---
async def check_kick_hierarchy(event, paths, target_id):
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
                if not perms.get(s_rank, {}).get("طرد", False):
                    await event.edit(f"⚠️ **رتبتك ({s_rank}) لا تملك صلاحية الطرد!**")
                    return False
        else: return False

    # 2. فحص رتبة الهدف (المطرود)
    t_rank = "عضو"
    if os.path.exists(paths["owner"]):
        with open(paths["owner"], "r") as f:
            if json.load(f).get("id") == target_id: t_rank = "owner"
    if t_rank != "owner" and os.path.exists(paths["ranks"]):
        with open(paths["ranks"], "r") as f:
            ranks = json.load(f)
            t_rank = ranks.get(str(target_id), {}).get("rank", "عضو")

    # تطبيق قانون الهرمية
    if RANK_POWER[s_rank] <= RANK_POWER[t_rank] and s_rank != "owner":
        msg = await event.edit(f"⚠️ **لا يمكنك طرد رتبة أعلى منك أو مساوية لك ({t_rank})!**")
        await asyncio.sleep(10)
        await msg.delete()
        return False
        
    return True

# ==========================================
# أمر الطرد الهرمي (.طرد بالرد)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.طرد$"))
async def kick_user(event):
    if not event.is_group: return
    
    paths = get_group_paths(event.chat_id)
    if not paths: return await event.edit("⚠️ المجموعة غير مفعلة بالسورس!")
    
    if not event.is_reply:
        return await event.edit("⚠️ **يرجى الرد على الشخص لطرده!**")

    reply_msg = await event.get_reply_message()
    target_id = reply_msg.sender_id
    
    if target_id == event.sender_id:
        return await event.edit("⚠️ **تريد تطرد نفسك؟ ارجع للمملكة واستريح!**")

    # تشغيل منطق الهرمية قبل التنفيذ
    if not await check_kick_hierarchy(event, paths, target_id):
        return

    try:
        user_entity = await client.get_entity(target_id)
        name = user_entity.first_name or "المستخدم"

        # حركات الدوامة (Vortex)
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري استبعاد {name} من المملكة 〕 {f} ⌯")
            await asyncio.sleep(0.1)

        # تنفيذ الطرد النهائي
        await client.kick_participant(event.chat_id, target_id)
        
        # الكليشة النهائية (IRAQTHOON STYLE)
        final_text = (
            "★────────☭────────★\n"
            "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
            f"• 𝑰𝒅 ⌯ `{target_id}`\n"
            "• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **𝑲𝒊𝒄𝒌𝒆𝒅 𝑫𝒐𝒏𝒆** ✅\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
        )
        await event.edit(final_text)

    except Exception as e:
        await event.edit(f"⚠️ **فشل الطرد:** `{str(e)}` \nتأكد أنك مشرف وتمتلك صلاحيات كافية.")
