import __main__, os, asyncio, json
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# دالة التأكد من المالك (نفس اللي تستخدمها بملفاتك)
def get_owner_only(chat_id):
    if not os.path.exists(BASE_DIR): return None
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            owner_path = os.path.join(BASE_DIR, folder, "owner.json")
            if os.path.exists(owner_path):
                with open(owner_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("id")
    return None

# ==========================================
# 7. أمر الطرد المعدل (الشغال 100%)
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
        return await event.edit("⚠️ **يرجى الرد على الشخص لطرده!**")

    # جلب الرسالة المردود عليها
    reply_msg = await event.get_reply_message()
    user_id = reply_msg.sender_id
    
    if user_id == event.sender_id:
        return await event.edit("⚠️ **ما تكدر تطرد نفسك يا ملك!**")

    await event.edit("⌯ 〔 جاري معالجة الطلب... 〕 ⌯")

    try:
        # جلب بيانات المستخدم كاملة قبل الطرد لضمان التنفيذ
        user_entity = await client.get_entity(user_id)
        
        # حركات الفورتكس
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري استبعاد الشخص من المملكة 〕 {f} ⌯")
            await asyncio.sleep(0.1)

        # تنفيذ الطرد
        await client.kick_participant(event.chat_id, user_id)
        
        # التنسيق النهائي
        name = user_entity.first_name or "المستخدم"
        final_text = (
            "★────────☭────────★\n"
            "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
            f"• 𝑰𝒅 ⌯ `{user_id}`\n"
            "• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **تم الطرد بنجاح** ✅\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )
        await event.edit(final_text)

    except Exception as e:
        # إذا فشل بسبب الصلاحيات أو غيرها
        await event.edit(f"⚠️ **فشل الطرد:**\n`{str(e)}` \n\nتأكد أنك مشرف وتمتلك صلاحية (حظر المستخدمين).")
