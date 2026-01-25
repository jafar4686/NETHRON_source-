import __main__
import asyncio
import re
from telethon import events, types

client = __main__.client
TARGET_BOT = "@OTHMAN_HKS_bot"

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(بحث يوت|بحث تيك) (.*)"))
async def nethron_search_dl(event):
    cmd = event.pattern_match.group(1)
    url = event.pattern_match.group(2).strip()
    chat_id = event.chat_id
    
    platform_name = "يوتيوب" if "يوت" in cmd else "تيك توك"
    
    # 1. شريط التحميل للهيبة
    msg = await event.edit(f"🎬 **جاري الدخول لقسم {platform_name}...**\n`[▒▒▒▒▒▒▒▒▒▒] 0%`")
    
    try:
        async with client.conversation(TARGET_BOT, timeout=200) as conv:
            # الخطوة 1: تشغيل البوت
            await conv.send_message("/start")
            res1 = await conv.get_response()
            
            # الضغط على زر المنصة
            if res1.buttons:
                for row in res1.buttons:
                    for button in row:
                        if platform_name in button.text:
                            await button.click()
                            break
            
            await asyncio.sleep(2) 
            await msg.edit(f"📥 **تم الاختيار.. جاري إرسال الرابط...**\n`[███▒▒▒▒▒▒▒] 35%`")

            # الخطوة 2: إرسال الرابط
            await conv.send_message(url)
            
            # الخطوة 3: الضغط على "مقطع فيديو" تلقائياً
            # ننتظر الرد الذي يحتوي على خيارات (فيديو/صوت/بصمة)
            res2 = await conv.get_response()
            if res2.buttons:
                found_vid = False
                for row in res2.buttons:
                    for button in row:
                        # التدقيق في النص لاختيار الفيديو فقط
                        if "مقطع فيديو" in button.text or "فيديو" in button.text or "🎬" in button.text:
                            await button.click()
                            found_vid = True
                            break
                    if found_vid: break
            
            await msg.edit("⚡ **جاري معالجة الفيديو...**\n`[███████▒▒▒] 75%` \n⏱ _ثواني ويصلك الملف_")

            # الخطوة 4: استلام الفيديو النهائي (يتجاهل الصور والمعاينات)
            while True:
                final_res = await conv.get_response()
                # التأكد أن الميديا فيديو وليس صورة أو بصمة
                if final_res.media and not isinstance(final_res.media, types.MessageMediaPhoto):
                    await msg.edit("✅ **اكتمل التحميل! جاري الرفع...**\n`[██████████] 100%`")
                    await client.send_file(chat_id, final_res.media, caption=f"🎬 **تم التحميل بنجاح (نيثرون)**")
                    break
            
            # تنظيف المحادثة تماماً للأمان
            await msg.delete()
            await client.delete_dialog(TARGET_BOT)

    except Exception as e:
        await event.edit(f"❌ **حدث خطأ أو تأخر البوت:**\n`{str(e)}`")
        await client.delete_dialog(TARGET_BOT)
