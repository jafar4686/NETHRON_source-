import __main__
from telethon import events
import yt_dlp
import io
import os

# الوصول للكلاينت
client = __main__.client

@client.on(events.NewMessage(pattern=r"^\.م5$", outgoing=True))
async def m5_menu(event):
    m5_text = (
        "★────────☭────────★\n"
        "   ☭ • 𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 • ☭\n"
        "         • تـحـمـيـل مـبـاشـر •\n"
        "★────────☭────────★\n\n"
        "• `.بحث يوت` (رابط)\n"
        "• `.بحث تيك` (رابط)\n\n"
        "⚙️ **التحميل يتم بالذاكرة بدون حفظ ملفات.**"
    )
    await event.edit(m5_text)

@client.on(events.NewMessage(pattern=r"^\.بحث يوت (.*)", outgoing=True))
async def youtube_download(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري السحب للذاكرة...**")
    
    # إعدادات التحميل للبث المباشر (Streaming to memory)
    ydl_opts = {
        'format': 'best[ext=mp4]/best', 
        'quiet': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info['url']
            title = info.get('title', 'Video')

        await event.edit("🚀 **جاري الرفع المباشر...**")
        
        # إرسال الرابط كملف (تليجرام يسحب من الرابط مباشرة في بعض الحالات) 
        # أو رفعه كـ Stream
        await event.client.send_file(event.chat_id, video_url, caption=f"🎬 `{title}`")
        await event.delete()

    except Exception as e:
        await event.edit(f"❌ **خطأ:** `{str(e)[:100]}`")

@client.on(events.NewMessage(pattern=r"^\.بحث تيك (.*)", outgoing=True))
async def tiktok_download(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **سحب تيك توك...**")
    
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info['url']
        
        await event.client.send_file(event.chat_id, video_url, caption="📱 **تيك توك مباشر**")
        await event.delete()
    except Exception as e:
        await event.edit(f"❌ **خطأ تيك توك:** `{e}`")
