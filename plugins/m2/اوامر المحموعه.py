import __main__, asyncio, json, os
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]
BASE_DIR = "group"

# دالة لتجهيز اسم مجلد آمن
def get_folder_name(title, chat_id):
    safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '_')]).strip()
    return f"{safe_title}_{chat_id}"

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل مجموعه$"))
async def enable_group(event):
    if not event.is_group:
        return

    # --- التحقق: هل المستخدم هو مالك (منشئ) المجموعة؟ ---
    permissions = await client.get_permissions(event.chat_id, event.sender_id)
    if not permissions.is_creator:
        return await event.edit("⚠️ **عذراً، هذا الأمر مخصص لمالك المجموعة (المنشئ) فقط!**")

    # 1. الدوامة الأولى
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري تفعيل مجموعتك 〕 {f} ⌯")
        await asyncio.sleep(0.2)

    # 2. جلب المعلومات وإنشاء المجلد
    me = await client.get_me()
    chat = await event.get_chat()
    folder_name = get_folder_name(chat.title, event.chat_id)
    group_path = os.path.join(BASE_DIR, folder_name)

    if not os.path.exists(group_path):
        os.makedirs(group_path)

    # 3. إنشاء ملف المالك owner.json مرتب
    owner_data = {
        "name": me.first_name,
        "id": me.id,
        "rank": "المالك الأساسي",
        "user": f"@{me.username}" if me.username else "لا يوجد"
    }
    
    owner_file = os.path.join(group_path, "owner.json")
    with open(owner_file, "w", encoding="utf-8") as f:
        json.dump(owner_data, f, indent=4, ensure_ascii=False)

    # 4. الدوامة الثانية (النجاح)
    await event.edit(f"⌯ {VORTEX[0]} 〔 تم تفعيل مجموعتك بنجاح 〕 {VORTEX[0]} ⌯")
    
    # حذف الرسالة ورا 10 ثواني
    await asyncio.sleep(10)
    await event.delete()
