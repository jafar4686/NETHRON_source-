import __main__
from telethon import events
import yt_dlp
import os
import time

# الوصول للكلاينت من ملف المين
client = __main__.client

@client.on(events.NewMessage(pattern=r"^\.بحث يوت (.*)", outgoing=True))
async def yut_dl(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري سحب الفيديو والوصف...**")
    
    # اسم ملف مؤقت مع timestamp لتجنب التعارض
    timestamp = int(time.time())
    v_file = f"temp_{event.id}_{timestamp}.mp4"

    ydl_opts = {
        'format': 'best[height<=720]',  # جودة 720p كحد أقصى
        'outtmpl': v_file,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'referer': 'https://www.youtube.com/',
        'origin': 'https://www.youtube.com',
        # إعدادات مهمة لتجنب 403
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],  # استخدام عميل مختلف
            }
        },
        'sleep_interval_requests': 2,  # تقليل الضغط على السيرفر
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 1. جلب المعلومات والوصف
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'لا يوجد عنوان')
            description = info.get('description', 'لا يوجد وصف')[:300]

        # 2. إرسال الفيديو مع الوصف في الكابشن
        caption = f"🎬 **العنوان:** `{title}`\n\n📝 **الوصف:**\n`{description}...`"
        
        await event.edit("🚀 **جاري الرفع...**")
        
        # التحقق من حجم الملف قبل الإرسال
        if os.path.exists(v_file) and os.path.getsize(v_file) > 0:
            await event.client.send_file(
                event.chat_id, 
                v_file, 
                caption=caption,
                supports_streaming=True
            )
        else:
            raise Exception("الملف غير موجود أو فارغ")
        
        # 3. حذف الملف
        if os.path.exists(v_file):
            os.remove(v_file)
        
        await event.delete()

    except Exception as e:
        if os.path.exists(v_file): 
            os.remove(v_file)
        await event.edit(f"❌ **الخطأ:** {str(e)[:150]}")

@client.on(events.NewMessage(pattern=r"^\.بحث تيك (.*)", outgoing=True))
async def tik_dl(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **سحب تيك توك...**")
    
    timestamp = int(time.time())
    t_file = f"tik_{event.id}_{timestamp}.mp4"
    
    # إعدادات خاصة لتيك توك
    ydl_opts = {
        'outtmpl': t_file,
        'quiet': True,
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            'Referer': 'https://www.tiktok.com/',
        },
        'extractor_args': {
            'tiktok': {
                'app_version': '29.5.0',
                'manifest_app_version': '29.5.0',
            }
        },
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            desc = info.get('description', 'تيك توك')[:200]
        
        if os.path.exists(t_file) and os.path.getsize(t_file) > 0:
            await event.client.send_file(
                event.chat_id, 
                t_file, 
                caption=f"📱 `{desc}`",
                supports_streaming=True
            )
            await event.delete()
        else:
            raise Exception("ملف التيك توك غير موجود أو فارغ")
            
    except Exception as e:
        await event.edit(f"❌ **خطأ تيك توك:** {str(e)[:100]}")
    finally:
        if os.path.exists(t_file): 
            os.remove(t_file)
