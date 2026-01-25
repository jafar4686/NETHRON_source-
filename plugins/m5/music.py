import __main__
from telethon import events
import yt_dlp
import requests
import os
import re

# الوصول للكلاينت من سورس نيثرون
client = __main__.client

def get_url(text):
    urls = re.findall(r'(https?://\S+)', text)
    for url in urls:
        if "youtube.com" in url or "youtu.be" in url or "tiktok.com" in url:
            return url
    return None

@client.on(events.NewMessage(outgoing=True))
async def auto_dl(event):
    if not event.text: return
    url = get_url(event.text)
    if not url: return

    # --- قسم يوتيوب (إعدادات كسر الحظر بالسيرفر الجديد) ---
    if "youtube" in url or "youtu.be" in url:
        await event.edit("⏳ **جاري جلب الفيديو من يوتيوب...**")
        v_file = f"y_{event.id}.mp4"
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': v_file,
            'quiet': True,
            'no_warnings': True,
            # إعدادات قوية لتبدو كأنك متصفح ايفون (تكسر الـ 403)
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
            'referer': 'https://www.youtube.com/',
            'nocheckcertificate': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'فيديو يوتيوب')
                # جلب الوصف (أول 150 حرف)
                desc = info.get('description', '')[:150]
            
            await event.edit("🚀 **جاري الرفع...**")
            await event.client.send_file(
                event.chat_id, 
                v_file, 
                caption=f"🎬 **العنوان:** `{title}`\n\n📝 **الوصف:**\n`{desc}...`"
            )
            if os.path.exists(v_file): os.remove(v_file)
            await event.delete()
            
        except Exception as e:
            if os.path.exists(v_file): os.remove(v_file)
            await event.edit(f"❌ **فشل التحميل:**\n`{str(e)[:100]}`")

    # --- قسم تيك توك (منطق ملفك القديم bot4.py) ---
    elif "tiktok.com" in url:
        await event.edit("⏳ **جاري جلب تيك توك...**")
        try:
            api_tik = f"https://www.tikwm.com/api/?url={url}"
            data = requests.get(api_tik).json()
            if data.get('code') == 0:
                v_url = data['data'].get('play')
                title = data['data'].get('title', 'TikTok')
                if v_url.startswith('//'): v_url = 'https:' + v_url
                
                await event.client.send_file(event.chat_id, v_url, caption=f"📱 `{title}`")
                await event.delete()
            else:
                await event.edit("❌ رابط تيك توك غير صالح.")
        except Exception:
            await event.edit("❌ خطأ في محرك تيك توك.")

# أمر الفحص
@client.on(events.NewMessage(pattern=r"^\.فحص$", outgoing=True))
async def check(event):
    await event.edit("✅ **المحرك شغال وبانتظار الروابط!**")
