import __main__
import asyncio
import re
from telethon import events, types

client = __main__.client

# البوت المستهدف (تأكد انك مفعل /start وياه بالخاص)
TARGET_BOT = "@OTHMAN_HKS_bot"

@client.on(events.NewMessage(outgoing=True))
async def nethron_downloader(event):
    text = event.text
    # التحقق من روابط يوتيوب وتيك توك
    if "youtube.com" in text or "youtu.be" in text or "tiktok.com" in text:
        chat_id = event.chat_id
        
        # 1. إظهار شريط التحميل الاحترافي
        msg = await event.edit("🎬 **جاري الاتصال بقاعدة بيانات نيثرون...**\n`[▒▒▒▒▒▒▒▒▒▒] 0%`")
        
        # 2. إرسال الرابط للبوت المساعد سراً
        sent_msg = await client.send_message(TARGET_BOT, text)
        await msg.edit("📥 **جاري جلب بيانات الفيديو...**\n`[███▒▒▒▒▒▒▒] 30%`")

        # 3. مراقبة الرد والتعامل مع الأزرار
        @client.on(events.NewMessage(from_users=TARGET_BOT))
        async def catcher(reply):
            # الضغط التلقائي على زر "فيديو" إذا ظهر
            if reply.buttons:
                for row in reply.buttons:
                    for button in row:
                        if "فيديو" in button.text or "Video" in button.text or "🎬" in button.text:
                            await button.click()
                            await msg.edit("⚡ **جاري المعالجة والرفع...**\n`[███████▒▒▒] 70%`")
                            return

            # استلام ملف الفيديو النهائي (نتجاهل الصور والمعاينات)
            if reply.media and not isinstance(reply.media, types.MessageMediaPhoto):
                await msg.edit("✅ **اكتمل التحميل! جاري الإرسال...**\n`[██████████] 100%`")
                await asyncio.sleep(1)
                
                # إرسال الفيديو من حسابك
                await client.send_file(chat_id, reply.media, caption="🎬 **تم التحميل بواسطة سورس نيثرون**")
                
                # تنظيف الآثار فوراً لإخفاء البوت الخارجي
                await msg.delete()
                await client.delete_messages(TARGET_BOT, [reply.id, sent_msg.id])
                await client.delete_dialog(TARGET_BOT) # مسح الدردشة نهائياً
                client.remove_event_handler(catcher)

        # توقيت أمان (3 دقائق) في حال تأخر البوت
        await asyncio.sleep(180)
        client.remove_event_handler(catcher)
