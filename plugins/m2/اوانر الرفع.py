import __main__, os, asyncio, json, re
from telethon import events, functions, types

# استخراج الكلاينت والمسارات
client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# --- دالة إدارة المسارات ---
def get_rank_paths(chat_id):
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return {
                "ranks": os.path.join(gp, "member_rank.json"),
                "owner": os.path.join(gp, "owner.json")
            }
    return None

# دالة جلب ID المستخدم (رد، يوزر، ايدي)
async def get_user_id(event, args):
    if event.is_reply:
        return (await event.get_reply_message()).sender_id
    if args:
        try:
            user = await client.get_entity(args[0])
            return user.id
        except: return None
    return None

# ==========================================
# أمر الرفع (.رفع مميز / .رفع ادمن)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.رفع (مميز|ادمن)(?:\s+(.*))?$"))
async def promote_user(event):
    if not event.is_group: return
    
    paths = get_rank_paths(event.chat_id)
    if not paths: return await event.edit("⚠️ **المجموعة غير مفعلة!**")
    
    # التأكد من المالك
    with open(paths["owner"], "r", encoding="utf-8") as f:
        if json.load(f).get("id") != event.sender_id: return

    rank_type = event.pattern_match.group(1)
    args = event.pattern_match.group(2).split() if event.pattern_match.group(2) else []
    
    user_id = await get_user_id(event, args)
    if not user_id: return await event.edit("⚠️ **رد على الشخص او ارسل يوزره/ايديه!**")

    try:
        user_ent = await client.get_entity(user_id)
        name = user_ent.first_name or "المستخدم"
        u_id_str = str(user_id)

        # تحميل أو إنشاء ملف الرتب
        ranks_data = {}
        if os.path.exists(paths["ranks"]):
            with open(paths["ranks"], "r", encoding="utf-8") as f:
                ranks_data = json.load(f)

        # تخزين البيانات بالتنسيق اللي ردته: الاسم | الرتبة | الايدي
        ranks_data[u_id_str] = {
            "name": name,
            "rank": rank_type,
            "id": user_id,
            "full_info": f"{name} | {rank_type} | {user_id}"
        }

        with open(paths["ranks"], "w", encoding="utf-8") as f:
            json.dump(ranks_data, f, indent=4, ensure_ascii=False)

        # حركات الفورتكس
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري رفع {name} رتبة {rank_type} 〕 {f} ⌯")
            await asyncio.sleep(0.1)

        # إذا كان الرفع "ادمن" نغير لقبه بالتليجرام
        if rank_type == "ادمن":
            try:
                await client(functions.channels.EditAdminRequest(
                    event.chat_id, user_id,
                    types.ChatAdminRights(post_messages=True, add_admins=False, invite_users=True, ban_users=True, delete_messages=True, pin_messages=True),
                    rank="ادمن" # اللقب المخصص
                ))
            except: pass

        await event.edit(f"✅ **تم رفع:** {name}\n👑 **الرتبة:** `{rank_type}`\n📂 **تم الحفظ في:** `member_rank.json`")

    except Exception as e:
        await event.edit(f"❌ **خطأ:** `{str(e)}`")

# ==========================================
# أمر التنزيل (.تنزيل مميز / .تنزيل ادمن)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنزيل (مميز|ادمن)(?:\s+(.*))?$"))
async def demote_user(event):
    if not event.is_group: return
    paths = get_rank_paths(event.chat_id)
    with open(paths["owner"], "r", encoding="utf-8") as f:
        if json.load(f).get("id") != event.sender_id: return

    rank_type = event.pattern_match.group(1)
    args = event.pattern_match.group(2).split() if event.pattern_match.group(2) else []
    user_id = await get_user_id(event, args)
    
    if not user_id or not os.path.exists(paths["ranks"]): return

    with open(paths["ranks"], "r", encoding="utf-8") as f:
        ranks_data = json.load(f)

    u_id_str = str(user_id)
    if u_id_str in ranks_data and ranks_data[u_id_str]["rank"] == rank_type:
        del ranks_data[u_id_str]
        with open(paths["ranks"], "w", encoding="utf-8") as f:
            json.dump(ranks_data, f, indent=4, ensure_ascii=False)
        
        # إذا نزلنا ادمن نشيل اللقب
        if rank_type == "ادمن":
            try: await client(functions.channels.EditAdminRequest(event.chat_id, user_id, types.ChatAdminRights(post_messages=False), rank=""))
            except: pass
            
        await event.edit(f"✅ **تم تنزيل المستخدم من رتبة {rank_type} بنجاح.**")
    else:
        await event.edit(f"⚠️ **هذا المستخدم ليس {rank_type} أصلاً!**")
