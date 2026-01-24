import __main__
from telethon import events
import yt_dlp
import os
import asyncio

# الوصول للكلاينت المعرف في الملف الرئيسي لسورس نيثرون
client = __main__.client

# ─────────────────── [ قائمة الأوامر م5 ] ───────────────────

@client.on(events.NewMessage(pattern=r"^\.م5$", outgoing=True))
async def m5_menu(event):
    m5_text = (
        "★────────☭────────★\n"
        "   ☭ • 𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 • ☭\n"
        "         • قـسـم الـتـحـمـيـل •\n"
        "★────────☭────────★\n\n"
        "📥 **أوامر التحميل المباشرة:**\n\n"
        "• `.بحث يوت` (رابط الفيديو)\n"
        "➥ تحميل فيديو + بصمة صوتية\n\n"
        "• `.بحث تيك` (رابط الفيديو)\n"
        "➥ تحميل تيك توك بدون حقوق\n\n"
        "★────────☭────────★\n"
        "💬 **ملاحظة:** يتم الحذف تلقائياً بعد الإرسال."
    )
    try:
        await event.edit(m5_text)
    except Exception as e:
        print(f"Error in m5: {e}")

# ─────────────────── [ تحميل يوتيوب ] ───────────────────

@client.on(events.NewMessage(pattern=r"^\.بحث يوت (.*)", outgoing=True))
async def youtube_download(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري جلب الفيديو.. انتظر ثواني**")
    
    # إنشاء اسم ملف مؤقت باستخدام ID الرسالة لتجنب التكرار
    v_file = f"y_video_{event.id}.mp4"

    ydl_opts = {
        'format': 'best',
        'outtmpl': v_file,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Video')

        await event.edit("🚀 **جاري الرفع الآن..**")
        
        # إرسال الفيديو أولاً
        await event.client.send_file(event.chat_id, v_file, caption=f"🎬 **يوتيوب:** `{title}`")
        
        # إرسال الصوت كبصمة
        await event.client.send_file(event.chat_id, v_file, voice_note=True)
        
        # حذف الملف فوراً لتوفير مساحة السيرفر
        if os.path.exists(v_file):
            os.remove(v_file)
            
        await event.delete()

    except Exception as e:
        if os.path.exists(v_file): os.remove(v_file)
        await event.edit(f"❌ **خطأ يوتيوب:**\n`{str(e)[:150]}`")

# ─────────────────── [ تحميل تيك توك ] ───────────────────

@client.on(events.NewMessage(pattern=r"^\.بحث تيك (.*)", outgoing=True))
async def tiktok_download(event):
    url = event.pattern_match.group(1).strip()
    await event.edit("⏳ **جاري سحب فيديو تيك توك..**")
    
    t_file = f"t_video_{event.id}.mp4"
    ydl_opts = {
        'outtmpl': t_file, 
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        await event.client.send_file(event.chat_id, t_file, caption="📱 **تيك توك نيثرون**")
        
        # الحذف بعد الإرسال
        if os.path.exists(t_file):
            os.remove(t_file)
        await event.delete()

    except Exception as e:
        if os.path.exists(t_file): os.remove(t_file)
        await event.edit(f"❌ **خطأ تيك توك:**\n`{str(e)[:150]}`")
