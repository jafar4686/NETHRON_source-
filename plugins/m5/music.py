import __main__
import asyncio
import re
from telethon import events, types

client = __main__.client

# البوت المستهدف
TARGET_BOT = "@C_5BOT"

@client.on(events.NewMessage(outgoing=True))
async def silent_downloader(event):
    text = event.text
    # فحص روابط يوتيوب وتيك توك
    if "youtube.com" in text or "youtu.be" in text or "tiktok.com" in text:
        chat_id = event.chat_id
        await event.edit("⏳ **جاري التحميل التلقائي (فيديو)...**")
        
        # 1. إرسال الرابط للبوت الخارجي
        sent_msg = await client.send_message(TARGET_BOT, text)
        await event.delete() 

        # 2. مراقبة الرسائل القادمة من البوت للضغط على الأزرار
        @client.on(events.NewMessage(from_users=TARGET_BOT))
        async def catcher(reply):
            # إذا البوت أرسل أزرار خيارات
            if reply.buttons:
                for row in reply.buttons:
                    for button in row:
                        # البحث عن زر يحتوي كلمة "فيديو" أو "Video" والضغط عليه تلقائياً
                        if "فيديو" in button.text or "Video" in button.text:
                            await button.click()
                            return # الخروج بعد الضغط

            # التأكد أن الرد هو فيديو وليس صورة معاينة
            if reply.media and not isinstance(reply.media, types.MessageMediaPhoto):
                # إرسال الملف الأصلي للشات مالتك
                await client.send_file(chat_id, reply.media, caption="✅ **بواسطة سورس نيثرون**")
                
                # تنظيف الأثر فوراً
                await asyncio.sleep(1)
                await client.delete_messages(TARGET_BOT, [reply.id, sent_msg.id])
                await client.delete_dialog(TARGET_BOT)
                client.remove_event_handler(catcher)

        # توقيت أمان لغلق المراقبة بعد دقيقتين
        await asyncio.sleep(120)
        client.remove_event_handler(catcher)
