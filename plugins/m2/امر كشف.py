import __main__, os, json
from telethon import events, functions, types
from datetime import datetime

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
BASE_DIR = "group"

# --- دالة جلب مسار ملفات المجموعة ---
def get_group_folder(chat_id):
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            return os.path.join(BASE_DIR, folder)
    return None

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كشف$"))
async def detect_user(event):
    if not event.is_group or not event.is_reply:
        return await event.edit("⚠️ **يرجى الرد على رسالة الشخص لكشف حسابه!**")

    # جلب معلومات الشخص المردود عليه
    reply_msg = await event.get_reply_message()
    user = await client.get_entity(reply_msg.sender_id)
    full_user = await client(functions.users.GetFullUserRequest(user.id))
    
    # 1. جلب الرتبة
    permissions = await client.get_permissions(event.chat_id, user.id)
    if permissions.is_creator:
        rank = "المنشئ"
    elif permissions.is_admin:
        rank = "مشرف"
    else:
        rank = "عضو"

    # 2. جلب تاريخ الانضمام (تقريبي بناءً على أول ظهور أو بيانات التليجرام)
    join_date = "غير متاح"
    if hasattr(user, 'date'):
        join_date = user.date.strftime("%Y/%m/%d")

    # 3. جلب عدد الرسائل (من ملف المجموعة إذا كان مفعلاً)
    count_msg = 0
    folder = get_group_folder(event.chat_id)
    if folder:
        # هنا نفترض وجود ملف إحصائيات أو نقوم بعد رسائله في التليجرام فوراً
        result = await client(functions.messages.SearchRequest(
            peer=event.chat_id,
            q='',
            filter=types.InputMessagesFilterEmpty(),
            min_date=None, max_date=None, offset_id=0, add_offset=0, limit=0, max_id=0, min_id=0,
            from_id=user.id, hash=0
        ))
        count_msg = result.total

    # 4. بناء رسالة الكشف الفخمة
    name = user.first_name
    username = f"@{user.username}" if user.username else "لا يوجد"
    bio = full_user.full_user.about or "لا يوجد بايو"
    user_id = user.id
    
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
        f"• 𝑰𝒅 ⌯ `{user_id}`\n\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
    )

    # إرسال الصورة الشخصية مع الكشف
    photo = await client.download_profile_photo(user.id)
    if photo:
        await client.send_file(event.chat_id, photo, caption=final_text)
        await event.delete()
    else:
        await event.edit(final_text, link_preview=False)
