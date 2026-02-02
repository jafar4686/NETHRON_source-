import __main__, os, asyncio, json
from telethon import events, functions, types

client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# --- دالة جلب المسارات ---
def get_group_paths(chat_id):
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return {
                "ranks": os.path.join(gp, "member_rank.json"),
                "owner": os.path.join(gp, "owner.json")
            }
    return None

# ==========================================
# أمر الرفع (تلقائياً يحذف القديم ويحط الجديد)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.رفع (مميز|ادمن|مدير|مطور)(?:\s+(.*))?$"))
async def promote_user(event):
    if not event.is_group: return
    paths = get_group_paths(event.chat_id)
    
    # التأكد أن المالك هو من يرفع
    with open(paths["owner"], "r", encoding="utf-8") as f:
        if json.load(f).get("id") != event.sender_id: return

    rank_type = event.pattern_match.group(1)
    
    # جلب ايدي الشخص (رد أو يوزر)
    if event.is_reply:
        user_id = (await event.get_reply_message()).sender_id
    else:
        # كود جلب الايدي من اليوزر هنا
        return await event.edit("⚠️ **رد على الشخص لرفعه!**")

    user_ent = await client.get_entity(user_id)
    name = user_ent.first_name or "المستخدم"
    u_id_str = str(user_id)

    # تحميل البيانات
    ranks_data = {}
    if os.path.exists(paths["ranks"]):
        with open(paths["ranks"], "r", encoding="utf-8") as f:
            ranks_data = json.load(f)

    # التحقق إذا كان عنده رتبة قديمة (لإزالتها ذهنياً وتحديثها)
    status_msg = f"ترقية لـ {rank_type}"
    if u_id_str in ranks_data:
        old_rank = ranks_data[u_id_str]["rank"]
        status_msg = f"تغيير من {old_rank} إلى {rank_type}"

    # دوامة التحميل
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري {status_msg} 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    # التحديث الفوري في الملف (يمسح القديم ويحط الجديد)
    ranks_data[u_id_str] = {
        "name": name,
        "rank": rank_type,
        "id": user_id
    }

    with open(paths["ranks"], "w", encoding="utf-8") as f:
        json.dump(ranks_data, f, indent=4, ensure_ascii=False)

    # تحديث اللقب في المجموعة (إذا كان البوت مشرف)
    try:
        await client(functions.channels.EditAdminRequest(
            event.chat_id, user_id,
            types.ChatAdminRights(post_messages=True, add_admins=False, invite_users=True, ban_users=True, delete_messages=True, pin_messages=True),
            rank=rank_type
        ))
    except: pass

    res = (
        "★────────☭────────★\n"
        "   ☭ • 𝑼𝑷𝑫𝑨𝑻𝑬 𝑹𝑨𝑵𝑲 • ☭\n"
        "★────────☭────────★\n\n"
        f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
        f"• 𝑵𝒆𝒘 𝑹𝒂𝒏𝒌 ⌯ **{rank_type}** ✅\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )
    await event.edit(res)
