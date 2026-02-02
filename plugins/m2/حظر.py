import __main__, os, asyncio, json
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# --- دالة جلب المسارات وفحص الصلاحية ---
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

async def can_ban(event, paths):
    uid = event.sender_id
    # 1. المالك (حق مطلق)
    if os.path.exists(paths["owner"]):
        with open(paths["owner"], "r", encoding="utf-8") as f:
            if json.load(f).get("id") == uid: return True
            
    # 2. فحص الرتبة (عدا المميز) والصلاحية
    if os.path.exists(paths["ranks"]):
        with open(paths["ranks"], "r", encoding="utf-8") as f:
            ranks = json.load(f)
            if str(uid) in ranks:
                u_rank = ranks[str(uid)]["rank"]
                if u_rank == "مميز": return False
                
                if os.path.exists(paths["perms"]):
                    with open(paths["perms"], "r", encoding="utf-8") as f:
                        perms = json.load(f)
                        return perms.get(u_rank, {}).get("حظر", False)
    return False

# ==========================================
# 1. أمر الحظر المربوط (.حظر بالرد)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حظر$"))
async def ban_user(event):
    if not event.is_group: return
    
    paths = get_group_paths(event.chat_id)
    if not paths: return
    
    # فحص الصلاحية
    if not await can_ban(event, paths):
        return await event.edit("⚠️ **عذراً، رتبتك لا تملك صلاحية الحظر!**")

    if not event.is_reply:
        return await event.edit("⚠️ **رد على الشخص لحظره نهائياً!**")

    reply_msg = await event.get_reply_message()
    user_id = reply_msg.sender_id
    if user_id == event.sender_id: return await event.edit("⚠️ **لا يمكن حظر الملك!**")

    try:
        user = await client.get_entity(user_id)
        name = user.first_name or "المستخدم"

        # دوامة الفورتكس
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري الحظر والتدوين في السجلات 〕 {f} ⌯")
            await asyncio.sleep(0.1)

        # 1. الحظر من تليجرام
        await client(functions.channels.EditBannedRequest(
            event.chat_id, user_id, 
            types.ChatBannedRights(until_date=None, view_messages=True)
        ))
        
        # 2. التدوين في ban.json (الرادار)
        ban_list = []
        if os.path.exists(paths["ban_file"]):
            with open(paths["ban_file"], "r", encoding="utf-8") as f:
                ban_list = json.load(f)
        
        if user_id not in ban_list:
            ban_list.append(user_id)
            with open(paths["ban_file"], "w", encoding="utf-8") as f:
                json.dump(ban_list, f)

        final_text = (
            "★────────☭────────★\n"
            "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
            f"• 𝑰𝒅 ⌯ `{user_id}`\n"
            "• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **𝑩𝒂𝒏𝒏𝒆𝒅 𝑫𝒐𝒏𝒆** 🚫\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )
        await event.edit(final_text)

    except Exception as e:
        await event.edit(f"⚠️ **فشل الحظر:** `{str(e)}`")

# ==========================================
# 2. رادار الطرد التلقائي (المراقبة المستمرة)
# ==========================================
@client.on(events.ChatAction())
async def auto_kick_banned(event):
    if event.user_joined or event.user_added:
        paths = get_group_paths(event.chat_id)
        if paths and os.path.exists(paths["ban_file"]):
            with open(paths["ban_file"], "r", encoding="utf-8") as f:
                ban_list = json.load(f)
            
            if event.user_id in ban_list:
                try:
                    await client.kick_participant(event.chat_id, event.user_id)
                    await event.reply(f"⚠️ **المحظر آيديه `{event.user_id}` حاول الدخول وتم طرده فوراً!**")
                except: pass
