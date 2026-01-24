import __main__
from telethon import events
import requests
import re
import os

# الوصول للكلاينت من ملف المين
client = __main__.client

@client.on(events.NewMessage(pattern=r"^\.بحث يوت (.*)", outgoing=True))
async def yut_dl(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري جلب الوصف والرفع المباشر...**")
    
    # استخدام API خارجي لجلب رابط فيديو يوتيوب المباشر لتجنب حظر السيرفر
    # تم تبسيط هذا الجزء ليعمل بدون حفظ ملفات نهائياً
    import yt_dlp
    ydl_opts = {'format': 'best', 'quiet': True, 'no_warnings': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            title = info.get('title', 'فيديو يوتيوب')
            description = info.get('description', 'لا يوجد وصف')[:300]

        if video_url:
            caption = f"🎬 **العنوان:** `{title}`\n\n📝 **الوصف:**\n`{description}...`"
            # إرسال الرابط المباشر (Stream) كملف فيديو
            await event.client.send_file(event.chat_id, video_url, caption=caption)
            await event.delete()
        else:
            await event.edit("❌ فشل الحصول على رابط الفيديو")
            
    except Exception as e:
        await event.edit(f"❌ **خطأ يوتيوب:**\n`{str(e)[:150]}`")

@client.on(events.NewMessage(pattern=r"^\.بحث تيك (.*)", outgoing=True))
async def tik_dl(event):
    video_url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري جلب وصف فيديو تيك توك...**")
    
    try:
        # استخلاص منطق التحميل باستخدام TikWM API من كودك القديم
        api_url = f"https://www.tikwm.com/api/?url={video_url}"
        response = requests.get(api_url, timeout=30)
        data = response.json()
        
        if data.get('code') == 0:
            video_data = data.get('data', {})
            play_url = video_data.get('play')
            title = video_data.get('title', 'فيديو تيك توك')
            
            if play_url:
                # تصحيح الرابط إذا كان ناقصاً
                if play_url.startswith('//'): play_url = 'https:' + play_url
                
                await event.edit("🚀 **رفع تيك توك مباشر...**")
                # إرسال الفيديو مباشرة من الرابط دون تخزينه
                await event.client.send_file(event.chat_id, play_url, caption=f"📱 **العنوان:** `{title}`")
                await event.delete()
            else:
                await event.edit("❌ لم أجد رابط الفيديو")
        else:
            await event.edit("❌ رابط تيك توك غير صالح")
            
    except Exception as e:
        await event.edit(f"❌ **خطأ تيك توك:** `{str(e)[:100]}`")
