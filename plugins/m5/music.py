import __main__
from telethon import events
from ntgcalls import NTgCalls
from ntgcalls import StreamStatus
import asyncio

# استدعاء الحساب الرئيسي
client = __main__.client
# محرك الصوت
ntg = NTgCalls(client)

@client.on(events.NewMessage(pattern=r"^\.ميوزك$"))
async def start_music_engine(event):
    if not event.out: return
    await event.edit("🔄 **جاري تشغيل محرك الصوت (NTgCalls)...**")
    try:
        # بدلاً من pygcalls.start() نستخدم النموذج الخاص بـ ntgcalls
        # المحرك يعمل تلقائياً عند الحاجة
        await event.edit("✅ **نظام الميوزك جاهز الآن!**\n🎶 يمكنك استخدام `.تشغيل` مع رابط يوتيوب.")
    except Exception as e:
        await event.edit(f"❌ حدث خطأ في التشغيل: {e}")

@client.on(events.NewMessage(pattern=r"^\.ايقاف$"))
async def stop_music(event):
    if not event.out: return
    try:
        # إيقاف كل المكالمات النشطة
        await ntg.leave_group_call(event.chat_id)
        await event.edit("🛑 تم إيقاف الموسيقى بنجاح.")
    except:
        await event.edit("⚠️ لا يوجد اتصال نشط حالياً.")

@client.on(events.NewMessage(pattern=r"^\.تشغيل (.+)$"))
async def play_music(event):
    if not event.out: return
    url = event.pattern_match.group(1)
    await event.edit(f"🎵 **جاري تشغيل:** {url}")
    
    try:
        # مثال على تشغيل صوت مع ntgcalls
        await ntg.join_group_call(
            event.chat_id,
            input_mode=InputMode.Shell(f'youtube-dl -f bestaudio -g "{url}"'),
            stream_mode=StreamMode().pulse_stream(
                '-f s16le -ac 2 -ar 48000 -'
            )
        )
        await event.edit(f"▶️ **جاري التشغيل الآن:** {url}")
    except Exception as e:
        await event.edit(f"❌ خطأ في التشغيل: {e}")
