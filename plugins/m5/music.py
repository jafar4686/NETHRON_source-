import __main__
from telethon import events
import yt_dlp
import requests
import os
import re

# الوصول للكلاينت من السورس
client = __main__.client

# دالة للتحقق من الروابط
def extract_url(text):
    pattern = r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be|tiktok\.com)\S+)'
    match = re.search(pattern, text)
    return match.group(0) if match else None

# الأمر التلقائي: بمجرد إرسال رابط
@client.on(events.NewMessage(outgoing=True))
async def auto_downloader(event):
    url = extract_url(event.text)
    if not url:
        return

    # إذا كان رابط يوتيوب
    if "youtube.com" in url or "youtu.be" in url:
        await event.edit("⏳ **جاري جلب فيديو يوتيوب والوصف...**")
        v_file = f"y_{event.id}.mp4"
        ydl_opts = {
            'format': 'best',
            'outtmpl': v_file,
            'quiet': True,
            'no_warnings': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'فيديو يوتيوب')
                desc = info.get('description', 'لا يوجد وصف')[:200]
            
            await event.client.send_file(
                event.chat_id, 
                v_file, 
                caption=f"🎬 **العنوان:** `{title}`\n\n📝 **الوصف:**\n`{desc}...`"
            )
            if os.path.exists(v_file): os.remove(v_file)
            await event.delete()
        except Exception as e:
            if os.path.exists(v_file): os.remove(v_file)
            await event.edit(f"❌ خطأ يوتيوب: `{str(e)[:100]}`")

    # إذا كان رابط تيك توك (باستخدام API tikwm من ملفك bot4.py)
    elif "tiktok.com" in url:
        await event.edit("⏳ **جاري سحب تيك توك والوصف...**")
        try:
            api_url = f"https://www.tikwm.com/api/?url={url}"
            data = requests.get(api_url).json()
            if data.get('code') == 0:
                v_url = data['data'].get('play')
                title = data['data'].get('title', 'تيك توك')
                if v_url.startswith('//'): v_url = 'https:' + v_url
                
                await event.client.send_file(
                    event.chat_id, 
                    v_url, 
                    caption=f"📱 **الوصف:**\n`{title}`"
                )
                await event.delete()
        except Exception as e:
            await event.edit(f"❌ خطأ تيك توك: `{str(e)[:100]}`")

# قائمة الأوامر م5 (للتوضيح فقط)
@client.on(events.NewMessage(pattern=r"^\.م5$", outgoing=True))
async def m5_info(event):
    await event.edit("✅ **نظام التحميل التلقائي مفعل:**\n\nفقط أرسل رابط (يوتيوب أو تيك توك) في أي دردشة، وسأقوم بتحميله فوراً مع الوصف.")
