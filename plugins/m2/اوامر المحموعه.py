import __main__, asyncio, os
from telethon import events

# استخراج الكلاينت من الملف الرئيسي
client = getattr(__main__, 'client', None)

# الدوامات (الزخرفة)
VORTEX = ["◜", "◝", "◞", "◟"]
BASE_DIR = "group"

# التأكد من وجود المجلد الرئيسي
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل مجموعه$"))
async def enable_group(event):
    # التأكد أن الأمر داخل مجموعة حصراً
    if not event.is_group:
        return 

    # 1. الدوامة: جاري تفعيل مجموعتك
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري تفعيل مجموعتك 〕 {f} ⌯")
        await asyncio.sleep(0.2)

    # 2. إنشاء المجلد (باسم المجموعة + الآيدي)
    chat = await event.get_chat()
    title = chat.title if chat.title else "Group"
    # تنظيف الاسم من الرموز الممنوعة في الوندوز/لينكس
    safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '_')]).rstrip()
    folder_name = f"{safe_title}_{event.chat_id}"
    
    group_path = os.path.join(BASE_DIR, folder_name)
    
    if not os.path.exists(group_path):
        os.makedirs(group_path)

    # 3. الدوامة: تم تفعيل مجموعتك
    await event.edit(f"⌯ {VORTEX[0]} 〔 تم تفعيل مجموعتك بنجاح 〕 {VORTEX[0]} ⌯")
    
    # حذف الرسالة بعد 10 ثواني (اختياري حسب رغبتك السابقة)
    await asyncio.sleep(10)
    await event.delete()
