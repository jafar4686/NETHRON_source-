import __main__
import asyncio
import re
from telethon import events, types

client = __main__.client
TARGET_BOT = "@OTHMAN_HKS_bot"

# دالة البحث والتحميل الذكي
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(بحث يوت|بحث تيك) (.*)"))
async def nethron_search_dl(event):
    cmd = event.pattern_match.group(1)
    url = event.pattern_match.group(2)
    chat_id = event.chat_id
    
    # تحديد نوع المنصة للضغط على الزر الصحيح في أول خطوة
    platform_target = "يوتيوب" if "يوت" in cmd else "تيك توك"
    
    # 1. شريط التحميل للهيبة
    msg = await event.edit(f"🎬 **جاري البحث في {platform_target}...**\n`[▒▒▒▒▒▒▒▒▒▒] 0%`")
    
    # 2. بدء المحادثة مع البوت وإرسال /start لتظهر الأزرار
    async with client.conversation(TARGET_BOT) as conv:
        try:
            # إرسال ستارت لجلب الأزرار الأساسية
            await conv.send_message("/start")
            reply = await conv.get_response()
            
            # الضغط على زر المنصة (يوتيوب أو تيك توك)
            if reply.buttons:
                for row in reply.buttons:
                    for button in row:
                        if platform_target in button.text:
                            await button.click()
                            break
            
            await asyncio.sleep(1)
            # 3. إرسال الرابط الآن
            await msg.edit(f"📥 **تم اختيار {platform_target}.. جاري جلب الرابط...**\n`[███▒▒▒▒▒▒▒] 35%`")
            await conv.send_message(url)
            
            # 4. انتظار أزرار (فيديو / صوت) والضغط على فيديو
            reply_dl = await conv.get_response()
            if reply_dl.buttons:
                for row in reply_dl.buttons:
                    for button in row:
                        if "فيديو" in button.text or "Video" in button.text:
                            await button.click()
                            break
            
            await msg.edit("⚡ **جاري المعالجة النهائية...**\n`[███████▒▒▒] 75%`")

            # 5. استلام الفيديو النهائي
            # نبحث عن رسالة تحتوي على ميديا (ليست صورة)
            while True:
                final_res = await conv.get_response()
                if final_res.media and not isinstance(final_res.media, types.MessageMediaPhoto):
                    await msg.edit("✅ **اكتمل التحميل! جاري الرفع...**\n`[██████████] 100%`")
                    await client.send_file(chat_id, final_res.media, caption=f"🎬 **تم التحميل بنجاح عبر سورس نيثرون**\n🔗 المنصة: {platform_target}")
                    break
            
            # تنظيف المحادثة تماماً
            await msg.delete()
            await client.delete_dialog(TARGET_BOT)

        except Exception as e:
            await msg.edit(f"❌ **حدث خطأ:**\n`{str(e)}`")
            await client.delete_dialog(TARGET_BOT)
