import __main__
from telethon import events
import asyncio
from g4f.client import Client # نستخدم الذكاء الاصطناعي للتصحيح الدقيق

client = __main__.client
ai_client = Client()

# إعدادات الميزة في الذاكرة
if not hasattr(__main__, 'autofix_status'):
    __main__.autofix_status = False

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل التصحيح$"))
async def enable_fix(e):
    __main__.autofix_status = True
    await e.edit("✅ **تم تفعيل مصحح الأخطاء الإملائية تلقائياً.**\nسيقوم السورس بتعديل بدلياتك فوراً!")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تعطيل التصحيح$"))
async def disable_fix(e):
    __main__.autofix_status = False
    await e.edit("❌ **تم تعطيل مصحح الأخطاء الإملائية.**")

# محرك التصحيح التلقائي
@client.on(events.NewMessage(outgoing=True))
async def corrector_handler(event):
    # لا يصحح الأوامر التي تبدأ بنقطة ولا يعمل إذا كانت الميزة معطلة
    if not __main__.autofix_status or event.text.startswith("."):
        return

    text = event.text
    # نتأكد أن النص طويل كفاية ليكون جملة (أكثر من كلمة واحدة)
    if len(text.split()) < 1:
        return

    try:
        # نرسل النص للذكاء الاصطناعي بطلب "تصحيح فقط" بدون كلام إضافي
        response = ai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "أنت مصحح لغوي سريع. إذا وجد خطأ إملائي في النص التالي، أرسل النص المصحح فقط بدون أي شرح. إذا كان النص صحيحاً، أرسل كلمة 'صحيح'."},
                      {"role": "user", "content": text}]
        )
        
        corrected_text = response.choices[0].message.content.strip()

        # إذا كان النص مختلفاً عن الأصلي وليس كلمة "صحيح"
        if corrected_text.lower() != "صحيح" and corrected_text != text:
            # نقوم بتعديل الرسالة الأصلية للنص الصحيح
            await event.edit(corrected_text)
            
    except Exception as e:
        print(f"خطأ في التصحيح: {e}")
