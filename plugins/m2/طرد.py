import __main__, os, asyncio, json
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
                "perms": os.path.join(gp, "permissions.json")
            }
    return None

async def can_kick(event, paths):
    uid = event.sender_id
    # 1. فحص المالك (له الحق دائماً)
    if os.path.exists(paths["owner"]):
        with open(paths["owner"], "r", encoding="utf-8") as f:
            if json.load(f).get("id") == uid: return True
            
    # 2. فحص الرتبة والصلاحية من الملفات
    if os.path.exists(paths["ranks"]):
        with open(paths["ranks"], "r", encoding="utf-8") as f:
            ranks = json.load(f)
            if str(uid) in ranks:
                u_rank = ranks[str(uid)]["rank"]
                if os.path.exists(paths["perms"]):
                    with open(paths["perms"], "r", encoding="utf-8") as f:
                        perms = json.load(f)
                        # فحص هل رتبته مسموح لها بـ "طرد"
                        return perms.get(u_rank, {}).get("طرد", False)
    return False

# ==========================================
# أمر الطرد المربوط بالصلاحيات
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.طرد$"))
async def kick_user(event):
    if not event.is_group: return
    
    paths = get_group_paths(event.chat_id)
    if not paths: return
    
    # التحقق من الصلاحية (مالك أو رتبة مفعل لها الطرد)
    if not await can_kick(event, paths):
        return await event.edit("⚠️ **عذراً، رتبتك لا تملك صلاحية الطرد!**")

    if not event.is_reply:
        return await event.edit("⚠️ **يرجى الرد على الشخص لطرده!**")

    reply_msg = await event.get_reply_message()
    user_id = reply_msg.sender_id
    
    if user_id == event.sender_id:
        return await event.edit("⚠️ **ما تكدر تطرد نفسك يا ملك!**")

    try:
        user_entity = await client.get_entity(user_id)
        name = user_entity.first_name or "المستخدم"

        # حركات الفورتكس
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري استبعاد {name} من المملكة 〕 {f} ⌯")
            await asyncio.sleep(0.1)

        # تنفيذ الطرد
        await client.kick_participant(event.chat_id, user_id)
        
        # التنسيق النهائي (عراق ثون ستايل)
        final_text = (
            "★────────☭────────★\n"
            "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
            f"• 𝑰𝒅 ⌯ `{user_id}`\n"
            "• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **𝑲𝒊𝒄𝒌𝒆𝒅 𝑫𝒐𝒏𝒆** ✅\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )
        await event.edit(final_text)

    except Exception as e:
        await event.edit(f"⚠️ **فشل الطرد:**\n`{str(e)}` \n\nتأكد أن البوت مشرف بالمجموعة.")
