import __main__, os, json, asyncio
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
BASE_DIR = "group"

# --- دالة جلب مسار ملف المالك للتحقق ---
def get_owner_id(chat_id):
    if not os.path.exists(BASE_DIR): return None
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            owner_path = os.path.join(BASE_DIR, folder, "owner.json")
            if os.path.exists(owner_path):
                with open(owner_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("id")
    return None

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كشف$"))
async def detect_user(event):
    if not event.is_group: return
    
    # 1. التحقق: هل المستخدم هو المالك المسجل في ملف المجموعه؟
    owner_id = get_owner_id(event.chat_id)
    if not owner_id or event.sender_id != owner_id:
        return # لا يستجيب لغير المالك

    if not event.is_reply:
        # إصلاح خطأ التعديل: نتحقق إذا كان النص سيختلف فعلياً
        msg_text = "⚠️ يرجى الرد على الشخص لكشف حسابه!"
        if event.raw_text != msg_text:
            return await event.edit(msg_text)
        return

    reply_msg = await event.get_reply_message()
    user_id = reply_msg.sender_id
    
    try:
        # جلب البيانات
        user = await client.get_entity(user_id)
        full_user = await client(functions.users.GetFullUserRequest(user.id))
        
        # جلب الرتبة
        p = await client.get_permissions(event.chat_id, user.id)
        rank = "المنشئ" if p.is_creator else "مشرف" if p.is_admin else "عضو"

        # جلب تاريخ الانضمام
        join_date = user.date.strftime("%Y/%m/%d") if hasattr(user, 'date') and user.date else "غير معروف"

        # حساب عدد الرسائل
        search_result = await client(functions.messages.SearchRequest(
            peer=event.chat_id, q='', filter=types.InputMessagesFilterEmpty(),
            min_date=None, max_date=None, offset_id=0, add_offset=0, limit=1,
            max_id=0, min_id=0, from_id=user.id, hash=0
        ))
        count_msg = getattr(search_result, 'count', 0)

        # التنسيق النهائي
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

        # منع خطأ EditMessageRequest عن طريق محاولة التعديل والقبول بأي خطأ بسيط
        try:
            await event.edit(final_text, link_preview=False)
        except Exception:
            # إذا فشل التعديل (بسبب تشابه النص)، نرسل رسالة جديدة ونحذف القديمة
            await event.delete()
            await event.respond(final_text, link_preview=False)

    except Exception as e:
        print(f"Error in Detect: {e}")
