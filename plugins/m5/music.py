import asyncio
import yt_dlp
from telethon import events
from ntgcalls import NTgCalls

# العميل
try:
    from userbot import bot as client
except:
    import __main__
    client = __main__.client

ntg = NTgCalls(client)

@client.on(events.NewMessage(pattern=r'^\.ميوزك$'))
async def test_music(event):
    await event.edit('🎵 **النظام جاهز!**')

@client.on(events.NewMessage(pattern=r'^\.تشغيل (.+)$'))
async def test_play(event):
    url = event.pattern_match.group(1)
    await event.edit(f'⏳ **جاري تشغيل:** {url}')
    
    try:
        # استخراج الرابط
        ydl_opts = {'format': 'bestaudio', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
        
        # تشغيل
        await ntg.join_group_call(event.chat_id, stream_audio=audio_url)
        await event.edit('✅ **جاري التشغيل الآن!**')
    except Exception as e:
        await event.edit(f'❌ خطأ: {e}')

@client.on(events.NewMessage(pattern=r'^\.ايقاف$'))
async def test_stop(event):
    await ntg.leave_group_call(event.chat_id)
    await event.edit('⏹️ **تم الإيقاف**')

# بدء NTgCalls
async def start():
    await ntg.start()
    print("✅ NTgCalls بدأ!")

if client:
    client.loop.create_task(start())
