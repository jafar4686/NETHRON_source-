import __main__, os
from telethon import events

# جلب الكلاينت المحقون من الميكر
client = getattr(__main__, 'client', None)

# مسار الصورة اللي صممناها
IMG_PATH = "assets/TIME.jpg"

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م7$"))
async def menu7(event):
    klisha = (
        "★────────☭────────★\n"
        "   ☭ • 𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 • ☭\n"
        "                  ☭ • سورس نيثرون • ☭\n"
        "★────────☭────────★\n\n"
        "⚙️ أوامر الوقتي والتحكم:\n\n"
        "• .وقتي اسم\n"
        "➥ لتفعيل الوقت بتوقيت العراق في اسمك\n\n"
        "• .وقتي بايو\n"
        "➥ لتفعيل الوقت بتوقيت العراق في بايوك\n\n"
        "• .ايقاف وقتي\n"
        "➥ لإيقاف الوقت وتنظيف الحساب فوراً\n\n"
        "★────────☭────────★\n"
        "💬 ملاحظة: تم البرمجة بواسطة نيثرون"
    )

    # فحص إذا الصورة موجودة بالمجلد
    if os.path.exists(IMG_PATH):
        # يحذف الأمر (.م7) ويرسل الصورة مع الكليشة
        await event.delete()
        await client.send_file(event.chat_id, IMG_PATH, caption=klisha)
    else:
        # إذا الصورة مو موجودة، يعدل الرسالة فقط حتى ما يعلق السورس
        await event.edit(klisha + "\n\n⚠️ تنبيه: صورة TIME.jpg غير موجودة في مجلد assets")
