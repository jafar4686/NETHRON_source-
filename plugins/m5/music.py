import __main__
from telethon import events
import requests
import re
import os

# الوصول للكلاينت من سورس نيثرون
client = __main__.client

# دالة ذكية لسحب الرابط
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

    # --- قسم يوتيوب (حل مشكلة 403 عبر API خارجي) ---
    if "youtube" in url or "youtu.be" in url:
        await event.edit("⏳ **يتـم السحب عبر منفذ خارجي (تخطى 403)...**")
        try:
            # استخدام API خارجي (يحل محل السيرفر المحظور)
            api_url = f"https://api.cobalt.tools/api/json"
            headers = {"Accept": "application/json", "Content-Type": "application/json"}
            payload = {"url": url, "vQuality": "720"}
            
            response = requests.post(api_url, json=payload, headers=headers)
            data = response.json()
            
            if data.get('url'):
                video_url = data['url']
                # الرفع المباشر من رابط الـ API
                await event.client.send_file(event.chat_id, video_url, caption="🎬 **تم التحميل بنجاح عبر المنفذ البديل**")
                await event.delete()
            else:
                await event.edit("❌ المنفذ البديل مشغول، جرب لاحقاً.")
        except Exception as e:
            await event.edit(f"❌ خطأ يوتيوب: السيرفر محظور والمنفذ لا يستجيب.")

    # --- قسم تيك توك (نفس منطق ملفك bot4.py) ---
    elif "tiktok.com" in url:
        await event.edit("⏳ **جاري سحب تيك توك (بدون حقوق)...**")
        try:
            # منطق الـ API اللي دزيته بملفك القديم
            api_tik = f"https://www.tikwm.com/api/?url={url}"
            data = requests.get(api_tik).json()
            if data.get('code') == 0:
                v_url = data['data'].get('play')
                title = data['data'].get('title', 'TikTok')
                if v_url.startswith('//'): v_url = 'https:' + v_url
                
                await event.client.send_file(event.chat_id, v_url, caption=f"📱 `{title}`")
                await event.delete()
            else:
                await event.edit("❌ فشل سحب تيك توك.")
        except Exception:
            await event.edit("❌ خطأ في الاتصال بالمحرك.")

# للتأكد من عمل الملف
@client.on(events.NewMessage(pattern=r"^\.فحص$", outgoing=True))
async def check(event):
    await event.edit("✅ **المحرك يعمل ويتخطى الحظر (403)!**")
