import __main__, asyncio
from telethon import events

# استخراج الكلاينت
client = getattr(__main__, 'client', None)

# مصفوفة الدوامة للتنسيق
VORTEX = ["◜", "◝", "◞", "◟"]

# الأمر يبدأ بـ $نسخ
@client.on(events.NewMessage(outgoing=True, pattern=r"^\$نسخ(?:\s+(.*))?$"))
async def copy_text_maker(event):
    # جلب النص سواء كان بجانب الأمر أو بالرد
    input_text = event.pattern_match.group(1)
    
    # إذا كان الأمر بالرد على رسالة
    if event.is_reply and not input_text:
        reply_msg = await event.get_reply_message()
        input_text = reply_msg.text

    if not input_text:
        return await event.edit("⚠️ **يرجى كتابة نص بعد $نسخ أو الرد على رسالة!**")

    # حركات الدوامة قبل التعديل
    for f in VORTEX:
        await event.edit(f"⌯ {f} جاري تنسيق النص {f} ⌯")
        await asyncio.sleep(0.05)

    # التنسيق الملكي
    # الرمز ` يخلي النص ينسخ بضغطة وحدة بالتليجرام
    msg = (
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑪𝑶𝑷𝒀 • ☭\n"
        "★────────☭────────★\n\n"
        f" `{input_text}` \n\n"
        "• **اضغط على النص أعلاه لنسخه فوراً.**\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )
    
    await event.edit(msg)
