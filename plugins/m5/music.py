import __main__
from telethon import events
import yt_dlp
import os

# الوصول للكلاينت من ملف المين
client = __main__.client

@client.on(events.NewMessage(pattern=r"^\.بحث يوت (.*)", outgoing=True))
async def yut_dl(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري سحب الفيديو والوصف...**")
    
    # اسم ملف مؤقت يختفي فوراً
    v_file = f"temp_{event.id}.mp4"

    ydl_opts = {
        'format': 'best',
        'outtmpl': v_file, # تحميل مؤقت لتجنب خطأ cURL
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 1. جلب المعلومات والوصف
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'لا يوجد عنوان')
            description = info.get('description', 'لا يوجد وصف')[:300] # أول 300 حرف

        # 2. إرسال الفيديو مع الوصف في الكابشن
        caption = f"🎬 **العنوان:** `{title}`\n\n📝 **الوصف:**\n`{description}...`"
        
        await event.edit("🚀 **جاري الرفع...**")
        await event.client.send_file(event.chat_id, v_file, caption=caption)
        
        # 3. حذف الملف فوراً (ماراح يحفظ ولا ياخذ مساحة)
        if os.path.exists(v_file):
            os.remove(v_file)
        
        await event.delete()

    except Exception as e:
        if os.path.exists(v_file): os.remove(v_file)
        await event.edit(f"❌ **الخطأ:** السيرفر محظور أو الرابط غلط.\n`{str(e)[:150]}`")

@client.on(events.NewMessage(pattern=r"^\.بحث تيك (.*)", outgoing=True))
async def tik_dl(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **سحب تيك توك...**")
    t_file = f"tik_{event.id}.mp4"
    try:
        with yt_dlp.YoutubeDL({'outtmpl': t_file, 'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=True)
            desc = info.get('description', 'تيك توك')
        
        await event.client.send_file(event.chat_id, t_file, caption=f"📱 `{desc}`")
        if os.path.exists(t_file): os.remove(t_file)
        await event.delete()
    except Exception as e:
        if os.path.exists(t_file): os.remove(t_file)
        await event.edit(f"❌ **خطأ:** `{str(e)[:100]}`")
