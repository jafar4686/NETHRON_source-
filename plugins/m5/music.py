import __main__
from telethon import events
import yt_dlp
import os

client = __main__.client

# أمر تحميل يوتيوب
@client.on(events.NewMessage(pattern=r"^\.بحث يوت (.*)"))
async def youtube_download(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري جلب معلومات الفيديو والتحميل...**")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            title = info.get('title', 'Video')
            uploader = info.get('uploader', 'Unknown')

        caption = f"🎬 **تـم الـتـحـمـيـل مـن يـوتـيـوب**\n📌 **العنوان:** `{title}`\n👤 **القناة:** `{uploader}`"
        
        # إرسال الفيديو ثم البصمة
        await event.client.send_file(event.chat_id, path, caption=caption)
        await event.client.send_file(event.chat_id, path, voice_note=True)
        
        os.remove(path) # تنظيف المساحة
        await event.delete()
    except Exception as e:
        await event.edit(f"❌ **خطأ يوتيوب:** `{e}`")

# أمر تحميل تيك توك
@client.on(events.NewMessage(pattern=r"^\.بحث تيك (.*)"))
async def tiktok_download(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري تحميل فيديو تيك توك...**")
    
    ydl_opts = {'outtmpl': 'downloads/tik.mp4', 'quiet': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            uploader = info.get('uploader', 'TikToker')

        await event.client.send_file(
            event.chat_id, 'downloads/tik.mp4', 
            caption=f"📱 **تـيـك تـوك نـيـثـرون**\n👤 **المصمم:** `{uploader}`"
        )
        os.remove('downloads/tik.mp4')
        await event.delete()
    except Exception as e:
        await event.edit(f"❌ **خطأ تيك توك:** `{e}`")
