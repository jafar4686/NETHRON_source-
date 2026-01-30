import __main__
import asyncio
import re
from telethon import events, types

client = __main__.client
TARGET_BOT = "@ckdkvnsndjcbot"

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(بحث يوت|بحث تيك) (.*)"))
async def nethron_search_dl(event):
    cmd = event.pattern_match.group(1)
    url = event.pattern_match.group(2).strip()
    chat_id = event.chat_id
    
    platform_name = "يوتيوب" if "يوت" in cmd else "تيك توك"
    
    # 1. شريط التحميل للهيبة
    msg = await event.edit(f"🎬 **جاري الدخول لقسم {platform_name}...**\n`[▒▒▒▒▒▒▒▒▒▒] 0%`")
    
    try:
        async with client.conversation(TARGET_BOT, timeout=300) as conv:
            # الخطوة 1: تشغيل البوت واختيار المنصة
            await conv.send_message("/start")
            res1 = await conv.get_response()
            
            if res1.buttons:
                for row in res1.buttons:
                    for button in row:
                        if platform_name in button.text:
                            await button.click()
                            break
            
            # انتظار بسيط للانتقال
            await asyncio.sleep(3) 
            await msg.edit(f"📥 **تم الاختيار.. جاري إرسال الرابط...**\n`[███▒▒▒▒▒▒▒] 35%`")

            # الخطوة 2: إرسال الرابط
            await conv.send_message(url)
            
            # --- [ التعديل الجديد: انتظار الأزرار بعشر ثواني ] ---
            await msg.edit("⌛ **جاري معالجة الرابط.. انتظر 10 ثوانٍ للأزرار...**\n`[█████▒▒▒▒▒] 50%`")
            
            # ننتظر 10 ثواني عشان البوت يلحق يطلع الأزرار
            await asyncio.sleep(10) 
            
            # الحصول على آخر رسالة أرسلها البوت (اللي المفروض بيها الأزرار)
            history = await client.get_messages(TARGET_BOT, limit=1)
            res2 = history[0]

            if res2.buttons:
                found_vid = False
                for row in res2.buttons:
                    for button in row:
                        # التدقيق في النص لاختيار الفيديو فقط
                        if "مقطع فيديو" in button.text or "فيديو" in button.text or "🎬" in button.text:
                            await button.click()
                            found_vid = True
                            await msg.edit("⚡ **تم اختيار الفيديو! جاري التحميل...**\n`[███████▒▒▒] 75%`")
                            break
                    if found_vid: break
            else:
                await msg.edit("❌ **البوت لم يرسل أزرار الخيارات، جرب مرة أخرى.**")
                return

            # الخطوة 4: استلام الفيديو النهائي
            while True:
                final_res = await conv.get_response()
                # التأكد أن الميديا فيديو
                if final_res.media and not isinstance(final_res.media, types.MessageMediaPhoto):
                    await msg.edit("✅ **اكتمل التحميل! جاري الرفع...**\n`[██████████] 100%`")
                    await client.send_file(chat_id, final_res.media, caption=f"🎬 **تم التحميل بنجاح (سورس نيثرون)**")
                    break
            
            # تنظيف المحادثة تماماً للأمان
            await msg.delete()
            await client.delete_messages(TARGET_BOT, [res1.id, res2.id]) # حذف رسائل الأزرار
            await client.delete_dialog(TARGET_BOT)

    except Exception as e:
        await event.edit(f"❌ **حدث خطأ أو تأخر البوت:**\n`{str(e)}`")
        await client.delete_dialog(TARGET_BOT)
