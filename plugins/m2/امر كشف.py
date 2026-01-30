import __main__, os, json
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
BASE_DIR = "group"

# دالة لجلب المجلد (للتأكد من أن المجموعة مفعلة)
def get_group_folder(chat_id):
    if not os.path.exists(BASE_DIR): return None
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            return os.path.join(BASE_DIR, folder)
    return None

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كشف$"))
async def detect_user(event):
    if not event.is_group: return
    if not event.is_reply:
        return await event.edit("⚠️ **يرجى الرد على الشخص لكشف حسابه!**")

    # جلب معلومات الشخص المردود عليه
    reply_msg = await event.get_reply_message()
    user_id = reply_msg.sender_id
    
    try:
        user = await client.get_entity(user_id)
        full_user = await client(functions.users.GetFullUserRequest(user.id))
        
        # 1. جلب الرتبة من التليجرام مباشرة
        p = await client.get_permissions(event.chat_id, user.id)
        rank = "المنشئ" if p.is_creator else "مشرف" if p.is_admin else "عضو"

        # 2. جلب تاريخ الانضمام (تقريبي من بيانات الحساب)
        join_date = user.date.strftime("%Y/%m/%d") if hasattr(user, 'date') and user.date else "غير معروف"

        # 3. حساب عدد الرسائل في هذه المجموعة
        result = await client(functions.messages.SearchRequest(
            peer=event.chat_id, q='', filter=types.InputMessagesFilterEmpty(),
            min_date=None, max_date=None, offset_id=0, add_offset=0, limit=0, max_id=0, min_id=0,
            from_id=user.id, hash=0
        ))
        count_msg = result.total

        # 4. التنسيق النهائي
        name = user.first_name
        username = f"@{user.username}" if user.username else "لا يوجد"
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
            f"• 𝑹𝒂𝒏𝒌 ⌯ {rank}\n"
            f"• 𝑱𝒐𝒊𝒏 𝑫𝒂𝒕𝒆 ⌯ {join_date}\n"
            f"• 𝑰𝒅 ⌯ `{user.id}`\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )

        await event.edit(final_text, link_preview=False)

    except Exception as e:
        await event.edit(f"⚠️ **خطأ في جلب البيانات:**\n`{str(e)}`")
