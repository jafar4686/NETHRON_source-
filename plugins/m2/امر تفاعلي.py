import __main__, os, json, asyncio
from telethon import events, functions, types

client = getattr(__main__, 'client', None)
BASE_DIR = "group"

# --- دالة جلب المسارات وفحص الصلاحية ---
def get_group_paths(chat_id):
    if not os.path.exists(BASE_DIR): return None
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return {
                "owner": os.path.join(gp, "owner.json"),
                "ranks": os.path.join(gp, "member_rank.json"),
                "perms": os.path.join(gp, "permissions.json"),
                "stats": os.path.join(gp, "stats.json")
            }
    return None

async def can_use_interactive(event, paths):
    uid = event.sender_id
    # 1. المالك (دائماً مسموح)
    if os.path.exists(paths["owner"]):
        with open(paths["owner"], "r", encoding="utf-8") as f:
            if json.load(f).get("id") == uid: return "المالك"
            
    # 2. فحص الرتب من ملف member_rank والصلاحيات
    if os.path.exists(paths["ranks"]):
        with open(paths["ranks"], "r", encoding="utf-8") as f:
            ranks_data = json.load(f)
            if str(uid) in ranks_data:
                u_rank = ranks_data[str(uid)]["rank"]
                # التأكد من تفعيل صلاحية "تفاعلي" لهذه الرتبة
                if os.path.exists(paths["perms"]):
                    with open(paths["perms"], "r", encoding="utf-8") as f:
                        perms = json.load(f)
                        if perms.get(u_rank, {}).get("تفاعلي", False):
                            return u_rank
    return None

# ==========================================
# أمر التفاعلي العام للرتب (.تفاعلي)
# ==========================================
@client.on(events.NewMessage(pattern=r"^\.تفاعلي$"))
async def interactive_info(event):
    if not event.is_group: return
    
    paths = get_group_paths(event.chat_id)
    if not paths: return

    # التحقق من الصلاحية (هل الشخص رتبة ومفعل له التفاعلي؟)
    rank_name = await can_use_interactive(event, paths)
    if not rank_name:
        return # لا يستجيب للأعضاء العاديين أو الرتب غير المفعلة

    try:
        user_id = event.sender_id
        user_ent = await client.get_entity(user_id)
        full_user = await client(functions.users.GetFullUserRequest(user_id))
        
        # جلب عدد الرسائل من stats.json
        count_msg = 0
        if os.path.exists(paths["stats"]):
            with open(paths["stats"], "r", encoding="utf-8") as f:
                stats_data = json.load(f)
                count_msg = stats_data.get(str(user_id), {}).get("count", 0)

        # التنسيق النهائي (عراق ثون ستايل)
        name = user_ent.first_name or "لا يوجد"
        username = f"@{user_ent.username}" if user_ent.username else "لا يوجد"
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

        await event.respond(final_text, link_preview=False)

    except Exception as e:
        print(f"Error in interactive: {e}")
