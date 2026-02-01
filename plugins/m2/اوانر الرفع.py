import __main__, os, asyncio, json, re
from telethon import events, functions, types

# استخراج الكلاينت والمسارات
client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# --- دالات المساعدة لادارة الملفات ---
def get_rank_paths(chat_id):
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return {
                "owner": os.path.join(gp, "owner.json"),
                "vip": os.path.join(gp, "vip.json"), # للمميز
                "admins": os.path.join(gp, "admins_ranks.json") # للادمنية
            }
    return None

def is_owner(chat_id, sender_id):
    paths = get_rank_paths(chat_id)
    if paths and os.path.exists(paths["owner"]):
        with open(paths["owner"], "r", encoding="utf-8") as f:
            return json.load(f).get("id") == sender_id
    return False

# دالة لجلب ID المستخدم سواء رد او يوزر او ايدي
async def get_user_id(event, args):
    if event.is_reply:
        reply = await event.get_reply_message()
        return reply.sender_id
    if args:
        try:
            user = await client.get_entity(args[0])
            return user.id
        except: return None
    return None

# ==========================================
# 1. أوامر الرفع (.رفع مميز / .رفع ادمن)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.رفع (مميز|ادمن)(?:\s+(.*))?$"))
async def promote_user(event):
    if not event.is_group: return
    if not is_owner(event.chat_id, event.sender_id): return

    rank_type = event.pattern_match.group(1)
    args = event.pattern_match.group(2).split() if event.pattern_match.group(2) else []
    
    user_id = await get_user_id(event, args)
    if not user_id: return await event.edit("⚠️ **رد على الشخص او ارسل يوزره!**")

    paths = get_rank_paths(event.chat_id)
    file_key = "vip" if rank_type == "مميز" else "admins"
    file_path = paths[file_key]

    # تحميل البيانات الحالية
    data = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f: data = json.load(f)

    if user_id in data:
        return await event.edit(f"⚠️ **هذا الشخص مرفوع {rank_type} مسبقاً!**")

    # حركات الفورتكس
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري منحه رتبة {rank_type} 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    # إضافة الرتبة
    data.append(user_id)
    with open(file_path, "w", encoding="utf-8") as f: json.dump(data, f)

    # إذا كان الرفع "ادمن" نغير لقبه المخصص
    if rank_type == "ادمن":
        try:
            await client(functions.channels.EditAdminRequest(
                event.chat_id, user_id,
                types.ChatAdminRights(post_messages=True, add_admins=False, invite_users=True, change_info=False, ban_users=True, delete_messages=True, pin_messages=True),
                rank="ادمن المملكة"
            ))
        except: pass

    user_ent = await client.get_entity(user_id)
    await event.edit(f"✅ **المستخدم:** [{user_ent.first_name}](tg://user?id={user_id})\n👑 **تم رفعه بنجاح إلى رتبة:** `{rank_type}`")

# ==========================================
# 2. أوامر التنزيل (.تنزيل مميز / .تنزيل ادمن)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنزيل (مميز|ادمن)(?:\s+(.*))?$"))
async def demote_user(event):
    if not event.is_group: return
    if not is_owner(event.chat_id, event.sender_id): return

    rank_type = event.pattern_match.group(1)
    args = event.pattern_match.group(2).split() if event.pattern_match.group(2) else []
    
    user_id = await get_user_id(event, args)
    if not user_id: return await event.edit("⚠️ **حدد المستخدم المراد تنزيله!**")

    paths = get_rank_paths(event.chat_id)
    file_key = "vip" if rank_type == "مميز" else "admins"
    file_path = paths[file_key]

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f: data = json.load(f)
        if user_id in data:
            data.remove(user_id)
            with open(file_path, "w", encoding="utf-8") as f: json.dump(data, f)
            
            # إذا نزلنا ادمن، نشيل منه اللقب والصلاحيات
            if rank_type == "ادمن":
                try:
                    await client(functions.channels.EditAdminRequest(
                        event.chat_id, user_id,
                        types.ChatAdminRights(post_messages=False), rank=""
                    ))
                except: pass
                
            return await event.edit(f"✅ **تم تنزيل المستخدم من رتبة {rank_type}!**")
    
    await event.edit("⚠️ **هذا الشخص ليس لديه هذه الرتبة!**")
