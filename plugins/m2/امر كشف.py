import __main__, os, json
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
BASE_DIR = "group"

# دالة جلب مسار المجلد والبيانات
def get_group_data(chat_id):
    if not os.path.exists(BASE_DIR): return None, None
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            folder_path = os.path.join(BASE_DIR, folder)
            owner_path = os.path.join(folder_path, "owner.json")
            stats_path = os.path.join(folder_path, "stats.json")
            
            owner_id = None
            if os.path.exists(owner_path):
                with open(owner_path, "r", encoding="utf-8") as f:
                    owner_id = json.load(f).get("id")
            
            return owner_id, stats_path
    return None, None

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كشف$"))
async def detect_user(event):
    if not event.is_group: return
    
    # 1. التحقق من المالك وجلب مسار ملف الإحصائيات
    owner_id, stats_file = get_group_data(event.chat_id)
    
    if not owner_id or event.sender_id != owner_id:
        return 

    if not event.is_reply:
        return await event.edit("⚠️ **يرجى الرد على الشخص لكشف حسابه!**")

    reply_msg = await event.get_reply_message()
    user_id = reply_msg.sender_id
    
    await event.edit("⌯ 〔 جاري استخراج البيانات من سجلات المملكة... 〕 ⌯")

    try:
        # جلب معلومات الحساب
        user = await client.get_entity(user_id)
        full_user = await client(functions.users.GetFullUserRequest(user.id))
        
        # جلب الرتبة الحالية
        p = await client.get_permissions(event.chat_id, user.id)
        rank = "المنشئ" if p.is_creator else "مشرف" if p.is_admin else "عضو"

        # تاريخ الانضمام
        join_date = user.date.strftime("%Y/%m/%d") if hasattr(user, 'date') and user.date else "غير معروف"

        # --- السحب من stats.json لضمان دقة 100% ---
        count_msg = 0
        if stats_file and os.path.exists(stats_file):
            with open(stats_file, "r", encoding="utf-8") as f:
                try:
                    stats_data = json.load(f)
                    # البحث عن آيدي المستخدم داخل الملف
                    user_data = stats_data.get(str(user_id))
                    if user_data:
                        count_msg = user_data.get("count", 0)
                except:
                    count_msg = 0

        # التنسيق النهائي بالكليشة المطلوبة
        name = user.first_name if user.first_name else "بدون اسم"
        username = f"@{user.username}" if user.username else "لا يوجد"
        bio = full_user.full_user.about if full_user.full_user.about else "لا يوجد بايو"
        
        final_text = (
            "★────────☭────────★\n"
            "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
            "★────────☭────────★\n\n"
            "• ⌯\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
            f"• 𝑼𝒔𝒆𝒓 ⌯ {username}\n"
            f"• 𝑩𝒊𝒐 ⌯ {bio}\n"
            f"• 𝑴𝒂𝒔𝒔𝒆𝒈𝒆 ⌯ {count_msg}\n"
            f"• 𝑹𝒂𝒏𝒌 ⌯ {rank}\n"
            f"• 𝑱𝒐𝒊𝒏 𝑫𝒂𝒕𝒆 ⌯ {join_date}\n"
            f"• 𝑰𝒅 ⌯ `{user.id}`\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )

        await event.edit(final_text, link_preview=False)

    except Exception as e:
        await event.edit(f"⚠️ **فشل الكشف:**\n`{str(e)}`")
