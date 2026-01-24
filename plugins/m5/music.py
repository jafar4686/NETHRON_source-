import __main__
from telethon import events
import requests
import os
import io

# الوصول للكلاينت من ملف المين لنيثرون
client = __main__.client

# 1. قائمة الأوامر .م5
@client.on(events.NewMessage(pattern=r"^\.م5$", outgoing=True))
async def m5_menu(event):
    m5_text = (
        "★────────☭────────★\n"
        "   ☭ • 𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 • ☭\n"
        "         • الـتـحـمـيـل الـفـوري •\n"
        "★────────☭────────★\n\n"
        "📥 **أوامر التحميل (فيديو + وصف):**\n\n"
        "• `.بحث يوت` (الرابط)\n"
        "• `.بحث تيك` (الرابط)\n\n"
        "⚙️ يتم الرفع من الذاكرة مباشرة بدون حفظ."
    )
    await event.edit(m5_text)

# 2. تحميل يوتيوب (رفع مباشر لتجنب خطأ cURL)
@client.on(events.NewMessage(pattern=r"^\.بحث يوت (.*)", outgoing=True))
async def yut_dl(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري سحب وصف وفيديو يوتيوب...**")
    
    import yt_dlp
    # إعدادات لجلب الرابط المباشر
    ydl_opts = {'format': 'best', 'quiet': True, 'no_warnings': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            title = info.get('title', 'فيديو يوتيوب')
            description = info.get('description', 'لا يوجد وصف')[:300]

        if video_url:
            await event.edit("🚀 **جاري الرفع المباشر...**")
            caption = f"🎬 **العنوان:** `{title}`\n\n📝 **الوصف:**\n`{description}...`"
            # إرسال الفيديو مباشرة من الرابط لتجنب SendMediaRequest
            await event.client.send_file(event.chat_id, video_url, caption=caption)
            await event.delete()
        else:
            await event.edit("❌ فشل استخراج الرابط.")
            
    except Exception as e:
        await event.edit(f"❌ خطأ يوتيوب: `{str(e)[:100]}`")

# 3. تحميل تيك توك (باستخدام API ملفك القديم bot4.py)
@client.on(events.NewMessage(pattern=r"^\.بحث تيك (.*)", outgoing=True))
async def tik_dl(event):
    video_url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري سحب تيك توك والوصف...**")
    
    try:
        # نفس منطق API التحميل في ملفك bot4.py
        api_url = f"https://www.tikwm.com/api/?url={video_url}"
        response = requests.get(api_url, timeout=30)
        data = response.json()
        
        if data.get('code') == 0:
            video_data = data.get('data', {})
            play_url = video_data.get('play') # الرابط المباشر
            title = video_data.get('title', 'فيديو تيك توك') # العنوان
            
            if play_url:
                if play_url.startswith('//'): play_url = 'https:' + play_url
                
                await event.edit("🚀 **جاري الرفع...**")
                # إرسال الفيديو مع الوصف فوراً
                await event.client.send_file(
                    event.chat_id, 
                    play_url, 
                    caption=f"📱 **الوصف:**\n`{title}`"
                )
                await event.delete()
            else:
                await event.edit("❌ لم أجد رابط الفيديو.")
        else:
            await event.edit("❌ رابط غير صالح.")
            
    except Exception as e:
        await event.edit(f"❌ خطأ تيك توك: `{str(e)[:100]}`")
