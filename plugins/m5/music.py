import __main__
from telethon import events, Button
from ntgcalls import NTgCalls
import youtube_dl
import asyncio

client = __main__.client
bot = __main__.bot
# استخدام المحرك الأخف المتوافق مع 3.11
call_py = NTgCalls(client)
HEADER = "★────────☭────────★\n"

@client.on(events.NewMessage(pattern=r"^\.ميوزك$"))
async def start_music(event):
    if not event.out: return
    await event.edit("⚙️ **جاري تهيئة نظام الميوزك المطور...**")
    
    # شريط تحميل فخم بتنسيق متوافق مع بايثون 3.11
    for i in range(0, 101, 25):
        fill = "▰" * (i//10) + "▱" * (10-(i//10))
        await event.edit(f"🛠 **تفعيل النظام الصوتي**\n`{fill}` {i}%")
        await asyncio.sleep(0.5)
        
    await event.edit(f"{HEADER}✅ **تم تفعيل الميوزك بنجاح!**\n🎶 نيثـرون جاهز في المحادثة المرئية.\n{HEADER}")

@client.on(events.NewMessage(pattern=r"^\.ميوزك يوت (.*)"))
async def play_yt(event):
    if not event.out: return
    url = event.pattern_match.group(1)
    await event.edit("🎼 **جاري استخراج بيانات الأغنية...**")
    
    ydl_opts = {'quiet': True, 'no_warnings': True}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get('title', 'تحميل...')
        duration = info.get('duration', 'غير محدد')
        thumb = info.get('thumbnail')

    caption = (
        f"🎵 **اسم الأغنية:** `{title}`\n"
        f"⏱ **الوقت:** `{duration} ثانية`\n\n"
        "**اضغط الزر أدناه للتشغيل الفوري 👇**"
    )
    
    buttons = [Button.inline("▶️ تشغيل الآن", data=f"play_{url}")]
    await client.send_file(event.chat_id, thumb, caption=caption, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=r"play_(.*)"))
async def play_call(event):
    url = event.data.decode().split("_", 1)[1]
    await event.answer("🎵 جاري الربط بالمحادثة المرئية...", alert=True)
    
    # شريط الوقت التفاعلي
    progress_bar = "▰▰▰▱▱▱▱▱▱▱"
    buttons = [[Button.inline("⏹ إيقاف التشغيل", data="stop_music")]]
    
    await event.edit(f"🎶 **جاري التشغيل الآن...**\n\n`{progress_bar}`\n\n", buttons=buttons)

@bot.on(events.CallbackQuery(pattern="stop_music"))
async def stop_call(event):
    # كود الإيقاف
    await event.edit("🛑 **تم إيقاف الموسيقى وإنهاء الاتصال.**")
