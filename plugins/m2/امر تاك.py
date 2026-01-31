# ==========================================
# 6. أمر التاك الجماعي (إصدار المملكة المستقر)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تاك مجموعة$"))
async def mention_all(event):
    # التأكد أن الأمر في مجموعة
    if not event.is_group:
        return await event.edit("⚠️ **الأمر للمجموعات فقط!**")
    
    await event.edit("⌯ 〔 جاري جمع أعضاء المملكة.. 〕 ⌯")
    
    try:
        # جلب قائمة الأعضاء بالكامل
        all_participants = await client.get_participants(event.chat_id)
        members = [u for u in all_participants if not u.bot and not u.deleted]
        
        if not members:
            return await event.edit("⚠️ **لم أجد أعضاء للمنشن!**")
        
        await event.delete() # حذف رسالة البدء
        
        # تقسيم الأعضاء: 10 أشخاص بكل رسالة
        chunk_size = 10 
        for i in range(0, len(members), chunk_size):
            chunk = members[i:i + chunk_size]
            
            # بناء كليشة المنشن
            tag_text = "☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 𝑇𝐴𝐺 • ☭\n★────────☭────────★\n"
            for user in chunk:
                name = user.first_name if user.first_name else "عضو"
                # المنشن بالآيدي يضمن وصول الإشعار 100%
                tag_text += f"• ⌯ 〔 [{name}](tg://user?id={user.id}) 〕\n"
            
            tag_text += "★────────☭────────★"
            
            # إرسال المنشن
            await client.send_message(event.chat_id, tag_text)
            
            # وقت انتظار (2 ثانية) بين كل 10 أشخاص لحماية الحساب من الحظر
            await asyncio.sleep(2)
            
        await client.send_message(event.chat_id, "• ⌯ **اكتمل المنشن بنجاح!** ✔")

    except Exception as e:
        await client.send_message(event.chat_id, f"⚠️ **حدث خطأ:**\n`{str(e)}`")
