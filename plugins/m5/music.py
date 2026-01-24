import __main__
from telethon import events
import requests
import re
import os

# الوصول للكلاينت المعرف في نيثرون
client = __main__.client

# 1. قائمة الأوامر م5
@client.on(events.NewMessage(pattern=r"^\.م5$", outgoing=True))
async def m5_menu(event):
    m5_text = (
        "⚡️ **قـسـم الـتـحـمـيـل الـسـريـع**\n"
        "──────────────────\n"
        "• `.بحث يوت` + رابط اليوتيوب\n"
        "• `.بحث تيك` + رابط تيك توك\n"
        "──────────────────\n"
        "⚙️ الرفع مباشر بدون حفظ ملفات."
    )
    await event.edit(m5_text)

# 2. تحميل تيك توك (نفس منطق ملفك bot4.py بالضبط)
@client.on(events.NewMessage(pattern=r"^\.بحث تيك (.*)", outgoing=True))
async def tiktok_dl(event):
    video_url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري سحب فيديو تيك توك والوصف...**")
    
    try:
        # استخدام نفس الـ API اللي بملفك القديم
        api_url = f"https://www.tikwm.com/api/?url={video_url}"
        response = requests.get(api_url, timeout=30)
        data = response.json()
        
        if data.get('code') == 0:
            video_data = data.get('data', {})
            play_url = video_data.get('play') # الرابط المباشر
            title = video_data.get('title', 'فيديو تيك توك') # العنوان/الوصف
            
            if play_url:
                if play_url.startswith('//'): play_url = 'https:' + play_url
                
                # إرسال الفيديو مباشرة مع الوصف
                await event.client.send_file(
                    event.chat_id, 
                    play_url, 
                    caption=f"📱 **الوصف:**\n`{title}`"
                )
                await event.delete()
            else:
                await event.edit("❌ فشل الحصول على رابط التشغيل")
        else:
            await event.edit("❌ الرابط غير صالح أو محمي")
            
    except Exception as e:
        await event.edit(f"❌ خطأ تيك توك: `{str(e)[:100]}`")

# 3. تحميل يوتيوب (رفع مباشر لتجنب cURL)
@client.on(events.NewMessage(pattern=r"^\.بحث يوت (.*)", outgoing=True))
async def youtube_dl(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري جلب معلومات يوتيوب...**")
    
    import yt_dlp
    ydl_opts = {'format': 'best', 'quiet': True, 'no_warnings': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            title = info.get('title', 'فيديو يوتيوب')
            description = info.get('description', 'لا يوجد وصف')[:250]

        if video_url:
            caption = f"🎬 **العنوان:** `{title}`\n\n📝 **الوصف:**\n`{description}...`"
            # إرسال الرابط المباشر كملف لتجنب SendMediaRequest
            await event.client.send_file(event.chat_id, video_url, caption=caption)
            await event.delete()
        else:
            await event.edit("❌ فشل استخراج رابط يوتيوب")
            
    except Exception as e:
        await event.edit(f"❌ خطأ يوتيوب: `{str(e)[:100]}`")
