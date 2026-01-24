import __main__
from telethon import events
import yt_dlp
import os

client = __main__.client

@client.on(events.NewMessage(pattern=r"^\.بحث يوت (.*)"))
async def youtube_download(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري جلب البيانات من يوتيوب...**")
    
    if not os.path.exists("downloads"): os.makedirs("downloads")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'nocheckcertificate': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            title = info.get('title', 'Video')

        await event.edit("✅ **جاري رفع الملفات...**")
        await event.client.send_file(event.chat_id, path, caption=f"🎬 **يوتيوب:** `{title}`")
        await event.client.send_file(event.chat_id, path, voice_note=True)
        
        if os.path.exists(path): os.remove(path)
        await event.delete()
    except Exception as e:
        await event.edit(f"❌ **خطأ يوتيوب:**\n`{str(e)}`")

@client.on(events.NewMessage(pattern=r"^\.بحث تيك (.*)"))
async def tiktok_download(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري تحميل تيك توك...**")
    
    path_tik = "downloads/tik_nethron.mp4"
    ydl_opts = {
        'outtmpl': path_tik, 
        'quiet': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        await event.client.send_file(event.chat_id, path_tik, caption="📱 **تيك توك نيثرون**")
        if os.path.exists(path_tik): os.remove(path_tik)
        await event.delete()
    except Exception as e:
        await event.edit(f"❌ **خطأ تيك توك:** `{e}`")
