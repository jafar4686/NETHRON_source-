import asyncio
import yt_dlp
from telethon import events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.phone import JoinGroupCallRequest
from telethon.tl.types import InputPeerChannel

# استيراد ntgcalls بشكل صحيح
try:
    from ntgcalls import NTgCalls
except ImportError:
    print("❌ ntgcalls غير مثبت!")
    NTgCalls = None

# الحصول على العميل
try:
    from userbot import bot as client
except ImportError:
    try:
        import __main__
        client = __main__.client
    except:
        print("❌ لا يمكن العثور على عميل Telethon")
        client = None

# إنشاء NTgCalls بدون معامل
if client and NTgCalls:
    ntg = NTgCalls()
else:
    ntg = None

# قاموس لتخزين طابور التشغيل
queues = {}

async def init_ntg():
    """تهيئة NTgCalls"""
    if ntg:
        await ntg.start(client)
        print("✅ NTgCalls جاهز!")

@client.on(events.NewMessage(pattern=r'^\.ميوزك$'))
async def music_start(event):
    """تشغيل النظام"""
    if not event.out:
        return
    
    await event.edit('🎵 **نظام الميوزك يعمل!**\nاستخدم `.تشغيل رابط`')

@client.on(events.NewMessage(pattern=r'^\.تشغيل (.+)$'))
async def play_music(event):
    """تشغيل أغنية"""
    if not event.out or not ntg:
        return
    
    url = event.pattern_match.group(1).strip()
    chat_id = event.chat_id
    
    await event.edit('⏳ **جاري تحميل الصوت...**')
    
    try:
        # استخراج الرابط المباشر من YouTube
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extractaudio': True,
            'audioformat': 'mp3',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'مقطع صوت')
            audio_url = info.get('url')
            
            if not audio_url:
                # البحث عن تنسيق صوتي
                for fmt in info.get('formats', []):
                    if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                        audio_url = fmt.get('url')
                        break
        
        if not audio_url:
            await event.edit('❌ **لم أجد رابط صوتي مباشر**')
            return
        
        # الانضمام للمكالمة الصوتية
        try:
            # الحصول على معلومات المجموعة
            chat = await event.get_chat()
            if hasattr(chat, 'call'):
                # الانضمام للمكالمة
                await client(JoinGroupCallRequest(
                    call=chat.call,
                    params='',
                    muted=False,
                    video_stopped=False
                ))
        except:
            pass  # تجاهل خطأ الانضمام
        
        # تشغيل الصوت باستخدام NTgCalls
        await ntg.join_group_call(
            chat_id,
            stream_audio=audio_url
        )
        
        # حفظ في الطابور
        if chat_id not in queues:
            queues[chat_id] = []
        queues[chat_id].append({'url': url, 'title': title})
        
        await event.edit(f'🎶 **جاري التشغيل:**\n**{title}**')
        
    except Exception as e:
        await event.edit(f'❌ **خطأ:** `{str(e)[:100]}`')
        print(f"Play error: {e}")

@client.on(events.NewMessage(pattern=r'^\.ايقاف$'))
async def stop_music(event):
    """إيقاف التشغيل"""
    if not event.out or not ntg:
        return
    
    chat_id = event.chat_id
    
    try:
        await ntg.leave_group_call(chat_id)
        
        # مسح الطابور
        if chat_id in queues:
            del queues[chat_id]
        
        await event.edit('⏹️ **تم إيقاف الموسيقى**')
    except Exception as e:
        await event.edit(f'⚠️ **لا يوجد تشغيل نشط**')

@client.on(events.NewMessage(pattern=r'^\.مؤقت$'))
async def pause_music(event):
    """إيقاف مؤقت"""
    if not event.out or not ntg:
        return
    
    try:
        chat_id = event.chat_id
        await ntg.pause_stream(chat_id)
        await event.edit('⏸️ **تم الإيقاف المؤقت**')
    except:
        await event.edit('⚠️ **لا يمكن الإيقاف المؤقت**')

@client.on(events.NewMessage(pattern=r'^\.استمرار$'))
async def resume_music(event):
    """استئناف التشغيل"""
    if not event.out or not ntg:
        return
    
    try:
        chat_id = event.chat_id
        await ntg.resume_stream(chat_id)
        await event.edit('▶️ **تم الاستئناف**')
    except:
        await event.edit('⚠️ **لا يمكن الاستئناف**')

@client.on(events.NewMessage(pattern=r'^\.طابور$'))
async def show_queue(event):
    """عرض قائمة الانتظار"""
    if not event.out:
        return
    
    chat_id = event.chat_id
    
    if chat_id in queues and queues[chat_id]:
        text = '📋 **قائمة الانتظار:**\n'
        for i, item in enumerate(queues[chat_id][:10], 1):
            text += f'{i}. {item["title"]}\n'
        
        if len(queues[chat_id]) > 10:
            text += f'\n... و {len(queues[chat_id]) - 10} أغنية أخرى'
        
        await event.edit(text)
    else:
        await event.edit('📭 **الطابور فارغ**')

@client.on(events.NewMessage(pattern=r'^\.تخطي$'))
async def skip_music(event):
    """تخطي الأغنية الحالية"""
    if not event.out or not ntg:
        return
    
    chat_id = event.chat_id
    
    if chat_id in queues and len(queues[chat_id]) > 1:
        # حذف الحالية وإضافة التالية
        queues[chat_id].pop(0)
        
        if queues[chat_id]:
            next_item = queues[chat_id][0]
            await event.edit(f'⏭️ **جاري التخطي...**')
            
            # تشغيل التالية
            try:
                ydl_opts = {'format': 'bestaudio', 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(next_item['url'], download=False)
                    audio_url = info.get('url')
                
                await ntg.leave_group_call(chat_id)
                await ntg.join_group_call(chat_id, stream_audio=audio_url)
                
                await event.edit(f'🎵 **جاري التشغيل:** {next_item["title"]}')
            except Exception as e:
                await event.edit(f'❌ **خطأ في التخطي:** `{e}`')
    else:
        await event.edit('⚠️ **لا يوجد أغاني في الطابور للتخطي**')

@client.on(events.NewMessage(pattern=r'^\.معلومات$'))
async def music_info(event):
    """معلومات النظام"""
    if not event.out:
        return
    
    info_text = '🎵 **معلومات نظام الميوزك:**\n'
    info_text += f'• المكتبة: {"✅ NTgCalls" if ntg else "❌ غير مثبت"}\n'
    info_text += f'• العميل: {"✅ جاهز" if client and client.is_connected() else "❌ غير متصل"}\n'
    
    chat_id = event.chat_id
    if chat_id in queues:
        info_text += f'• الطابور: {len(queues[chat_id])} أغنية\n'
    else:
        info_text += '• الطابور: فارغ\n'
    
    info_text += '\n**الأوامر:**\n'
    info_text += '`.تشغيل رابط` - تشغيل أغنية\n'
    info_text += '`.ايقاف` - إيقاف التشغيل\n'
    info_text += '`.مؤقت` / `.استمرار` - إيقاف/استئناف\n'
    info_text += '`.تخطي` - تخطي الأغنية\n'
    info_text += '`.طابور` - عرض قائمة الانتظار\n'
    
    await event.edit(info_text)

# حدث عند انتهاء التشغيل
@ntg.on_stream_end()
async def on_stream_end(chat_id: int):
    """عند انتهاء الأغنية"""
    print(f"انتهت الأغنية في {chat_id}")
    
    if chat_id in queues and queues[chat_id]:
        # حذف الأغنية المنتهية
        if queues[chat_id]:
            queues[chat_id].pop(0)
        
        # إذا بقي أغاني في الطابور، شغل التالية
        if queues[chat_id]:
            next_item = queues[chat_id][0]
            try:
                ydl_opts = {'format': 'bestaudio', 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(next_item['url'], download=False)
                    audio_url = info.get('url')
                
                await ntg.join_group_call(chat_id, stream_audio=audio_url)
            except:
                pass

# تهيئة النظام عند التشغيل
async def setup_music():
    """تهيئة نظام الميوزك"""
    if client and ntg:
        await init_ntg()
        print("🎵 نظام الميوزك جاهز للتشغيل!")
    else:
        print("❌ تعذر تهيئة نظام الميوزك")

# إذا تم تشغيل الملف مباشرة
if __name__ == "__main__":
    if client:
        client.loop.create_task(setup_music())
