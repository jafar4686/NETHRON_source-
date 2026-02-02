import __main__, os, asyncio, json, re
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# --- دالة جلب المسارات وفحص الصلاحية المشتركة ---
def get_group_paths(chat_id):
    if not os.path.exists(BASE_DIR): return None
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

async def can_unban(event, paths):
    uid = event.sender_id
    # 1. فحص المالك
    if os.path.exists(paths["owner"]):
        with open(paths["owner"], "r", encoding="utf-8") as f:
            if json.load(f).get("id") == uid: return True
            
    # 2. فحص الرتبة والصلاحية (بشرط مو مميز)
    if os.path.exists(paths["ranks"]):
        with open(paths["ranks"], "r", encoding="utf-8") as f:
            ranks = json.load(f)
            if str(uid) in ranks:
                u_rank = ranks[str(uid)]["rank"]
                if u_rank == "مميز": return False # المميز ممنوع نهائياً
                
                if os.path.exists(paths["perms"]):
                    with open(paths["perms"], "r", encoding="utf-8") as f:
                        perms = json.load(f)
                        # نستخدم صلاحية "حظر" كمرجع لإلغاء الحظر أيضاً
                        return perms.get(u_rank, {}).get("حظر", False)
    return False

# ==========================================
# أمر الغاء الحظر المربوط بالسيستم
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.الغاء حظر(?:\s+(.*))?$"))
async def unban_user(event):
    if not event.is_group: return
    
    paths = get_group_paths(event.chat_id)
    if not paths: return
    
    # التحقق من الصلاحية
    if not await can_unban(event, paths):
        return await event.edit("⚠️ **عذراً، رتبتك لا تملك صلاحية الغاء الحظر!**")

    input_str = event.pattern_match.group(1)
    user_id = None

    # تحديد المستخدم
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        user_id = reply_msg.sender_id
    elif input_str:
        if input_str.isdigit():
            user_id = int(input_str)
        else:
            try:
                user_entity = await client.get_entity(input_str)
                user_id = user_entity.id
            except:
                return await event.edit("⚠️ **لم أستطع العثور على هذا المستخدم!**")
    else:
        return await event.edit("⚠️ **رد على الشخص أو أرسل آيديه/يوزره لفك الحظر!**")

    try:
        # حركات الدوامة (عراق ثون)
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري مسح القيود وإصدار العفو 〕 {f} ⌯")
            await asyncio.sleep(0.1)

        # 1. فك الحظر رسمياً في تليجرام
        await client(functions.channels.EditBannedRequest(
            event.chat_id, user_id, 
            types.ChatBannedRights(until_date=None, view_messages=False)
        ))

        # 2. حذفه من ملف ban.json
        if os.path.exists(paths["ban_file"]):
            with open(paths["ban_file"], "r", encoding="utf-8") as f:
                ban_list = json.load(f)
            if user_id in ban_list:
                ban_list.remove(user_id)
                with open(paths["ban_file"], "w", encoding="utf-8") as f:
                    json.dump(ban_list, f)

        user = await client.get_entity(user_id)
        name = user.first_name or "المستخدم"

        final_text = (
            "★────────☭────────★\n"
            "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
            f"• 𝑰𝒅 ⌯ `{user_id}`\n"
            "• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **𝑼𝒏𝒃𝒂𝒏𝒏𝒆𝒅 𝑫𝒐𝒏𝒆** ✅\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )
        await event.edit(final_text)

    except Exception as e:
        await event.edit(f"⚠️ **فشل الغاء الحظر:** `{str(e)}`")
