import __main__, os
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كشف$"))
async def detect_user(event):
    if not event.is_group: 
        return await event.edit("⚠️ الأمر للمجموعات فقط.")
    if not event.is_reply:
        return await event.edit("⚠️ يرجى الرد على الشخص لكشف حسابه!")

    # جلب معلومات الشخص المردود عليه
    reply_msg = await event.get_reply_message()
    user_id = reply_msg.sender_id
    
    try:
        # جلب الكيان الكامل للشخص والبايو
        user = await client.get_entity(user_id)
        full_user = await client(functions.users.GetFullUserRequest(user.id))
        
        # 1. جلب الرتبة (Rank)
        p = await client.get_permissions(event.chat_id, user.id)
        if p.is_creator:
            rank = "المنشئ"
        elif p.is_admin:
            rank = "مشرف"
        else:
            rank = "عضو"

        # 2. جلب تاريخ الانضمام (Join Date)
        # ملاحظة: تاريخ الانضمام الدقيق يحتاج صلاحيات مشرف، سنستخدم تاريخ أول ظهور بالحساب كبديل
        join_date = user.date.strftime("%Y/%m/%d") if hasattr(user, 'date') and user.date else "غير معروف"

        # 3. حساب عدد الرسائل (Message Count) بطريقة مضمونة
        search_result = await client(functions.messages.SearchRequest(
            peer=event.chat_id,
            q='',
            filter=types.InputMessagesFilterEmpty(),
            min_date=None,
            max_date=None,
            offset_id=0,
            add_offset=0,
            limit=1, # نحتاج العدد فقط
            max_id=0,
            min_id=0,
            from_id=user.id,
            hash=0
        ))
        # استخدام hasattr للتأكد من وجود القيمة وتجنب الخطأ السابق
        count_msg = getattr(search_result, 'count', 0)

        # 4. التنسيق الفخم كما طلبته
        name = user.first_name if user.first_name else "لا يوجد"
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
        await event.edit(f"⚠️ **حدث خطأ أثناء الكشف:**\n`{str(e)}`")
