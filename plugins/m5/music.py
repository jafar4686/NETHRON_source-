import asyncio
import yt_dlp
from telethon import events
from telethon.tl.functions.phone import JoinGroupCallRequest
from telethon.tl.types import InputPeerChannel

# استيراد ntgcalls 2.x
try:
    from ntgcalls import NTgCalls
    from ntgcalls import AudioStream, VideoStream
    NTGCALLS_AVAILABLE = True
except ImportError as e:
    print(f"❌ تعذر استيراد ntgcalls: {e}")
    NTGCALLS_AVAILABLE = False
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

# إنشاء NTgCalls
if client and NTGCALLS_AVAILABLE:
    ntg = NTgCalls()
else:
    ntg = None

# قاموس لتخزين طابور التشغيل
queues = {}
active_calls = {}

async def init_ntg():
    """تهيئة NTgCalls"""
    if ntg:
        await ntg.start(client)
        print("✅ NTgCalls 2.0.7 جاهز!")
        return True
    return False

@client.on(events.NewMessage(pattern=r'^[\.!]ميوزك$'))
async def music_start(event):
    """تشغيل النظام"""
    if not event.out:
        return
    
    await event.edit('🎵 **نظام الميوزك يعمل (NTgCalls 2.0.7)!**\nاستخدم `.تشغيل رابط`')

@client.on(events.NewMessage(pattern=r'^[\.!]تشغيل (.+)$'))
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
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'مقطع صوت')
            duration = info.get('duration', 0)
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
            chat = await event.get_chat()
            if hasattr(chat, 'call') and chat.call:
                # الانضمام للمكالمة
                await client(JoinGroupCallRequest(
                    call=chat.call,
                    params='',
                    muted=False,
                    video_stopped=False
                ))
        except Exception as e:
            print(f"⚠️ خطأ في الانضمام للمكالمة: {e}")
        
        # تشغيل الصوت باستخدام NTgCalls 2.x
        # الطريقة الجديدة مع AudioStream
        stream = AudioStream(
            input_mode='shell',
            input=f'ffmpeg -re -i "{audio_url}" -f s16le -ar 48000 -ac 2 -'
        )
        
        await ntg.join_group_call(
            chat_id,
            stream=stream
        )
        
        # حفظ في الطابور
        if chat_id not in queues:
            queues[chat_id] = []
        
        queues[chat_id].append({
            'url': url,
            'title': title,
            'audio_url': audio_url,
            'duration': duration
        })
        
        # حفظ المكالمة النشطة
        active_calls[chat_id] = True
        
        # عرض معلومات التشغيل
        mins = duration // 60
        secs = duration % 60
        duration_str = f"{mins}:{secs:02d}" if duration > 0 else "مباشر"
        
        await event.edit(f'🎶 **جاري التشغيل:**\n**{title}**\n⏱️ المدة: {duration_str}')
        
    except yt_dlp.utils.DownloadError as e:
        await event.edit(f'❌ **خطأ في تحميل الفيديو:**\n`{str(e)[:80]}`')
    except Exception as e:
        await event.edit(f'❌ **خطأ غير متوقع:**\n`{str(e)[:80]}`')
        print(f"Play error: {e}")

@client.on(events.NewMessage(pattern=r'^[\.!]ايقاف$'))
async def stop_music(event):
    """إيقاف التشغيل"""
    if not event.out or not ntg:
        return
    
    chat_id = event.chat_id
    
    try:
        await ntg.leave_group_call(chat_id)
        
        # مسح الطابور والمكالمة النشطة
        if chat_id in queues:
            del queues[chat_id]
        if chat_id in active_calls:
            del active_calls[chat_id]
        
        await event.edit('⏹️ **تم إيقاف الموسيقى**')
    except Exception as e:
        await event.edit(f'⚠️ **خطأ في الإيقاف:**\n`{e}`')

@client.on(events.NewMessage(pattern=r'^[\.!]مؤقت$'))
async def pause_music(event):
    """إيقاف مؤقت"""
    if not event.out or not ntg:
        return
    
    chat_id = event.chat_id
    
    try:
        await ntg.pause(chat_id)
        await event.edit('⏸️ **تم الإيقاف المؤقت**')
    except Exception as e:
        await event.edit(f'⚠️ **لا يمكن الإيقاف المؤقت:**\n`{e}`')

@client.on(events.NewMessage(pattern=r'^[\.!]استمرار$'))
async def resume_music(event):
    """استئناف التشغيل"""
    if not event.out or not ntg:
        return
    
    chat_id = event.chat_id
    
    try:
        await ntg.resume(chat_id)
        await event.edit('▶️ **تم الاستئناف**')
    except Exception as e:
        await event.edit(f'⚠️ **لا يمكن الاستئناف:**\n`{e}`')

@client.on(events.NewMessage(pattern=r'^[\.!]طابور$'))
async def show_queue(event):
    """عرض قائمة الانتظار"""
    if not event.out:
        return
    
    chat_id = event.chat_id
    
    if chat_id in queues and queues[chat_id]:
        text = '📋 **قائمة الانتظار:**\n\n'
        for i, item in enumerate(queues[chat_id][:10], 1):
            duration = item.get('duration', 0)
            mins = duration // 60
            secs = duration % 60
            duration_str = f"{mins}:{secs:02d}" if duration > 0 else ""
            
            text += f'{i}. **{item["title"]}**'
            if duration_str:
                text += f' ({duration_str})'
            text += '\n'
        
        if len(queues[chat_id]) > 10:
            text += f'\n... و {len(queues[chat_id]) - 10} أغنية أخرى'
        
        await event.edit(text)
    else:
        await event.edit('📭 **الطابور فارغ**')

@client.on(events.NewMessage(pattern=r'^[\.!]تخطي$'))
async def skip_music(event):
    """تخطي الأغنية الحالية"""
    if not event.out or not ntg:
        return
    
    chat_id = event.chat_id
    
    if chat_id in queues and len(queues[chat_id]) > 1:
        # حذف الحالية
        current = queues[chat_id].pop(0)
        
        if queues[chat_id]:
            next_item = queues[chat_id][0]
            await event.edit(f'⏭️ **جاري التخطي إلى:**\n{next_item["title"]}')
            
            # تشغيل التالية
            try:
                stream = AudioStream(
                    input_mode='shell',
                    input=f'ffmpeg -re -i "{next_item["audio_url"]}" -f s16le -ar 48000 -ac 2 -'
                )
                
                await ntg.leave_group_call(chat_id)
                await asyncio.sleep(1)
                await ntg.join_group_call(chat_id, stream=stream)
                
                await event.edit(f'🎵 **جاري التشغيل الآن:**\n{next_item["title"]}')
            except Exception as e:
                await event.edit(f'❌ **خطأ في التخطي:**\n`{e}`')
    else:
        await event.edit('⚠️ **لا يوجد أغاني في الطابور للتخطي**')

@client.on(events.NewMessage(pattern=r'^[\.!]بحث (.+)$'))
async def search_youtube(event):
    """بحث في يوتيوب"""
    if not event.out:
        return
    
    query = event.pattern_match.group(1).strip()
    
    await event.edit(f'🔍 **جاري البحث عن:** {query}')
    
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'default_search': 'ytsearch5'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            
            if 'entries' in info:
                results = info['entries'][:5]
                text = '🎵 **نتائج البحث:**\n\n'
                
                for i, entry in enumerate(results, 1):
                    title = entry.get('title', 'بدون عنوان')
                    video_id = entry.get('id', '')
                    duration = entry.get('duration', 0)
                    
                    if video_id:
                        url = f"https://youtube.com/watch?v={video_id}"
                    else:
                        url = entry.get('url', '')
                    
                    mins = duration // 60
                    secs = duration % 60
                    duration_str = f"{mins}:{secs:02d}" if duration > 0 else "مباشر"
                    
                    text += f'{i}. **{title}**\n'
                    text += f'   ⏱️ {duration_str} | 🔗 `{url}`\n\n'
                
                text += '**استخدم `.تشغيل رقم` لتشغيل النتيجة**'
                await event.edit(text)
            else:
                await event.edit('❌ **لم أجد نتائج**')
    except Exception as e:
        await event.edit(f'❌ **خطأ في البحث:**\n`{e}`')

@client.on(events.NewMessage(pattern=r'^[\.!]تشغيل (\d+)$'))
async def play_from_search(event):
    """تشغيل نتيجة بحث برقم"""
    if not event.out:
        return
    
    try:
        index = int(event.pattern_match.group(1)) - 1
        
        # البحث في آخر رسالة بحث (هذا مثال مبسط)
        # في الواقع تحتاج لحفظ نتائج البحث لكل مستخدم
        await event.edit('⚠️ **هذه الميزة تحتاج تطوير إضافي**\nاستخدم `.تشغيل رابط_كامل` مباشرة')
    except:
        await event.edit('❌ **استخدم `.تشغيل رقم` بعد البحث**')

@client.on(events.NewMessage(pattern=r'^[\.!]معلومات$'))
async def music_info(event):
    """معلومات النظام"""
    if not event.out:
        return
    
    info_text = '🎵 **معلومات نظام الميوزك:**\n\n'
    info_text += f'• المكتبة: {"✅ NTgCalls 2.0.7" if NTGCALLS_AVAILABLE else "❌ غير مثبت"}\n'
    info_text += f'• العميل: {"✅ متصل" if client and client.is_connected() else "❌ غير متصل"}\n'
    
    chat_id = event.chat_id
    if chat_id in queues:
        info_text += f'• الطابور: {len(queues[chat_id])} أغنية\n'
    else:
        info_text += '• الطابور: فارغ\n'
    
    info_text += f'• مكالمات نشطة: {len(active_calls)}\n'
    
    info_text += '\n**الأوامر المتاحة:**\n'
    info_text += '`.تشغيل رابط` - تشغيل أغنية\n'
    info_text += '`.ايقاف` - إيقاف التشغيل\n'
    info_text += '`.مؤقت` / `.استمرار` - إيقاف/استئناف\n'
    info_text += '`.تخطي` - تخطي الأغنية\n'
    info_text += '`.طابور` - عرض قائمة الانتظار\n'
    info_text += '`.بحث كلمة` - بحث في يوتيوب\n'
    info_text += '`.معلومات` - عرض هذه المعلومات\n'
    
    await event.edit(info_text)

@client.on(events.NewMessage(pattern=r'^[\.!]مساعدة$'))
async def music_help(event):
    """مساعدة"""
    help_text = '🎵 **مساعدة نظام الميوزك:**\n\n'
    help_text += '**كيفية الاستخدام:**\n'
    help_text += '1. أضف البوت إلى مجموعة صوتية\n'
    help_text += '2. ابدأ مكالمة صوتية في المجموعة\n'
    help_text += '3. استخدم `.تشغيل رابط_يوتيوب`\n\n'
    help_text += '**أمثلة:**\n'
    help_text += '`.تشغيل https://youtu.be/xxxx`\n'
    help_text += '`.بحث أغنية حب`\n'
    help_text += '`.طابور`\n'
    
    await event.edit(help_text)

# تهيئة النظام عند التشغيل
async def setup_music():
    """تهيئة نظام الميوزك"""
    if client and NTGCALLS_AVAILABLE:
        success = await init_ntg()
        if success:
            print("🎵 نظام الميوزك جاهز للتشغيل!")
            return True
        else:
            print("❌ تعذر تهيئة NTgCalls")
            return False
    else:
        print("❌ تعذر تهيئة نظام الميوزك")
        return False

# إذا تم تشغيل الملف مباشرة
if __name__ == "__main__":
    if client:
        import asyncio
        asyncio.run(setup_musi        await event.edit(f'❌ **خطأ:** `{str(e)[:100]}`')
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
