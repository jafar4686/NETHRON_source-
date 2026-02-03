import __main__, asyncio, json, os
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]
BASE_DIR = "group"

# 1. موازين القوة (الهرمية)
RANK_POWER = {
    "عضو": 0,
    "مميز": 1,
    "ادمن": 2,
    "مدير": 3,
    "مطور": 4,
    "owner": 5  # المالك (أنت)
}

# --- دالة جلب المسارات ---
def get_group_paths(chat_id):
    if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)
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

# --- دالة فحص الهرمية والصلاحية (العقل المدبر) ---
async def check_admin_logic(event, paths, target_id, action):
    sender_id = event.sender_id
    
    # جلب رتبة المنفذ (أنت أو رتبتك بالسورس)
    s_rank = "عضو"
    if os.path.exists(paths["owner"]):
        with open(paths["owner"], "r") as f:
            if json.load(f).get("id") == sender_id: s_rank = "owner"
    
    if s_rank != "owner" and os.path.exists(paths["ranks"]):
        with open(paths["ranks"], "r") as f:
            ranks = json.load(f)
            s_rank = ranks.get(str(sender_id), {}).get("rank", "عضو")

    # 1. فحص هل الرتبة عندها صلاحية (كتم/فك كتم) من ملف الصلاحيات
    if s_rank != "owner":
        if os.path.exists(paths["perms"]):
            with open(paths["perms"], "r") as f:
                perms = json.load(f)
                if not perms.get(s_rank, {}).get(action, False):
                    await event.edit(f"⚠️ **رتبتك ({s_rank}) لا تملك صلاحية {action}!**")
                    return False
        else: return False

    # 2. فحص الهرمية (مقارنة الرتب)
    t_rank = "عضو"
    if os.path.exists(paths["owner"]):
        with open(paths["owner"], "r") as f:
            if json.load(f).get("id") == target_id: t_rank = "owner"
            
    if t_rank != "owner" and os.path.exists(paths["ranks"]):
        with open(paths["ranks"], "r") as f:
            ranks = json.load(f)
            t_rank = ranks.get(str(target_id), {}).get("rank", "عضو")

    if RANK_POWER[s_rank] <= RANK_POWER[t_rank] and s_rank != "owner":
        msg = await event.edit(f"⚠️ **لا يمكنك {action} رتبة اعلى منك او مساوية لك ({t_rank})!**")
        await asyncio.sleep(10)
        await msg.delete()
        return False
        
    return True

# ==========================================
# 1. أمر الكتم (.كتم بالرد)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كتم$"))
async def mute_user(event):
    if not event.is_group or not event.is_reply: return
    
    paths = get_group_paths(event.chat_id)
    if not paths: return

    reply = await event.get_reply_message()
    target_id = reply.sender_id

    # تشغيل المنطق الهرمي
    if not await check_admin_logic(event, paths, target_id, "كتم"):
        return

    u_id = str(target_id)
    mute_data = []
    if os.path.exists(paths["mute"]):
        with open(paths["mute"], "r") as f: mute_data = json.load(f)

    if u_id in mute_data:
        return await event.edit("⚠️ **هذا الشخص ملجوم بالفعل!**")

    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري تنفيذ الكتم الهرمي 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    mute_data.append(u_id)
    with open(paths["mute"], "w") as f: json.dump(mute_data, f)

    await event.edit(f"★────────☭────────★\n   ☭ • 𝑴𝑼𝑻𝑬𝑫 𝑫𝑶𝑵𝑬 • ☭\n★────────☭────────★\n• تم كتمه وكسر رتبته بنجاح ✅")

# ==========================================
# 2. أمر فك الكتم (.فك كتم بالرد)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.فك كتم$"))
async def unmute_user(event):
    if not event.is_group or not event.is_reply: return
    
    paths = get_group_paths(event.chat_id)
    reply = await event.get_reply_message()
    
    if not await check_admin_logic(event, paths, reply.sender_id, "فك كتم"):
        return

    u_id = str(reply.sender_id)
    if os.path.exists(paths["mute"]):
        with open(paths["mute"], "r") as f: mute_data = json.load(f)
        if u_id in mute_data:
            mute_data.remove(u_id)
            with open(paths["mute"], "w") as f: json.dump(mute_data, f)
            await event.edit("• ⌯ **تم فك الكتم، خلي يحجي هسة ✔**")
        else:
            await event.edit("⚠️ **الشخص مو مكتوم أصلاً!**")

# ==========================================
# 3. محرك الحذف (الشغال)
# ==========================================
@client.on(events.NewMessage(incoming=True))
async def mute_engine(event):
    paths = get_group_paths(event.chat_id)
    if paths and os.path.exists(paths["mute"]):
        with open(paths["mute"], "r") as f:
            if str(event.sender_id) in json.load(f):
                await event.delete()
