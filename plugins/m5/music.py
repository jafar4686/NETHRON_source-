import __main__
from telethon import events
import yt_dlp
import os
import time
import random

# الوصول للكلاينت من ملف المين
client = __main__.client

@client.on(events.NewMessage(pattern=r"^\.بحث يوت (.*)", outgoing=True))
async def yut_dl(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري سحب الفيديو...**")
    
    # اسم ملف مؤقت
    timestamp = int(time.time())
    v_file = f"temp_yt_{timestamp}.mp4"

    # إعدادات متعددة المحاولات
    ydl_opts_list = [
        # محاولة 1: إعدادات بسيطة
        {
            'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            'outtmpl': v_file,
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'socket_timeout': 30,
            'retries': 5,
        },
        # محاولة 2: مع ترويسات
        {
            'format': 'worst[ext=mp4]',
            'outtmpl': v_file,
            'quiet': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.youtube.com/',
                'Origin': 'https://www.youtube.com',
            },
        },
        # محاولة 3: استخدام extractor مختلف
        {
            'format': 'best',
            'outtmpl': v_file,
            'quiet': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                    'player_skip': ['webpage'],
                }
            },
        }
    ]

    success = False
    last_error = ""
    
    for attempt, ydl_opts in enumerate(ydl_opts_list, 1):
        try:
            await event.edit(f"⏳ **المحاولة {attempt}/3...**")
            
            # إضافة تأخير عشوائي
            time.sleep(random.uniform(1, 3))
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # محاولة الحصول على معلومات بدون تحميل أولاً
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'لا يوجد عنوان')
                description = info.get('description', 'لا يوجد وصف')[:300]
                
                # الآن تحميل الفيديو
                await event.edit(f"📥 **جاري التحميل (المحاولة {attempt})...**")
                ydl.download([url])
            
            # التحقق من الملف
            if os.path.exists(v_file) and os.path.getsize(v_file) > 1024:  # أكبر من 1KB
                caption = f"🎬 **{title}**\n\n📝 {description}..."
                
                await event.edit("🚀 **جاري الرفع...**")
                await event.client.send_file(
                    event.chat_id,
                    v_file,
                    caption=caption,
                    supports_streaming=True,
                    video_note=False
                )
                
                success = True
                break
                
        except Exception as e:
            last_error = str(e)
            if os.path.exists(v_file):
                os.remove(v_file)
            continue

    # التنظيف
    if os.path.exists(v_file):
        os.remove(v_file)
    
    if success:
        await event.delete()
    else:
        await event.edit(f"❌ **فشل التحميل بعد 3 محاولات**\nآخر خطأ: `{last_error[:100]}`")

@client.on(events.NewMessage(pattern=r"^\.بحث تيك (.*)", outgoing=True))
async def tik_dl(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **سحب تيك توك...**")
    
    timestamp = int(time.time())
    t_file = f"tik_{timestamp}.mp4"
    
    try:
        # استخدام الأمر المباشر ل yt-dlp
        cmd = f'yt-dlp -f "best[ext=mp4]" --no-warnings --quiet -o "{t_file}" "{url}"'
        os.system(cmd)
        
        if os.path.exists(t_file) and os.path.getsize(t_file) > 1024:
            await event.client.send_file(
                event.chat_id,
                t_file,
                caption="📱 **تيك توك**",
                supports_streaming=True
            )
            await event.delete()
        else:
            # محاولة بديلة
            await event.edit("🔄 **جرب طريقة بديلة...**")
            alt_cmd = f'yt-dlp -f mp4 -o "{t_file}" "{url}"'
            os.system(alt_cmd)
            
            if os.path.exists(t_file):
                await event.client.send_file(event.chat_id, t_file)
                await event.delete()
            else:
                await event.edit("❌ **فشل تحميل تيك توك**")
                
    except Exception as e:
        await event.edit(f"❌ **خطأ:** {str(e)[:100]}")
    finally:
        if os.path.exists(t_file):
            os.remove(t_file)

@client.on(events.NewMessage(pattern=r"^\.تحديث$", outgoing=True))
async def update_ytdlp(event):
    """تحديث yt-dlp"""
    await event.edit("🔄 **جاري تحديث yt-dlp...**")
    try:
        os.system("pip install --upgrade yt-dlp")
        await event.edit("✅ **تم التحديث بنجاح!**")
    except Exception as e:
        await event.edit(f"❌ **فشل التحديث:** {str(e)}")
