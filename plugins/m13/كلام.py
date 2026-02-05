import __main__
from telethon import events
import asyncio
from g4f.client import Client

client = __main__.client
ai_client = Client()

# حالة الميزة
if not hasattr(__main__, 'fix_mode'):
    __main__.fix_mode = True

@client.on(events.NewMessage(outgoing=True))
async def silent_corrector(event):
    # إذا الميزة معطلة أو الرسالة أمر (تبدأ بنقطة) لا تدخل
    if not __main__.fix_mode or event.text.startswith("."):
        return

    original_text = event.text
    if not original_text or len(original_text) < 2:
        return

    try:
        # نطلب من الذكاء الاصطناعي يعطينا الجملة الصحيحة فقططط بدون أي حرف زايد
        response = ai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "أنت مصحح إملائي صامت. وظيفتك هي إعادة صياغة الجملة العربية المليئة بالأخطاء (البدليات) إلى جملة صحيحة. أرسل الجملة المصححة فقط بدون أي تعليق أو مقدمات. إذا كانت الجملة صحيحة أصلاً، أرسل نفس الجملة."},
                {"role": "user", "content": original_text}
            ]
        )
        
        corrected_text = response.choices[0].message.content.strip()

        # إذا لقى خطأ وعدله، يسوي تعديل للرسالة فوراً
        if corrected_text != original_text:
            await event.edit(corrected_text)
            
    except:
        pass # إذا صار خطأ بالاتصال يسكت وما يسوي شي

# أوامر التحكم (تقدر تمسحها إذا تريدها تشتغل دوم)
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(تفعيل|تعطيل) التصحيح$"))
async def toggle_fix(event):
    __main__.fix_mode = True if "تفعيل" in event.text else False
    status = "شغال ✅" if __main__.fix_mode else "معطل ❌"
    await event.edit(f"⚙️ **مصحح البدليات التلقائي:** {status}")
    await asyncio.sleep(2)
    await event.delete()
