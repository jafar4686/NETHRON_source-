import __main__
import asyncio
import yt_dlp
from telethon import events
from ntgcalls import NTgCalls, InputMode  # ✅ استيراد صحيح
# ملاحظة: StreamMode موجود في ntgcalls

# استدعاء الحساب الرئيسي
client = __main__.client
# محرك الصوت
ntg = NTgCalls(client)

# إذا StreamMode ما يشتغل، استخدم هذا:
from ntgcalls import MediaStream

@client.on(events.NewMessage(pattern=r"^\.ميوزك$"))
async def start_music_engine(event):
    if not event.out: 
        return
    await event.edit("✅ **نظام الميوزك (NTgCalls) جاهز!**")

@client.on(events.NewMessage(pattern=r"^\.تشغيل (.+)$"))
async def play_music(event):
    if not event.out: 
        return
    
    url = event.pattern_match.group(1).strip()
    chat_id = event.chat_id
    
    await event.edit(f"🎵 **جاري التحميل...**")
    
    try:
        # تحميل معلومات الصوت
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info.get('url')
            title = info.get('title', 'مقطع صوت')
        
        if not audio_url:
            await event.edit("❌ **ماقدرش أحصل على رابط الصوت**")
            return
        
        # تشغيل الصوت
        # الطريقة المبسطة:
        await ntg.join_group_call(
            chat_id,
            media_stream=MediaStream(
                audio_path=audio_url,
                video_path=None
            )
        )
        
        await event.edit(f"▶️ **جاري التشغيل:**\n**{title}**")
        
    except Exception as e:
        await event.edit(f"❌ **خطأ:**\n`{str(e)[:100]}`")
        print(f"خطأ: {e}")

@client.on(events.NewMessage(pattern=r"^\.ايقاف$"))
async def stop_music(event):
    if not event.out: 
        return
    
    chat_id = event.chat_id
    
    try:
        await ntg.leave_group_call(chat_id)
        await event.edit("🛑 **تم إيقاف الموسيقى**")
    except Exception as e:
        await event.edit(f"⚠️ **خطأ:**\n`{e}`")            del queues[chat_id]
        
        await event.edit("🛑 **تم إيقاف الموسيقى ومسح الطابور**")
    except Exception as e:
        await event.edit(f"⚠️ **لا يوجد تشغيل نشط أو خطأ:**\n`{e}`")

@client.on(events.NewMessage(pattern=r"^\.مؤقت$"))
async def pause_music(event):
    if not event.out: 
        return
    
    try:
        chat_id = event.chat_id
        # مؤقت - ntgcalls ماعنده pause مباشر، نسوي workaround
        await ntg.pause(chat_id)
        await event.edit("⏸️ **تم إيقاف التشغيل مؤقتاً**")
    except:
        await event.edit("⚠️ **ما أقدر أوقف مؤقتاً**")

@client.on(events.NewMessage(pattern=r"^\.استمرار$"))
async def resume_music(event):
    if not event.out: 
        return
    
    try:
        chat_id = event.chat_id
        # استمرار
        await ntg.resume(chat_id)
        await event.edit("▶️ **تم استئناف التشغيل**")
    except:
        await event.edit("⚠️ **ما أقدر أستأنف التشغيل**")

@client.on(events.NewMessage(pattern=r"^\.تخطي$"))
async def skip_music(event):
    if not event.out: 
        return
    
    chat_id = event.chat_id
    
    if chat_id in queues and queues[chat_id]:
        # تخطي للأغنية التالية في الطابور
        queues[chat_id].pop(0)
        
        if queues[chat_id]:
            next_url = queues[chat_id][0]
            # تشغيل التالية
            await play_music_from_url(event, next_url, is_skip=True)
            await event.edit("⏭️ **تم تخطي الأغنية**")
        else:
            await ntg.leave_group_call(chat_id)
            await event.edit("⏭️ **تم تخطي الأغنية - الطابور فارغ**")
    else:
        await event.edit("⚠️ **مافي أغاني في الطابور للتخطي**")

async def play_music_from_url(event, url, is_skip=False):
    """دالة مساعدة للتشغيل"""
    chat_id = event.chat_id
    
    try:
        ydl_opts = {'format': 'bestaudio', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info.get('url')
            title = info.get('title', 'مقطع صوت')
        
        if audio_url:
            await ntg.join_group_call(
                chat_id,
                input_mode=InputMode.Stream(audio_url),
                stream_mode=StreamMode().shell_stream(
                    'ffmpeg -re -i pipe:0 -f s16le -ac 2 -ar 48000 pipe:1'
                )
            )
            
            if not is_skip:
                await event.edit(f"▶️ **جاري التشغيل:** {title}")
    except Exception as e:
        if not is_skip:
            await event.edit(f"❌ خطأ: {e}")

@client.on(events.NewMessage(pattern=r"^\.طابور$"))
async def show_queue(event):
    if not event.out: 
        return
    
    chat_id = event.chat_id
    
    if chat_id in queues and queues[chat_id]:
        queue_text = "📋 **قائمة الانتظار:**\n"
        for i, url in enumerate(queues[chat_id][:10], 1):
            try:
                ydl_opts = {'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'عنوان غير معروف')
                queue_text += f"{i}. {title}\n"
            except:
                queue_text += f"{i}. {url}\n"
        
        if len(queues[chat_id]) > 10:
            queue_text += f"\n... و {len(queues[chat_id]) - 10} أغنية أخرى"
        
        await event.edit(queue_text)
    else:
        await event.edit("📭 **الطابور فارغ**")

@client.on(events.NewMessage(pattern=r"^\.اضف (.+)$"))
async def add_to_queue(event):
    if not event.out: 
        return
    
    url = event.pattern_match.group(1).strip()
    chat_id = event.chat_id
    
    if chat_id not in queues:
        queues[chat_id] = []
    
    queues[chat_id].append(url)
    
    try:
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'مقطع صوت')
        
        await event.edit(f"➕ **تمت الإضافة للطابور:**\n{title}\n📊 المكان: {len(queues[chat_id])}")
    except:
        await event.edit(f"➕ **تمت الإضافة للطابور:**\n{url}")

@client.on(events.NewMessage(pattern=r"^\.حذف (\d+)$"))
async def remove_from_queue(event):
    if not event.out: 
        return
    
    try:
        index = int(event.pattern_match.group(1)) - 1
        chat_id = event.chat_id
        
        if chat_id in queues and 0 <= index < len(queues[chat_id]):
            removed = queues[chat_id].pop(index)
            await event.edit(f"🗑️ **تم حذف العنصر رقم {index+1} من الطابور**")
        else:
            await event.edit("⚠️ **رقم غير صحيح أو الطابور فارغ**")
    except:
        await event.edit("⚠️ **استخدم `.حذف رقم`**")

@client.on(events.NewMessage(pattern=r"^\.بحث (.+)$"))
async def search_youtube(event):
    if not event.out: 
        return
    
    query = event.pattern_match.group(1).strip()
    await event.edit(f"🔍 **جاري البحث عن:** {query}")
    
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
                response = "🎵 **نتائج البحث:**\n"
                
                for i, entry in enumerate(results, 1):
                    title = entry.get('title', 'بدون عنوان')
                    url = f"https://youtube.com/watch?v={entry.get('id', '')}"
                    duration = entry.get('duration', 0)
                    
                    if duration:
                        duration_str = f"{duration//60}:{duration%60:02d}"
                    else:
                        duration_str = "غير معروف"
                    
                    response += f"{i}. **{title}**\n   ⏱️ {duration_str}\n   🔗 `{url}`\n\n"
                
                response += "**استخدم `.تشغيل رقم` لتشغيل النتيجة**"
                await event.edit(response)
            else:
                await event.edit("❌ **ما لقيت نتائج**")
    except Exception as e:
        await event.edit(f"❌ **خطأ في البحث:**\n`{e}`")

@client.on(events.NewMessage(pattern=r"^\.حجم (\d+)$"))
async def set_volume(event):
    if not event.out: 
        return
    
    try:
        volume = int(event.pattern_match.group(1))
        if 1 <= volume <= 200:
            chat_id = event.chat_id
            # ntgcalls ماعنده volume control مباشر
            # ممكن نضيف filter لـ ffmpeg
            await event.edit(f"🔊 **تم ضبط الصوت على:** {volume}%\n⚠️ هذه الخاصية تحت التطوير")
        else:
            await event.edit("⚠️ **استخدم رقم بين 1 و 200**")
    except:
        await event.edit("⚠️ **استخدم `.حجم رقم`**")

@client.on(events.NewMessage(pattern=r"^\.معلومات$"))
async def player_info(event):
    if not event.out: 
        return
    
    chat_id = event.chat_id
    
    info_text = "🎵 **معلومات المشغل:**\n"
    info_text += f"• **المكتبة:** NTgCalls\n"
    info_text += f"• **المحادثة:** {chat_id}\n"
    
    if chat_id in queues:
        info_text += f"• **عدد الأغاني في الطابور:** {len(queues[chat_id])}\n"
    else:
        info_text += "• **الطابور:** فارغ\n"
    
    info_text += "\n**الأوامر المتاحة:**\n"
    info_text += "`.تشغيل رابط` - تشغيل أغنية\n"
    info_text += "`.ايقاف` - إيقاف التشغيل\n"
    info_text += "`.مؤقت` / `.استمرار` - إيقاف/استئناف\n"
    info_text += "`.تخطي` - تخطي الأغنية\n"
    info_text += "`.طابور` - عرض قائمة الانتظار\n"
    info_text += "`.اضف رابط` - إضافة للطابور\n"
    info_text += "`.بحث كلمة` - بحث في يوتيوب\n"
    
    await event.edit(info_text)

# حدث عند اكتمال التشغيل
@ntg.on_stream_end()
async def stream_end_handler(chat_id: int):
    """عند ما تنتهي الأغنية الحالية"""
    print(f"انتهت الأغنية في {chat_id}")
    
    if chat_id in queues and queues[chat_id]:
        # حذف الأغنية اللي خلصت
        if queues[chat_id]:
            queues[chat_id].pop(0)
        
        # إذا في أغاني أخرى في الطابور، نشغلها
        if queues[chat_id]:
            next_url = queues[chat_id][0]
            try:
                ydl_opts = {'format': 'bestaudio', 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(next_url, download=False)
                    audio_url = info.get('url')
                
                if audio_url:
                    await ntg.join_group_call(
                        chat_id,
                        input_mode=InputMode.Stream(audio_url),
                        stream_mode=StreamMode().shell_stream(
                            'ffmpeg -re -i pipe:0 -f s16le -ac 2 -ar 48000 pipe:1'
                        )
                    )
            except:
                pass
