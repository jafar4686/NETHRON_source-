import __main__, asyncio, json, os
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]
BASE_DIR = "group"

# --- دالة جلب المسارات والتحقق من المالك ---
def get_mute_paths(chat_id):
    if not os.path.exists(BASE_DIR): return None
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            group_path = os.path.join(BASE_DIR, folder)
            return {
                "mute_file": os.path.join(group_path, "mute.json"),
                "owner_file": os.path.join(group_path, "owner.json")
            }
    return None

async def is_owner(event, paths):
    if not os.path.exists(paths["owner_file"]): return False
    with open(paths["owner_file"], "r", encoding="utf-8") as f:
        data = json.load(f)
        return event.sender_id == data.get("id")

# ==========================================
# 1. أمر الكتم (.كتم بالرد)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كتم$"))
async def mute_user(event):
    if not event.is_group or not event.is_reply: return
    
    paths = get_mute_paths(event.chat_id)
    if not paths or not await is_owner(event, paths): return

    reply = await event.get_reply_message()
    u_id = str(reply.sender_id)
    u_name = (await reply.get_sender()).first_name or "بدون اسم"

    # تهيئة ملف المكتومين
    mute_data = []
    if os.path.exists(paths["mute_file"]):
        with open(paths["mute_file"], "r", encoding="utf-8") as f:
            mute_data = json.load(f)

    # التحقق إذا كان مكتوم مسبقاً
    if u_id in mute_data:
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 الشخص مكتوم من قبل! 〕 {f} ⌯")
            await asyncio.sleep(0.1)
        return

    # عملية الكتم مع الدوامة
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري كتم الشخص... 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    mute_data.append(u_id)
    with open(paths["mute_file"], "w", encoding="utf-8") as f:
        json.dump(mute_data, f, indent=4, ensure_ascii=False)

    await event.edit(f"★────────☭────────★\n• 𝑴𝒖𝒕𝒆𝒅 𝑫𝒐𝒏𝒆 ✔\n• 𝑼𝒔𝒆𝒓 ⌯ {u_name}\n• 𝑰𝒅 ⌯ `{u_id}`\n★────────☭────────★")

# ==========================================
# 2. أمر فك الكتم (.فك كتم بالرد)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.فك كتم$"))
async def unmute_user(event):
    if not event.is_group or not event.is_reply: return
    
    paths = get_mute_paths(event.chat_id)
    if not paths or not await is_owner(event, paths): return

    reply = await event.get_reply_message()
    u_id = str(reply.sender_id)

    if not os.path.exists(paths["mute_file"]): return

    with open(paths["mute_file"], "r", encoding="utf-8") as f:
        mute_data = json.load(f)

    if u_id not in mute_data:
        return await event.edit("⚠️ **هذا الشخص غير مكتوم أصلاً!**")

    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري فك الكتم... 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    mute_data.remove(u_id)
    with open(paths["mute_file"], "w", encoding="utf-8") as f:
        json.dump(mute_data, f, indent=4, ensure_ascii=False)

    await event.edit("• ⌯ **تم فك الكتم عن الشخص بنجاح ✔**")

# ==========================================
# 3. المحرك (حذف رسائل المكتومين فوراً)
# ==========================================
@client.on(events.NewMessage(incoming=True))
async def mute_engine(event):
    if not event.is_group: return
    
    paths = get_mute_paths(event.chat_id)
    if not paths or not os.path.exists(paths["mute_file"]): return

    with open(paths["mute_file"], "r", encoding="utf-8") as f:
        mute_list = json.load(f)

    if str(event.sender_id) in mute_list:
        try:
            await event.delete()
        except:
            pass
