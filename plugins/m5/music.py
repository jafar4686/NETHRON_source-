import __main__
from telethon import events
import yt_dlp
import os

# الوصول للكلاينت من الملف الرئيسي
client = __main__.client

@client.on(events.NewMessage(pattern=r"^\.م5$", outgoing=True))
async def m5_menu(event):
    await event.edit("⚡️ **قـسـم الـتـحـمـيـل الـسـريع**\n\n• `.بحث يوت` + الرابط\n• `.بحث تيك` + الرابط")

@client.on(events.NewMessage(pattern=r"^\.بحث يوت (.*)", outgoing=True))
async def yut_dl(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري جلب الوصف والرفع...**")
    
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info['url'] # رابط الفيديو المباشر
            title = info.get('title', 'لا يوجد عنوان')
            desc = info.get('description', 'لا يوجد وصف')[:250] # أول 250 حرف من الوصف

        # إرسال الفيديو مباشرة باستخدام الرابط المستخرج مع الوصف
        caption = f"🎬 **العنوان:** `{title}`\n\n📝 **الوصف:**\n`{desc}...`"
        await event.client.send_file(event.chat_id, video_url, caption=caption)
        await event.delete()

    except Exception as e:
        await event.edit(f"❌ **فشل جلب الفيديو:**\n`{str(e)[:150]}`")

@client.on(events.NewMessage(pattern=r"^\.بحث تيك (.*)", outgoing=True))
async def tik_dl(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري سحب تيك توك...**")
    
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info['url']
            desc = info.get('description', 'فيديو تيك توك')

        await event.client.send_file(event.chat_id, video_url, caption=f"📱 **تيك توك:**\n`{desc}`")
        await event.delete()
    except Exception as e:
        await event.edit(f"❌ **خطأ:** `{str(e)[:100]}`")
