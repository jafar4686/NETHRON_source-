import __main__
from telethon import events
import requests
import re
import os

# الوصول للكلاينت من الملف الرئيسي لنيثرون
client = __main__.client

@client.on(events.NewMessage(pattern=r"^\.بحث يوت (.*)", outgoing=True))
async def yut_dl(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري جلب وصف وتحميل فيديو يوتيوب...**")
    
    # استخدام API خارجي لجلب الرابط المباشر والوصف (كما في كودك القديم)
    # ملاحظة: يوتيوب يحتاج معالجة خاصة لذا سنستخدم استخراج المعلومات فقط
    import yt_dlp
    ydl_opts = {'format': 'best', 'quiet': True, 'no_warnings': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            title = info.get('title', 'فيديو يوتيوب')
            description = info.get('description', 'لا يوجد وصف')[:300]

        if video_url:
            await event.edit("🚀 **جاري الرفع المباشر للفيديو...**")
            caption = f"🎬 **العنوان:** `{title}`\n\n📝 **الوصف:**\n`{description}...`"
            # الإرسال المباشر بدون حفظ ملف
            await event.client.send_file(event.chat_id, video_url, caption=caption)
            await event.delete()
        else:
            await event.edit("❌ فشل الحصول على رابط الفيديو المباشر")
            
    except Exception as e:
        await event.edit(f"❌ **حدث خطأ:**\n`{str(e)[:150]}`")

@client.on(events.NewMessage(pattern=r"^\.بحث تيك (.*)", outgoing=True))
async def tik_dl(event):
    video_url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري جلب وصف وتحميل تيك توك...**")
    
    try:
        # استخلاص منطق التحميل من ملفك القديم (bot4.py)
        api_url = f"https://www.tikwm.com/api/?url={video_url}"
        response = requests.get(api_url, timeout=30)
        data = response.json()
        
        if data.get('code') == 0:
            video_data = data.get('data', {})
            play_url = video_data.get('play') # رابط الفيديو المباشر
            title = video_data.get('title', 'فيديو تيك توك')
            
            if play_url:
                # إضافة نطاق الـ API إذا كان الرابط ناقصاً كما في الكود القديم
                if play_url.startswith('//'): play_url = 'https:' + play_url
                
                await event.edit("🚀 **جاري الرفع المباشر...**")
                await event.client.send_file(event.chat_id, play_url, caption=f"📱 **العنوان:** `{title}`")
                await event.delete()
            else:
                await event.edit("❌ لم أجد رابط الفيديو")
        else:
            await event.edit("❌ رابط تيك توك غير صالح")
            
    except Exception as e:
        await event.edit(f"❌ **خطأ تيك توك:** `{str(e)[:100]}`")
