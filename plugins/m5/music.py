import __main__
import asyncio
import re
from telethon import events, types

client = __main__.client

# بوت مباشر وسريع (تأكد انك مفعل /start وياه)
TARGET_BOT = "@SaveAsbot" 

@client.on(events.NewMessage(outgoing=True))
async def premium_downloader(event):
    text = event.text
    if "youtube.com" in text or "youtu.be" in text or "tiktok.com" in text:
        chat_id = event.chat_id
        
        # 1. إرسال رسالة انتظار مع شريط تحميل وهمي للهيبة
        msg = await event.edit("🎬 **جاري تجهيز الفيديو...**\n`[▒▒▒▒▒▒▒▒▒▒] 0%`")
        await asyncio.sleep(1)
        await msg.edit("📥 **جاري السحب من السيرفر...**\n`[███▒▒▒▒▒▒▒] 30%`")
        
        # 2. إرسال الرابط للبوت المساعد سراً
        sent_msg = await client.send_message(TARGET_BOT, text)
        
        await msg.edit("⚡ **جاري المعالجة النهائية...**\n`[███████▒▒▒] 70%`\n⏱ _انتظر من 1-3 دقائق_")

        # 3. مراقبة الرد
        @client.on(events.NewMessage(from_users=TARGET_BOT))
        async def catcher(reply):
            # إذا البوت أرسل أزرار جودة، نختار 720p أو أعلى جودة تلقائياً
            if reply.buttons:
                for row in reply.buttons:
                    for button in row:
                        if "720" in button.text or "High" in button.text or "Quality" in button.text:
                            await button.click()
                            return

            # استلام الفيديو (تجاهل الصور والمعاينات)
            if reply.media and not isinstance(reply.media, types.MessageMediaPhoto):
                await msg.edit("✅ **اكتمل التحميل! جاري الإرسال...**\n`[██████████] 100%`")
                await asyncio.sleep(1)
                
                # إرسال الفيديو باسم السورس
                await client.send_file(chat_id, reply.media, caption="🎬 **تم التحميل بواسطة سورس نيثرون**")
                
                # تنظيف الآثار فوراً لإخفاء استخدام بوت خارجي
                await msg.delete()
                await client.delete_messages(TARGET_BOT, [reply.id, sent_msg.id])
                await client.delete_dialog(TARGET_BOT)
                client.remove_event_handler(catcher)

        # توقيت أمان
        await asyncio.sleep(180) 
        client.remove_event_handler(catcher)
