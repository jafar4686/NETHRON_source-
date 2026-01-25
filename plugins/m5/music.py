import __main__
from telethon import events
import yt_dlp
import requests
import os
import re

# الوصول للكلاينت من سورس نيثرون
client = __main__.client

def extract_url(text):
    pattern = r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be|tiktok\.com)\S+)'
    match = re.search(pattern, text)
    return match.group(0) if match else None

@client.on(events.NewMessage(outgoing=True))
async def auto_downloader(event):
    url = extract_url(event.text)
    if not url: return

    # يوتيوب - حل مشكلة 403 Forbidden
    if "youtube.com" in url or "youtu.be" in url:
        await event.edit("⏳ **جاري كسر حظر يوتيوب وسحب الفيديو...**")
        v_file = f"vid_{event.id}.mp4"
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': v_file,
            'quiet': True,
            'no_warnings': True,
            # هذي الإعدادات هي اللي تكسر الـ 403
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.google.com/',
            'nocheckcertificate': True,
            'geo_bypass': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Video')
                desc = info.get('description', '')[:250]
            
            await event.client.send_file(
                event.chat_id, 
                v_file, 
                caption=f"🎬 **العنوان:** `{title}`\n\n📝 **الوصف:**\n`{desc}...`"
            )
            if os.path.exists(v_file): os.remove(v_file)
            await event.delete()
            
        except Exception as e:
            if os.path.exists(v_file): os.remove(v_file)
            await event.edit(f"❌ **يوتيوب قفل السيرفر (403):**\n`جرب رابط ثاني أو انتظر شوي.`")

    # تيك توك - باستخدام الـ API اللي دزيته إنت (يحل كل المشاكل)
    elif "tiktok.com" in url:
        await event.edit("⏳ **جاري سحب تيك توك...**")
        try:
            api_url = f"https://www.tikwm.com/api/?url={url}"
            data = requests.get(api_url).json()
            if data.get('code') == 0:
                v_url = data['data'].get('play')
                title = data['data'].get('title', 'TikTok')
                if v_url.startswith('//'): v_url = 'https:' + v_url
                
                await event.client.send_file(event.chat_id, v_url, caption=f"📱 `{title}`")
                await event.delete()
        except Exception:
            await event.edit("❌ فشل سحب تيك توك.")

# قائمة الأوامر
@client.on(events.NewMessage(pattern=r"^\.م5$", outgoing=True))
async def m5_info(event):
    await event.edit("🚀 **نظام نيثرون للتحميل التلقائي:**\n\nفقط أرسل الرابط وسأقوم بالباقي!")
