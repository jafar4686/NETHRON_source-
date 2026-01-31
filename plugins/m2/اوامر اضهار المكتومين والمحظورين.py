import __main__, os, json
from telethon import events

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
BASE_DIR = "group"

# --- دالة جلب المسارات ---
def get_list_paths(chat_id):
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return {
                "ban": os.path.join(gp, "ban.json"),
                "mute": os.path.join(gp, "mute.json"),
                "owner": os.path.join(gp, "owner.json")
            }
    return None

# دالة التحقق من المالك
def is_owner(chat_id, sender_id):
    paths = get_list_paths(chat_id)
    if paths and os.path.exists(paths["owner"]):
        with open(paths["owner"], "r", encoding="utf-8") as f:
            return json.load(f).get("id") == sender_id
    return False

# ==========================================
# 11. أمر عرض المحظرين (.المحظرين)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.المحظرين$"))
async def show_banned(event):
    if not event.is_group: return
    if not is_owner(event.chat_id, event.sender_id): return

    paths = get_list_paths(event.chat_id)
    if not paths or not os.path.exists(paths["ban"]):
        return await event.edit("⚠️ **لا توجد سجلات حظر لهذه المجموعة!**")

    with open(paths["ban"], "r", encoding="utf-8") as f:
        ban_list = json.load(f)

    if not ban_list:
        return await event.edit("• ⌯ **لا يوجد محظرين في المملكة حالياً.**")

    await event.edit("⌯ 〔 جاري استخراج قائمة المنفيين... 〕 ⌯")
    
    res_text = "☭ • 𝐵𝐴𝑁𝑁𝐸𝐷 𝐿𝐼𝑆𝑇 • ☭\n★────────☭────────★\n"
    for index, b_id in enumerate(ban_list, 1):
        res_text += f"{index} - ID: `{b_id}`\n"
    
    res_text += "★────────☭────────★\n• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
    await event.edit(res_text)

# ==========================================
# 12. أمر عرض المكتومين (.المكتومين)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.المكتومين$"))
async def show_muted(event):
    if not event.is_group: return
    if not is_owner(event.chat_id, event.sender_id): return

    paths = get_list_paths(event.chat_id)
    if not paths or not os.path.exists(paths["mute"]):
        return await event.edit("⚠️ **لا توجد سجلات كتم لهذه المجموعة!**")

    with open(paths["mute"], "r", encoding="utf-8") as f:
        mute_list = json.load(f)

    if not mute_list:
        return await event.edit("• ⌯ **لا يوجد مكتومين في المملكة حالياً.**")

    await event.edit("⌯ 〔 جاري استخراج قائمة الصامتين... 〕 ⌯")
    
    res_text = "☭ • 𝑀𝑈𝑇𝐸𝐷 𝐿𝐼𝑆𝑇 • ☭\n★────────☭────────★\n"
    for index, m_id in enumerate(mute_list, 1):
        res_text += f"{index} - ID: `{m_id}`\n"
    
    res_text += "★────────☭────────★\n• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
    await event.edit(res_text)
