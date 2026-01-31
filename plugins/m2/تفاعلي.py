import __main__, os, json
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
BASE_DIR = "group"

# --- دالة جلب البيانات من الملفات المحلية ---
def get_group_info(chat_id):
    if not os.path.exists(BASE_DIR): return None
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            folder_path = os.path.join(BASE_DIR, folder)
            return {
                "owner_file": os.path.join(folder_path, "owner.json"),
                "stats_file": os.path.join(folder_path, "stats.json")
            }
    return None

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفاعلي$"))
async def interactive_info(event):
    if not event.is_group: return
    
    paths = get_group_info(event.chat_id)
    if not paths: return

    # 1. التحقق من المالك (فقط المالك المسجل في owner.json)
    if os.path.exists(paths["owner_file"]):
        with open(paths["owner_file"], "r", encoding="utf-8") as f:
            owner_data = json.load(f)
            if event.sender_id != owner_data.get("id"):
                return # لا يستجيب لغير المالك

    # 2. جلب معلومات المستخدم الحالي (أنت)
    try:
        me = await client.get_me()
        full_me = await client(functions.users.GetFullUserRequest(me.id))
        
        # جلب الرتبة من التليجرام مباشرة للتأكد
        p = await client.get_permissions(event.chat_id, me.id)
        rank = "المنشئ" if p.is_creator else "مشرف" if p.is_admin else "عضو"

        # 3. جلب عدد الرسائل من ملف stats.json (الدقة 100%)
        count_msg = 0
        if os.path.exists(paths["stats_file"]):
            with open(paths["stats_file"], "r", encoding="utf-8") as f:
                stats_data = json.load(f)
                user_stats = stats_data.get(str(me.id))
                if user_stats:
                    count_msg = user_stats.get("count", 0)

        # التنسيق النهائي بالكليشة المطلوبة
        name = me.first_name if me.first_name else "لا يوجد"
        user_link = f"@{me.username}" if me.username else "لا يوجد"
        bio = full_me.full_user.about if full_me.full_user.about else "لا يوجد بايو"
        
        final_text = (
            "★────────☭────────★\n"
            "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
            "★────────☭────────★\n\n"
            "• ⌯\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
            f"• 𝑼𝒔𝒆𝒓 ⌯ {user_link}\n"
            f"• 𝑩𝒊𝒐 ⌯ {bio}\n"
            f"• 𝑴𝒂𝒔𝒔𝒆𝒈𝒆 ⌯ {count_msg}\n"
            f"• 𝑹𝒂𝒏𝒌 ⌯ {rank}\n"
            "• ⌯\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )

        await event.edit(final_text, link_preview=False)

    except Exception as e:
        print(f"Error in interactive: {e}")
