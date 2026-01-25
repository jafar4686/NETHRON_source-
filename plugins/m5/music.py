import __main__
from telethon import events
import yt_dlp
import requests
import os
import re

# الوصول للكلاينت من سورس نيثرون
client = __main__.client

# دالة ذكية لسحب الرابط من النص
def get_url(text):
    urls = re.findall(r'(https?://\S+)', text)
    for url in urls:
        if "youtube.com" in url or "youtu.be" in url or "tiktok.com" in url:
            return url
    return None

# اشتغال تلقائي بمجرد إرسال رسالة تحتوي رابط
@client.on(events.NewMessage(outgoing=True))
async def auto_dl(event):
    # إذا النص فارغ أو ما بيه رابط عوفه
    if not event.text:
        return
        
    url = get_url(event.text)
    if not url:
        return

    # التحقق إذا كان يوتيوب
    if "youtube" in url or "youtu.be" in url:
        await event.edit("⏳ **تم كشف رابط يوتيوب.. جاري السحب...**")
        v_file = f"y_{event.id}.mp4"
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': v_file,
            'quiet': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'nocheckcertificate': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'فيديو يوتيوب')
                desc = info.get('description', '')[:200]
            
            await event.client.send_file(
                event.chat_id, 
                v_file, 
                caption=f"🎬 **العنوان:** `{title}`\n\n📝 **الوصف:**\n`{desc}...`"
            )
            if os.path.exists(v_file): os.remove(v_file)
            await event.delete() # حذف الرسالة اللي بيها الرابط
            
        except Exception as e:
            if os.path.exists(v_file): os.remove(v_file)
            # إذا طلع خطأ 403 يطبع لك تنبيه
            if "403" in str(e):
                await event.edit("❌ **عذراً، يوتيوب حظر السيرفر حالياً (403).**")
            else:
                await event.edit(f"❌ **خطأ يوتيوب:** `{str(e)[:100]}`")

    # التحقق إذا كان تيك توك
    elif "tiktok.com" in url:
        await event.edit("⏳ **تم كشف رابط تيك توك.. جاري السحب...**")
        try:
            # استخدام API tikwm من ملفك bot4.py
            api_url = f"https://www.tikwm.com/api/?url={url}"
            data = requests.get(api_url).json()
            if data.get('code') == 0:
                v_url = data['data'].get('play')
                title = data['data'].get('title', 'TikTok')
                if v_url.startswith('//'): v_url = 'https:' + v_url
                
                await event.client.send_file(event.chat_id, v_url, caption=f"📱 `{title}`")
                await event.delete()
            else:
                await event.edit("❌ فشل سحب الرابط من API.")
        except Exception as e:
            await event.edit(f"❌ خطأ تيك توك: `{str(e)[:100]}`")

# أمر للتأكد أن الملف شغال
@client.on(events.NewMessage(pattern=r"^\.فحص تحميل$", outgoing=True))
async def check_plugin(event):
    await event.edit("✅ **ملف التحميل التلقائي شغال 100%**\nأرسل رابط يوتيوب أو تيك توك للتجربة.")
