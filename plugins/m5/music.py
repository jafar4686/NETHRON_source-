import __main__
import asyncio
import re
from telethon import events, types

client = __main__.client

# بوت التحميل (تأكد انك مفعل /start وياه بالخاص)
TARGET_BOT = "@C_5BOT"

@client.on(events.NewMessage(outgoing=True))
async def silent_downloader(event):
    text = event.text
    # فحص روابط يوتيوب وتيك توك
    if "youtube.com" in text or "youtu.be" in text or "tiktok.com" in text:
        chat_id = event.chat_id
        await event.edit("⏳ **جاري جلب الفيديو والصوت سراً...**")
        
        # 1. إرسال الرابط للبوت الخارجي
        sent_msg = await client.send_message(TARGET_BOT, text)
        await event.delete() 

        # 2. مراقبة الردود (نتجاهل الصور ونأخذ الفيديو والصوت فقط)
        @client.on(events.NewMessage(from_users=TARGET_BOT))
        async def catcher(reply):
            # التأكد أن الرد هو فيديو أو ملف صوتي وليس صورة معاينة
            if reply.media and not isinstance(reply.media, types.MessageMediaPhoto):
                # إرسال الملف الأصلي للشات
                await client.send_file(chat_id, reply.media, caption="✅ **بواسطة سورس نيثرون**")
                
                # حذف الرسالة من خاص البوت فوراً لإخفاء الأثر
                await client.delete_messages(TARGET_BOT, [reply.id])
            
            # إذا استلمنا فيديو وصوت، أو إذا البوت دز رسالة نصية تعني انتهى
            # نمسح المحادثة ونوقف المراقبة
            if reply.video or reply.audio or reply.voice:
                 # ننتظر قليلاً للتأكد من وصول الملف الثاني (الصوت)
                 await asyncio.sleep(2) 
                 await client.delete_messages(TARGET_BOT, [sent_msg.id])
                 await client.delete_dialog(TARGET_BOT)
                 client.remove_event_handler(catcher)

        # توقيت أمان لمدة دقيقتين
        await asyncio.sleep(120)
        client.remove_event_handler(catcher)
        await client.delete_dialog(TARGET_BOT)
