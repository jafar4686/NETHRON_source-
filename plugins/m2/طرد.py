import __main__, os, asyncio, json
from telethon import events, functions, types

# استخراج الكلاينت بنفس طريقتك الأصلية
client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# دالة التأكد من المالك
def get_owner_only(chat_id):
    if not os.path.exists(BASE_DIR): return None
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            owner_path = os.path.join(BASE_DIR, folder, "owner.json")
            if os.path.exists(owner_path):
                with open(owner_path, "r", encoding="utf-8") as f:
                    return json.load(f).get("id")
    return None

# ==========================================
# 7. أمر الطرد (.طرد بالرد)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.طرد$"))
async def kick_user(event):
    if not event.is_group: return
    
    # 1. التحقق من المالك
    owner_id = get_owner_only(event.chat_id)
    if not owner_id or event.sender_id != owner_id:
        return 

    # 2. التأكد من وجود رد
    if not event.is_reply:
        return await event.edit("⚠️ **يرجى الرد على الشخص لطرده من المملكة!**")

    reply_msg = await event.get_reply_message()
    user_id = reply_msg.sender_id
    
    # منع طرد النفس
    if user_id == event.sender_id:
        return await event.edit("⚠️ **لا يمكنك طرد نفسك يا ملك!**")

    try:
        # حركات التحميل
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري استبعاد الشخص من المملكة 〕 {f} ⌯")
            await asyncio.sleep(0.1)

        # تنفيذ عملية الطرد (KICK)
        # ملاحظة: في تليجرام الطرد هو تقييد الشخص من الدخول مرة أخرى ثم فك التقييد
        await client.kick_participant(event.chat_id, user_id)
        
        # جلب معلومات المطرود للجمالية
        user = await client.get_entity(user_id)
        name = user.first_name if user.first_name else "المستخدم"
        
        final_text = (
            "★────────☭────────★\n"
            "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑼𝒔𝒆𝒓 ⌯ {name}\n"
            f"• 𝑰𝒅 ⌯ `{user_id}`\n"
            "• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **تم الطرد بنجاح** ✅\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )
        await event.edit(final_text)

    except Exception as e:
        await event.edit(f"⚠️ **فشل الطرد:**\n`{str(e)}` \n(تأكد أن السورس يمتلك صلاحيات المشرف)")
