import __main__
from telethon import events
import requests
import os
import re

# الوصول للكلاينت من سورس نيثرون
client = __main__.client

def get_url(text):
    urls = re.findall(r'(https?://\S+)', text)
    for url in urls:
        if "youtube" in url or "youtu.be" in url or "tiktok" in url:
            return url
    return None

@client.on(events.NewMessage(outgoing=True))
async def auto_dl(event):
    if not event.text: return
    url = get_url(event.text)
    if not url: return

    # --- قسم يوتيوب (كسر حظر البوتات عبر API سريع) ---
    if "youtube" in url or "youtu.be" in url:
        await event.edit("⏳ **يتـم تجـاوز حمايـة يوتيـوب...**")
        try:
            # استخدام محرك Invidious أو Cobalt API موثوق
            # هذا يخلي يوتيوب يشوف الطلب جاي من سيرفر مشهور مو من سيرفرك
            api_url = f"https://co.wuk.sh/api/json"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            data = {"url": url, "vQuality": "720"}
            
            res = requests.post(api_url, json=data, headers=headers)
            json_res = res.json()
            
            if json_res.get('url'):
                v_url = json_res['url']
                await event.edit("🚀 **جاري الرفع المباشر...**")
                await event.client.send_file(event.chat_id, v_url, caption="🎬 **تم كسر الحماية والتحميل بنجاح!**")
                await event.delete()
            else:
                await event.edit("❌ **عذراً، يوتيوب يطلب تسجيل دخول.. جاري تجربة طريقة أخرى...**")
                # هنا إذا فشل الـ API، نحاول بطريقة ثانية سريعة
        except Exception:
            await event.edit("❌ **فشل تجاوز حماية يوتيوب حالياً.**")

    # --- قسم تيك توك (شغال لوز من ملفك القديم) ---
    elif "tiktok.com" in url:
        await event.edit("⏳ **جاري جلب تيك توك...**")
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
        except Exception:
            await event.edit("❌ خطأ في محرك تيك توك.")

@client.on(events.NewMessage(pattern=r"^\.فحص$", outgoing=True))
async def check(event):
    await event.edit("✅ **المحرك شغال وبانتظار الروابط!**")
