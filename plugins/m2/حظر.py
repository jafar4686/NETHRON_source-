import __main__, os, asyncio, json
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# --- دالات المساعدة ---
def get_paths(chat_id):
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return gp, os.path.join(gp, "ban.json"), os.path.join(gp, "owner.json")
    return None, None, None

def is_owner(chat_id, sender_id):
    _, _, owner_path = get_paths(chat_id)
    if owner_path and os.path.exists(owner_path):
        with open(owner_path, "r", encoding="utf-8") as f:
            return json.load(f).get("id") == sender_id
    return False

# ==========================================
# 8. أمر الحظر (.حظر بالرد)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حظر$"))
async def ban_user(event):
    if not event.is_group: return
    if not is_owner(event.chat_id, event.sender_id): return 

    if not event.is_reply:
        return await event.edit("⚠️ **رد على الشخص لحظره نهائياً!**")

    reply_msg = await event.get_reply_message()
    user_id = reply_msg.sender_id
    if user_id == event.sender_id: return await event.edit("⚠️ **لا يمكن حظر الملك!**")

    await event.edit("⌯ 〔 جاري نفي الشخص من المملكة... 〕 ⌯")

    try:
        user = await client.get_entity(user_id)
        gp_path, ban_file, _ = get_paths(event.chat_id)

        # حركات الدوامة (VORTEX)
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري الحظر والتدوين في السجلات 〕 {f} ⌯")
            await asyncio.sleep(0.1)

        # 1. الحظر من تليجرام
        await client(functions.channels.EditBannedRequest(event.chat_id, user_id, types.ChatBannedRights(until_date=None, view_messages=True)))
        
        # 2. التدوين في ملف ban.json لمنعه من العودة
        ban_list = []
        if os.path.exists(ban_file):
            with open(ban_file, "r", encoding="utf-8") as f: ban_list = json.load(f)
        
        if user_id not in ban_list:
            ban_list.append(user_id)
            with open(ban_file, "w", encoding="utf-8") as f: json.dump(ban_list, f)

        final_text = (
            "★────────☭────────★\n"
            "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {user.first_name}\n"
            f"• 𝑰𝒅 ⌯ `{user_id}`\n"
            "• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **تم الحظر والنفي المؤبد** 🚫\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )
        await event.edit(final_text)

    except Exception as e:
        await event.edit(f"⚠️ **فشل الحظر:** `{str(e)}`")

# ==========================================
# 9. رادار الطرد التلقائي (لو حاول المحظور يرجع)
# ==========================================
@client.on(events.ChatAction())
async def auto_kick_banned(event):
    if event.user_joined or event.user_added:
        gp_path, ban_file, _ = get_paths(event.chat_id)
        if ban_file and os.path.exists(ban_file):
            with open(ban_file, "r", encoding="utf-8") as f:
                ban_list = json.load(f)
            
            if event.user_id in ban_list:
                try:
                    await client.kick_participant(event.chat_id, event.user_id)
                    await event.reply(f"⚠️ **المحظر آيديه `{event.user_id}` حاول الدخول وتم طرده فوراً!**")
                except: pass
