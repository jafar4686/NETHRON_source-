import __main__, asyncio, json, os
from telethon import events, functions, types

client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]
BASE_DIR = "group"

def get_folder_name(title, chat_id):
    # تنظيف الاسم ليكون صالحاً للمجلدات
    safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '_')]).strip()
    return f"{safe_title}_{chat_id}"

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل مجموعه$"))
async def enable_group(event):
    if not event.is_group:
        return

    # التحقق: هل أنت منشئ المجموعة؟
    permissions = await client.get_permissions(event.chat_id, event.sender_id)
    if not permissions.is_creator:
        return await event.edit("⚠️ **عذراً، هذا الأمر مخصص لمنشئ المجموعة فقط!**")

    # 1. الدوامة البصرية
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري تفعيل مجموعتك 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    # 2. جلب معلومات الحساب والكروب
    me = await client.get_me()
    full_user = await client(functions.users.GetFullUserRequest(me.id))
    chat = await event.get_chat()
    
    # جلب عدد الأعضاء الفعلي
    participants = await client.get_participants(event.chat_id, limit=0)
    number_mep = participants.total

    # 3. إنشاء الهيكلية وحفظ ملف المالك
    folder_name = get_folder_name(chat.title, event.chat_id)
    group_path = os.path.join(BASE_DIR, folder_name)
    if not os.path.exists(group_path):
        os.makedirs(group_path)

    owner_data = {
        "name": me.first_name,
        "id": me.id,
        "rank": "المالك الأساسي",
        "user": "@NETH_RON",
        "bio": full_user.full_user.about or "لا يوجد"
    }
    
    # حفظ الملف داخل المجلد الجديد
    with open(os.path.join(group_path, "owner.json"), "w", encoding="utf-8") as f:
        json.dump(owner_data, f, indent=4, ensure_ascii=False)

    # 4. رسالة التفعيل الفخمة مع حقوقك
    final_text = (
        "★────────☭────────★\n"
        "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
        "★────────☭────────★\n\n"
        "• ⌯ 𝑫𝒐𝒏𝒆 𝑨𝒄𝒕𝒊𝒗𝒆 𝑮𝒓𝒐𝒖𝒑 ✔\n"
        f"• 𝑵𝒂𝒎𝒆 ⌯ {chat.title}\n"
        f"• 𝑶𝒘𝒏𝒆𝒓 ⌯ {me.first_name}\n"
        f"• 𝑩𝒊𝒐 ⌯ {owner_data['bio']}\n"
        f"• 𝑵𝒖𝒎𝒃𝒆𝒓 𝑴𝒆𝒎𝒃𝒆𝒓𝒔 ⌯ {number_mep}\n\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
    )

    await event.edit(final_text, link_preview=False)
