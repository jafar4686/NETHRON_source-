import os
import yt_dlp
from telethon import events
from resources.strings import * # استيراد الكليشات إذا كانت موجودة

# كليشة القائمة م5
KLESHA_M5 = """
⚡️ **قـسـم الـتـحـمـيـل - نـيـثـرون** ⚡️
──────────────────
🔹 `.بحث يوت` + رابط : تحميل فيديو وصوت من يوتيوب
🔹 `.بحث تيك` + رابط : تحميل من تيك توك بدون حقوق
──────────────────
⚙️ **أرسل الرابط مع الأمر للبدء.**
"""

# 1. أمر تحديث القائمة .م5
@bot.on(events.NewMessage(pattern=r'\.م5', outgoing=True))
async def m5_menu(event):
    await event.edit(KLESHA_M5)

# 2. تحميل يوتيوب (فيديو + صوت + معلومات)
@bot.on(events.NewMessage(pattern=r'\.بحث يوت (.*)', outgoing=True))
async def yut_dl(event):
    url = event.pattern_match.group(1)
    await event.edit("⏳ **جاري جلب معلومات الفيديو...**")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'Nethron Video')
            desc = info.get('description', 'لا يوجد وصف')[:200]
            duration = info.get('duration', 0)

        # إرسال الفيديو
        await event.client.send_file(
            event.chat_id, 
            filename, 
            caption=f"🎬 **تـم الـتـحـمـيـل**\n📌 `{title}`\n⏱ {duration}ث\n📝 {desc}.."
        )
        
        # إرسال الصوت (بصمة)
        await event.client.send_file(
            event.chat_id, 
            filename, 
            caption=f"🎼 صوت: {title}",
            voice_note=True
        )
        
        if os.path.exists(filename):
            os.remove(filename)
        await event.delete()
            
    except Exception as e:
        await event.edit(f"❌ **خطأ:** `{str(e)}`")

# 3. تحميل تيك توك
@bot.on(events.NewMessage(pattern=r'\.بحث تيك (.*)', outgoing=True))
async def tik_dl(event):
    url = event.pattern_match.group(1)
    await event.edit("⏳ **جاري تحميل فيديو تيك توك...**")
    
    ydl_opts = {
        'outtmpl': 'downloads/tiktok.mp4',
        'quiet': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            uploader = info.get('uploader', 'TikTok User')
            
        await event.client.send_file(
            event.chat_id, 
            'downloads/tiktok.mp4', 
            caption=f"📱 **تـيـك تـوك**\n👤 المصمم: `{uploader}`"
        )
        if os.path.exists('downloads/tiktok.mp4'):
            os.remove('downloads/tiktok.mp4')
        await event.delete()
    except Exception as e:
        await event.edit(f"❌ **فشل:** `{str(e)}`")
