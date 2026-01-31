# ==========================================
# 6. أمر التاك الجماعي (للمنشن الشامل)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تاك مجموعة$"))
async def mention_all(event):
    if not event.is_group:
        return await event.edit("⚠️ **هذا الأمر يستخدم داخل المجموعات فقط!**")
    
    # التأكد من الصلاحيات (للمشرفين فقط أو المنشئ)
    p = await client.get_permissions(event.chat_id, event.sender_id)
    if not (p.is_admin or p.is_creator):
        return await event.edit("⚠️ **عذراً، هذا الأمر للمشرفين فقط!**")

    chat = await event.get_chat()
    await event.edit("⌯ 〔 جاري التحضير لمنشن المملكة 〕 ⌯")
    
    members = []
    async for user in client.iter_participants(event.chat_id):
        if not user.bot and not user.deleted:
            members.append(user)

    if not members:
        return await event.edit("⚠️ **لم يتم العثور على أعضاء!**")

    await event.delete() # حذف رسالة التحضير لبدء التاك
    
    # تقسيم الأعضاء إلى دفعات (كل دفعة 5 أشخاص) لمنع الحظر
    chunk_size = 5
    for i in range(0, len(members), chunk_size):
        chunk = members[i:i + chunk_size]
        tag_line = "☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n★────────☭────────★\n"
        
        for user in chunk:
            # منشن مخفي بالمسافات أو بالاسم
            name = user.first_name if user.first_name else "Member"
            tag_line += f"• ⌯ 〔 [{name}](tg://user?id={user.id}) 〕\n"
        
        tag_line += "★────────☭────────★"
        
        # إرسال الدفعة
        await client.send_message(event.chat_id, tag_line)
        
        # تأخير بسيط (ثانية واحدة) بين كل دفعة ودفعة لتجنب السبام
        await asyncio.sleep(1.5)

    # رسالة اختيارية عند الانتهاء
    await client.send_message(event.chat_id, "• ⌯ **تم اكتمال منشن جميع أعضاء المملكة!** ✔")
