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
                "stats": os.path.join(gp, "stats.json"),
                "perms": os.path.join(gp, "permissions.json")
            }
    return None

# ==========================================
# 1. أمر التفاعلي الشخصي (.تفاعلي)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفاعلي$"))
async def interactive_info(event):
    if not event.is_group: return
    
    paths = get_group_paths(event.chat_id)
    if not paths: return

    user_id = event.sender_id
    
    # جلب الرتبة أولاً لفحص صلاحية "تفاعلي"
    rank_name = "عضو"
    if os.path.exists(paths["owner"]):
        with open(paths["owner"], "r", encoding="utf-8") as f:
            if json.load(f).get("id") == user_id: rank_name = "owner"
    
    if rank_name != "owner" and os.path.exists(paths["ranks"]):
        with open(paths["ranks"], "r", encoding="utf-8") as f:
            ranks_data = json.load(f)
            if str(user_id) in ranks_data:
                rank_name = ranks_data[str(user_id)]["rank"]

    # فحص هل رتبتك مسموح لها استخدام التفاعلي؟
    if rank_name != "owner" and os.path.exists(paths["perms"]):
        with open(paths["perms"], "r", encoding="utf-8") as f:
            perms = json.load(f)
            if not perms.get(rank_name, {}).get("تفاعلي", False):
                warn = await event.edit(f"⚠️ **رتبتك ({rank_name}) لا تملك صلاحية رؤية التفاعلي!**")
                await asyncio.sleep(10)
                return await warn.delete()

    try:
        # جلب البيانات التقنية
        full_user = await client(functions.users.GetFullUserRequest(user_id))
        me = await client.get_me()
        
        # جلب الإحصائيات
        count_msg = 0
        if os.path.exists(paths["stats"]):
            with open(paths["stats"], "r", encoding="utf-8") as f:
                stats_data = json.load(f)
                count_msg = stats_data.get(str(user_id), {}).get("count", 0)

        # التنسيق النهائي
        name = me.first_name or "لا يوجد"
        username = f"@{me.username}" if me.username else "لا يوجد"
        bio = full_user.full_user.about or "لا يوجد بايو"
        rank_display = "المالك" if rank_name == "owner" else rank_name

        final_text = (
            "★────────☭────────★\n"
            "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
            f"• 𝑼𝒔𝒆𝒓 ⌯ {username}\n"
            f"• 𝑩𝒊𝒐 ⌯ {bio}\n"
            f"• 𝑴𝒆𝒔𝒔𝒂𝒈𝒆𝒔 ⌯ {count_msg}\n"
            f"• 𝑹𝒂𝒏𝒌 ⌯ {rank_display}\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )
        await event.edit(final_text, link_preview=False)

    except Exception as e:
        await event.edit(f"⚠️ **خطأ في جلب البيانات:** `{str(e)}`")

# ==========================================
# 2. محرك الإحصائيات (تسجيل الرسائل)
# ==========================================
@client.on(events.NewMessage(incoming=False, outgoing=True))
async def stats_engine(event):
    if not event.is_group: return
    paths = get_group_paths(event.chat_id)
    if not paths: return

    user_id = str(event.sender_id)
    stats_data = {}
    
    if os.path.exists(paths["stats"]):
        with open(paths["stats"], "r", encoding="utf-8") as f:
            try: stats_data = json.load(f)
            except: stats_data = {}

    if user_id not in stats_data:
        stats_data[user_id] = {"count": 1}
    else:
        stats_data[user_id]["count"] += 1

    with open(paths["stats"], "w", encoding="utf-8") as f:
        json.dump(stats_data, f, indent=4, ensure_ascii=False)
