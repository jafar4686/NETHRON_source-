import __main__
import asyncio
import re
from telethon import events, types

client = __main__.client

# هذا البوت يدز الفيديو كبل بدون أزرار
TARGET_BOT = "@YtbDownBot" 

@client.on(events.NewMessage(outgoing=True))
async def direct_downloader(event):
    text = event.text
    # فحص روابط يوتيوب وتيك توك
    if "youtube.com" in text or "youtu.be" in text or "tiktok.com" in text:
        chat_id = event.chat_id
        await event.edit("🚀 **جاري التحميل المباشر...**")
        
        # 1. إرسال الرابط للبوت المباشر سراً
        sent_msg = await client.send_message(TARGET_BOT, text)
        await event.delete() 

        # 2. مراقبة الرد واستلام الفيديو فوراً
        @client.on(events.NewMessage(from_users=TARGET_BOT))
        async def catcher(reply):
            # التأكد من وصول ملف (فيديو أو ميديا) وتجاهل الرسائل النصية والصور
            if reply.media and not isinstance(reply.media, types.MessageMediaPhoto):
                # إرسال الفيديو فوراً للشات مالتك
                await client.send_file(chat_id, reply.media, caption="✅ **بواسطة سورس نيثرون**")
                
                # تنظيف الآثار فوراً
                await client.delete_messages(TARGET_BOT, [reply.id, sent_msg.id])
                await client.delete_dialog(TARGET_BOT) # مسح المحادثة نهائياً
                client.remove_event_handler(catcher)

        # توقيت أمان لمدة دقيقتين في حال تأخر البوت
        await asyncio.sleep(120)
        client.remove_event_handler(catcher)
