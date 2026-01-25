import __main__
import asyncio
from telethon import events, Button

client = __main__.client

# بوت التحميل (تأكد انك مفعل /start وياه بالخاص)
# يفضل استخدام @SaveAsbot لأنه يدعم الصوت والفيديو
TARGET_BOT = "@C_5BOT"

@client.on(events.NewMessage(outgoing=True))
async def choice_dl(event):
    text = event.text
    if "youtube.com" in text or "youtu.be" in text or "tiktok.com" in text:
        # حفظ الرابط والدردشة الحالية
        event.chat_id
        
        # إظهار أزرار الاختيار
        buttons = [
            [Button.inline("🎬 تحميل فيديو", data=f"vid|{text}"),
             Button.inline("🎧 تحميل صوت", data=f"aud|{text}")]
        ]
        await event.edit("**📥 اختر نوع التحميل المطلوب:**", buttons=buttons)

@client.on(events.CallbackQuery(data=re.compile(b"vid||aud|")))
async def process_dl(event):
    data = event.data.decode('utf-8').split('|')
    type_dl = data[0]
    url = data[1]
    chat_id = event.chat_id
    
    await event.edit(f"🔄 **جاري المعالجة كـ {'فيديو' if type_dl == 'vid' else 'صوت'}...**")
    
    # 1. إرسال الرابط للبوت الخارجي
    # بعض البوتات تحتاج كلمة 'music' أو 'video' قبل الرابط، بس أغلبها تتعرف تلقائي
    sent_to_bot = await client.send_message(TARGET_BOT, url)
    
    # 2. مراقبة الرد
    @client.on(events.NewMessage(from_users=TARGET_BOT))
    async def catcher(reply):
        if reply.media:
            # إرسال الملف للشات الأصلي
            await client.send_file(chat_id, reply.media, caption="✅ **تم التحميل بواسطة سورس نيثرون**")
            
            # --- [ تنظيف الآثار فوراً ] ---
            await event.delete() # حذف رسالة الاختيار
            await client.delete_messages(TARGET_BOT, [sent_to_bot.id, reply.id])
            # مسح الدردشة بالكامل مع البوت الخارجي للأمان
            await client.delete_dialog(TARGET_BOT) 
            
            client.remove_event_handler(catcher)
            
    # توقيت أمان (Timeout)
    await asyncio.sleep(120)
    client.remove_event_handler(catcher)
