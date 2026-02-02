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
# أمر التنزيل الشامل (.تنزيل بالرد)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنزيل$"))
async def demote_user(event):
    if not event.is_group: return
    
    paths = get_group_paths(event.chat_id)
    if not paths: return
    
    # 1. التحقق من المالك (فقط المالك ينزل)
    with open(paths["owner"], "r", encoding="utf-8") as f:
        if json.load(f).get("id") != event.sender_id: return

    # 2. التأكد من وجود رد
    if not event.is_reply:
        return await event.edit("⚠️ **يرجى الرد على الشخص لتنزيله!**")

    reply_msg = await event.get_reply_message()
    user_id = reply_msg.sender_id
    u_id_str = str(user_id)

    # 3. تحميل بيانات الرتب
    if not os.path.exists(paths["ranks"]):
        return await event.edit("⚠️ **لا توجد رتب مسجلة في هذه المجموعة!**")

    with open(paths["ranks"], "r", encoding="utf-8") as f:
        ranks_data = json.load(f)

    # 4. التحقق إذا كان الشخص يملك رتبة أصلاً
    if u_id_str not in ranks_data:
        return await event.edit("⚠️ **هذا الشخص لا يملك أي رتبة في المملكة!**")

    old_rank = ranks_data[u_id_str]["rank"]
    user_ent = await client.get_entity(user_id)
    name = user_ent.first_name or "المستخدم"

    # 5. دوامة الفورتكس (تنزيل)
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري تنزيل {name} من رتبة {old_rank} 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    # 6. حذف البيانات من الملف
    del ranks_data[u_id_str]
    with open(paths["ranks"], "w", encoding="utf-8") as f:
        json.dump(ranks_data, f, indent=4, ensure_ascii=False)

    # 7. إزالة اللقب والصلاحيات من المجموعة (إذا كان مشرفاً)
    try:
        await client(functions.channels.EditAdminRequest(
            event.chat_id, user_id,
            types.ChatAdminRights(post_messages=False),
            rank="" # تصفير اللقب
        ))
    except: pass

    # 8. الكليشة النهائية (تنسيق عراق ثون)
    res = (
        "★────────☭────────★\n"
        "   ☭ • 𝑫𝑬𝑴𝑶𝑻𝑬 𝑫𝑶𝑵𝑬 • ☭\n"
        "★────────☭────────★\n\n"
        f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
        f"• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **تم تنزيله من رتبة {old_rank}** ✅\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )
    await event.edit(res)
