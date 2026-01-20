import asyncio
import yt_dlp
from telethon import events
from ntgcalls import NTgCalls

# محاولة الحصول على العميل (Client) من السورس الرئيسي
try:
    import __main__
    client = __main__.client
except:
    client = None

# ✅ الطريقة الصحيحة للإصدار 2.0.7: لا نمرر client هنا
ntg = NTgCalls()

@client.on(events.NewMessage(pattern=r'^\.ميوزك$'))
async def music_test(event):
    if not event.out: return
    await event.edit('🎵 **نظام الميوزك (NTgCalls 2.0.7) جاهز الآن!**\nاستخدم `.تشغيل` + رابط.')

@client.on(events.NewMessage(pattern=r'^\.تشغيل (.+)$'))
async def play_music(event):
    if not event.out: return
    url = event.pattern_match.group(1).strip()
    chat_id = event.chat_id
    
    await event.edit('⏳ **جاري استخراج رابط الصوت...**')
    
    try:
        # استخراج الرابط المباشر
        ydl_opts = {'format': 'bestaudio', 'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            title = info.get('title', 'أغنية')

        # ✅ في الإصدار 2.x نستخدم الانضمام والتشغيل هكذا:
        # ملاحظة: المكتبة تتعرف على الـ client تلقائياً من خلال الجلسة النشطة في السيرفر
        await ntg.join_group_call(
            chat_id,
            path=audio_url,  # نستخدم path بدلاً من stream_audio في بعض تحديثات 2.x
        )
        
        await event.edit(f'✅ **بدأ التشغيل الآن:**\n`{title}`')
    except Exception as e:
        await event.edit(f'❌ خطأ أثناء التشغيل: `{str(e)}`')

@client.on(events.NewMessage(pattern=r'^\.ايقاف$'))
async def stop_music(event):
    if not event.out: return
    try:
        await ntg.leave_group_call(event.chat_id)
        await event.edit('⏹️ **تم إيقاف التشغيل ومغادرة المكالمة.**')
    except Exception as e:
        await event.edit(f'⚠️ خطأ في الإيقاف: `{e}`')

# ✅ تشغيل المحرك عند بدء البوت
async def start_engine():
    try:
        await ntg.start()
        print("✅ NTgCalls Engine Started!")
    except Exception as e:
        print(f"❌ Engine Error: {e}")

if client:
    client.loop.create_task(start_engine())
