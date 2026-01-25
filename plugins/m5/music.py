import __main__
import asyncio
import re
from telethon import events

client = __main__.client

# بوت التحميل (تأكد انك مفعل /start وياه بالخاص)
TARGET_BOT = "@C_5BOT"

@client.on(events.NewMessage(outgoing=True))
async def silent_downloader(event):
    text = event.text
    # فحص الروابط (يوتيوب، تيك توك)
    if "youtube.com" in text or "youtu.be" in text or "tiktok.com" in text:
        chat_id = event.chat_id
        await event.edit("⏳ **جاري جلب الوسائط...**")
        
        # 1. إرسال الرابط للبوت الخارجي سراً
        sent_msg = await client.send_message(TARGET_BOT, text)
        await event.delete() # حذف رسالة الرابط الأصلية

        files_received = 0
        
        # 2. مراقبة الردود (فيديو ثم صوت)
        @client.on(events.NewMessage(from_users=TARGET_BOT))
        async def catcher(reply):
            nonlocal files_received
            if reply.media:
                # فورورد للملف (سواء فيديو أو صوت)
                await client.send_file(chat_id, reply.media, caption="✅ **بواسطة سورس نيثرون**")
                files_received += 1
                
                # حذف الرسالة من خاص البوت فوراً
                await client.delete_messages(TARGET_BOT, [reply.id])
                
                # إذا استلمنا ملفين (الفيديو والصوت) أو مر وقت كافي
                if files_received >= 2:
                    await client.delete_messages(TARGET_BOT, [sent_msg.id])
                    await client.delete_dialog(TARGET_BOT) # تصفير المحادثة نهائياً
                    client.remove_event_handler(catcher)

        # توقيت أمان: إذا تأخر البوت أكثر من دقيقتين يوقف المراقبة
        await asyncio.sleep(120)
        client.remove_event_handler(catcher)
        await client.delete_dialog(TARGET_BOT)
