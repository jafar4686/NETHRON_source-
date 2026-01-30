import __main__, os, json
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
BASE_DIR = "group"

# دالة جلب آيدي المالك من الملف للتحقق
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
    
    # 1. قفل المالك: التحقق من ملف المجموعة
    owner_id = get_owner_id(event.chat_id)
    if not owner_id or event.sender_id != owner_id:
        return 

    if not event.is_reply:
        return await event.edit("⚠️ **يرجى الرد على الشخص لكشف حسابه!**")

    reply_msg = await event.get_reply_message()
    user_id = reply_msg.sender_id
    
    # رسالة مؤقتة لأن الحساب الدقيق قد يأخذ ثانية
    await event.edit("⌯ 〔 جاري جمع معلومات الحساب... 〕 ⌯")

    try:
        # جلب الكيان الكامل والبايو
        user = await client.get_entity(user_id)
        full_user = await client(functions.users.GetFullUserRequest(user.id))
        
        # جلب الرتبة
        p = await client.get_permissions(event.chat_id, user.id)
        rank = "المنشئ" if p.is_creator else "مشرف" if p.is_admin else "عضو"

        # جلب تاريخ الانضمام (من بيانات الحساب)
        join_date = user.date.strftime("%Y/%m/%d") if hasattr(user, 'date') and user.date else "غير معروف"

        # --- الطريقة الاحترافية لحساب الرسائل (تراكمي) ---
        # نقوم بطلب البحث عن كافة رسائل المستخدم في هذا الدردشة
        msgs = await client(functions.messages.SearchRequest(
            peer=event.chat_id,
            q='', # بحث عن كل شيء
            filter=types.InputMessagesFilterEmpty(),
            min_date=None,
            max_date=None,
            offset_id=0,
            add_offset=0,
            limit=1, # نطلب رسالة واحدة لكن الـ API سيرجع العدد الكلي في حقل count
            max_id=0,
            min_id=0,
            from_id=user.id,
            hash=0
        ))
        # هنا التعديل: نستخدم .count لضمان جلب العدد الكامل من سيرفرات تليجرام
        count_msg = msgs.count if hasattr(msgs, 'count') else 0

        # التنسيق النهائي
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

        # تعديل الرسالة مع تجنب خطأ عدم التغيير
        try:
            await event.edit(final_text, link_preview=False)
        except:
            await event.delete()
            await event.respond(final_text, link_preview=False)

    except Exception as e:
        await event.edit(f"⚠️ **خطأ تقني:**\n`{str(e)}`")
