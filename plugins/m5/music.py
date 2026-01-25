import __main__
import asyncio
import re
from telethon import events, types

client = __main__.client

# بوتات التحميل (تأكد انك مفعل /start معهم)
YT_BOT = "@utubebot" 
TIK_BOT = "@SaveAsbot"

@client.on(events.NewMessage(outgoing=True))
async def universal_downloader(event):
    text = event.text
    # فحص الروابط
    is_yt = "youtube.com" in text or "youtu.be" in text
    is_tk = "tiktok.com" in text
    
    if is_yt or is_tk:
        chat_id = event.chat_id
        target = YT_BOT if is_yt else TIK_BOT
        
        # 1. شريط التحميل الوهمي للهيبة
        msg = await event.edit("🎬 **جاري الاتصال بالسيرفر...**\n`[▒▒▒▒▒▒▒▒▒▒] 0%`")
        await asyncio.sleep(1)
        
        # 2. إرسال الرابط للبوت المناسب سراً
        sent_msg = await client.send_message(target, text)
        await msg.edit("📥 **جاري سحب البيانات...**\n`[███▒▒▒▒▒▒▒] 35%`\n⏱ _انتظر قليلاً..._")

        # 3. مراقبة الرد
        @client.on(events.NewMessage(from_users=target))
        async def catcher(reply):
            # إذا طلب البوت اختيار الجودة (خاص باليوتيوب)
            if reply.buttons:
                for row in reply.buttons:
                    for button in row:
                        # البحث عن جودة 720p أو MP4 والضغط تلقائياً
                        if "720" in button.text or "MP4" in button.text or "High" in button.text:
                            await button.click()
                            await msg.edit("⚡ **جاري المعالجة النهائية...**\n`[███████▒▒▒] 75%`")
                            return

            # استلام الفيديو النهائي
            if reply.media and not isinstance(reply.media, types.MessageMediaPhoto):
                await msg.edit("✅ **اكتمل السحب! جاري الرفع...**\n`[██████████] 100%`")
                await asyncio.sleep(1)
                
                # إرسال الفيديو من حسابك للهيبة
                await client.send_file(chat_id, reply.media, caption="🎬 **تم التحميل بواسطة سورس نيثرون**")
                
                # تنظيف الآثار تماماً
                await msg.delete()
                await client.delete_messages(target, [reply.id, sent_msg.id])
                await client.delete_dialog(target)
                client.remove_event_handler(catcher)

        # توقيت أمان لمدة 3 دقائق
        await asyncio.sleep(180)
        client.remove_event_handler(catcher)
