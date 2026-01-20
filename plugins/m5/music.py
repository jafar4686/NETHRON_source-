import asyncio
import yt_dlp
from telethon import events
from ntgcalls import NTgCalls
from ntgcalls import InputMode

# في مالتي ترسيم مود، لازم نستدعي العميل بطريقة مختلفة
try:
    from userbot import bot
    client = bot
except:
    # إذا مالك userbot.py، جرب هذا
    import __main__
    if hasattr(__main__, 'client'):
        client = __main__.client
    else:
        # أو استخدم telethon مباشرة
        from telethon import TelegramClient
        import os
        client = TelegramClient(
            'bot',
            api_id=os.getenv('API_ID'),
            api_hash=os.getenv('API_HASH')
        )

# محرك الصوت
ntg = NTgCalls(client)

@client.on(events.NewMessage(pattern=r'^\.ميوزك$'))
async def music_handler(event):
    """دالة تفعيل النظام"""
    await event.edit('🎵 **نظام الميوزك جاهز!**\nاستخدم `.تشغيل رابط`')

@client.on(events.NewMessage(pattern=r'^\.تشغيل (.+)$'))
async def play_handler(event):
    """تشغيل أغنية"""
    if not event.is_private:
        url = event.pattern_match.group(1)
        chat_id = event.chat_id
        
        await event.edit('⏳ **جاري تحميل الصوت...**')
        
        try:
            # استخراج الرابط المباشر
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                audio_url = info.get('url')
                title = info.get('title', 'مقطع صوت')
                
                if not audio_url:
                    # جرب ناخذ أول رابط صوت
                    for fmt in info.get('formats', []):
                        if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                            audio_url = fmt.get('url')
                            break
            
            if not audio_url:
                await event.edit('❌ **مافيش رابط صوت مباشر**')
                return
            
            # تشغيل مع ffmpeg مباشرة
            await ntg.join_group_call(
                chat_id,
                input_mode=InputMode.Shell(
                    f'ffmpeg -i "{audio_url}" -f s16le -ar 48000 -ac 2 pipe:1'
                )
            )
            
            await event.edit(f'✅ **جاري التشغيل:**\n**{title}**')
            
        except Exception as e:
            await event.edit(f'❌ **خطأ:** `{str(e)[:50]}`')
            print(f"Play error: {e}")

@client.on(events.NewMessage(pattern=r'^\.ايقاف$'))
async def stop_handler(event):
    """إيقاف التشغيل"""
    if not event.is_private:
        chat_id = event.chat_id
        
        try:
            await ntg.leave_group_call(chat_id)
            await event.edit('⏹️ **تم الإيقاف**')
        except Exception as e:
            await event.edit(f'⚠️ **خطأ:** `{e}`')

@client.on(events.NewMessage(pattern=r'^\.تست$'))
async def test_handler(event):
    """اختبار النظام"""
    await event.edit('🎵 **اختبار NTgCalls:**\n'
                     '• العميل: ' + ('✅ جاهز' if client.is_connected() else '❌ غير متصل') + '\n'
                     '• المكتبة: NTgCalls ✅')

# دالة لبدء النظام
async def start_music_system():
    """تشغيل نظام الميوزك عند بدء البوت"""
    print("🎵 نظام الميوزك جاهز!")
    
    # أو يمكنك إرسال رسالة لمطور البوت
    try:
        await client.send_message('me', '🎵 **نظام الميوزك اشتغل بنجاح!**')
    except:
        pass

# إذا الكود في ملف مستقل، أضف هذا
if __name__ == "__main__":
    # ربط نظام الميوزك مع العميل
    client.loop.create_task(start_music_system())
