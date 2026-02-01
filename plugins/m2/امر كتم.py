import __main__, asyncio, json, os
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]
BASE_DIR = "group"

# --- دالة جلب المسارات ---
def get_group_paths(chat_id):
    if not os.path.exists(BASE_DIR): return None
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return {
                "mute": os.path.join(gp, "mute.json"),
                "owner": os.path.join(gp, "owner.json"),
                "ranks": os.path.join(gp, "member_rank.json"),
                "perms": os.path.join(gp, "permissions.json")
            }
    return None

# --- دالة فحص الصلاحية ---
async def check_permission(event, paths, action):
    uid = event.sender_id
    # فحص المالك أولاً
    with open(paths["owner"], "r", encoding="utf-8") as f:
        if json.load(f).get("id") == uid: return True
    
    # فحص الرتبة والصلاحية
    if os.path.exists(paths["ranks"]):
        with open(paths["ranks"], "r", encoding="utf-8") as f:
            ranks = json.load(f)
            if str(uid) in ranks:
                u_rank = ranks[str(uid)]["rank"]
                if os.path.exists(paths["perms"]):
                    with open(paths["perms"], "r", encoding="utf-8") as f:
                        perms = json.load(f)
                        return perms.get(u_rank, {}).get(action, False)
    return False

# ==========================================
# 1. أمر الكتم (.كتم بالرد)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كتم$"))
async def mute_user(event):
    if not event.is_group or not event.is_reply: return
    
    paths = get_group_paths(event.chat_id)
    if not paths: return
    
    if not await check_permission(event, paths, "كتم"):
        return await event.edit("⚠️ **عذراً، رتبتك لا تملك صلاحية الكتم!**")

    reply = await event.get_reply_message()
    u_id = str(reply.sender_id)
    user = await reply.get_sender()
    u_name = user.first_name or "Unknown"

    mute_data = []
    if os.path.exists(paths["mute"]):
        with open(paths["mute"], "r", encoding="utf-8") as f:
            mute_data = json.load(f)

    if u_id in mute_data:
        return await event.edit("⚠️ **الشخص مكتوم بالفعل!**")

    # تأثير الدوامة (Vortex)
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري كتم الشخص... 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    mute_data.append(u_id)
    with open(paths["mute"], "w", encoding="utf-8") as f:
        json.dump(mute_data, f, indent=4, ensure_ascii=False)

    # الكليشة الإنجليزية الأصلية
    await event.edit(f"★────────☭────────★\n• 𝑴𝒖𝒕𝒆𝒅 𝑫𝒐𝒏𝒆 ✔\n• 𝑼𝒔𝒆𝒓 ⌯ {u_name}\n• 𝑰𝒅 ⌯ `{u_id}`\n★────────☭────────★")

# ==========================================
# 2. أمر فك الكتم (.فك كتم بالرد)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.فك كتم$"))
async def unmute_user(event):
    if not event.is_group or not event.is_reply: return
    
    paths = get_group_paths(event.chat_id)
    if not paths or not await check_permission(event, paths, "كتم"):
        return await event.edit("⚠️ **عذراً، رتبتك لا تملك صلاحية فك الكتم!**")

    reply = await event.get_reply_message()
    u_id = str(reply.sender_id)

    if not os.path.exists(paths["mute"]): return

    with open(paths["mute"], "r", encoding="utf-8") as f:
        mute_data = json.load(f)

    if u_id not in mute_data:
        return await event.edit("⚠️ **الشخص غير مكتوم!**")

    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري فك الكتم... 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    mute_data.remove(u_id)
    with open(paths["mute"], "w", encoding="utf-8") as f:
        json.dump(mute_data, f, indent=4, ensure_ascii=False)

    # الكليشة القديمة
    await event.edit("• ⌯ **تم فك الكتم عن الشخص بنجاح ✔**")

# ==========================================
# 3. المحرك (حذف الرسائل)
# ==========================================
@client.on(events.NewMessage(incoming=True))
async def mute_engine(event):
    if not event.is_group: return
    paths = get_group_paths(event.chat_id)
    if not paths or not os.path.exists(paths["mute"]): return

    with open(paths["mute"], "r", encoding="utf-8") as f:
        mute_list = json.load(f)

    if str(event.sender_id) in mute_list:
        try: await event.delete()
        except: pass
