import __main__, os, json, asyncio
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
BASE_DIR = "group"

# --- دالة جلب المسارات ---
def get_group_paths(chat_id):
    if not os.path.exists(BASE_DIR): return None
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return {
                "owner": os.path.join(gp, "owner.json"),
                "ranks": os.path.join(gp, "member_rank.json"),
                "stats": os.path.join(gp, "stats.json")
            }
    return None

# ==========================================
# أمر التفاعلي الشخصي (.تفاعلي)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفاعلي$"))
async def interactive_info(event):
    if not event.is_group: return
    
    paths = get_group_paths(event.chat_id)
    if not paths: return

    try:
        user_id = event.sender_id
        # جلب معلوماتك الكاملة
        me = await client.get_me()
        full_user = await client(functions.users.GetFullUserRequest(user_id))
        
        # 1. تحديد الرتبة من الملفات
        rank_name = "عضو"
        # فحص إذا كنت أنت المالك
        if os.path.exists(paths["owner"]):
            with open(paths["owner"], "r", encoding="utf-8") as f:
                if json.load(f).get("id") == user_id:
                    rank_name = "المالك"

        # إذا مو مالك، يشوف رتبتك المسجلة بالملف
        if rank_name == "عضو" and os.path.exists(paths["ranks"]):
            with open(paths["ranks"], "r", encoding="utf-8") as f:
                ranks_data = json.load(f)
                if str(user_id) in ranks_data:
                    rank_name = ranks_data[str(user_id)]["rank"]

        # 2. جلب عدد الرسائل من stats.json
        count_msg = 0
        if os.path.exists(paths["stats"]):
            with open(paths["stats"], "r", encoding="utf-8") as f:
                stats_data = json.load(f)
                count_msg = stats_data.get(str(user_id), {}).get("count", 0)

        # 3. التنسيق النهائي بالكليشة الأصلية
        name = me.first_name or "لا يوجد"
        username = f"@{me.username}" if me.username else "لا يوجد"
        bio = full_user.full_user.about or "لا يوجد بايو"
        
        final_text = (
            "★────────☭────────★\n"
            "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
            "★────────☭────────★\n\n"
            "• ⌯\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
            f"• 𝑼𝒔𝒆𝒓 ⌯ {username}\n"
            f"• 𝑩𝒊𝒐 ⌯ {bio}\n"
            f"• 𝑴𝒂𝒔𝒔𝒆𝒈𝒆 ⌯ {count_msg}\n"
            f"• 𝑹𝒂𝒏𝒌 ⌯ {rank_name}\n"
            "• ⌯\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )

        await event.edit(final_text, link_preview=False)

    except Exception as e:
        print(f"Error in interactive: {e}")
