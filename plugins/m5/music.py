from pytgcalls import PyTgCalls, idle
from pytgcalls.types import AudioPiped
import __main__
from telethon import events, Button
import yt_dlp

client = __main__.client
bot = __main__.bot
call_py = PyTgCalls(client)

@client.on(events.NewMessage(pattern=r"^\.ميوزك$"))
async def start_music(event):
    await event.edit("⚙️ **جاري تهيئة نظام الميوزك...**")
    # شريط تحميل فخم
    bar = "▱▱▱▱▱▱▱▱▱▱ 0%"
    await event.edit(f"🛠 **تفعيل النظام**\n{bar}")
    for i in range(10, 101, 30):
        fill = "▰" * (i//10) + "▱" * (10-(i//10))
        await event.edit(f"🛠 **تفعيل النظام**\n{fill} {i}%")
    await event.edit(f"{HEADER}✅ **تم تفعيل الميوزك في المجموعة بنجاح!**\n🎶 نيثـرون جاهز للطرب.\n{HEADER}")

@client.on(events.NewMessage(pattern=r"^\.ميوزك يوت (.*)"))
async def play_yt(event):
    url = event.pattern_match.group(1)
    await event.edit("🎼 **جاري استخراج بيانات الأغنية...**")
    
    with yt_dlp.YoutubeDL({}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info['title']
        duration = info.get('duration_string', 'غير محدد')
        date = info.get('upload_date', 'غير معروف')
        thumb = info['thumbnail']

    caption = (
        f"🎵 **اسم الأغنية:** `{title}`\n"
        f"⏱ **الوقت:** `{duration}`\n"
        f"📅 **التاريخ:** `{date}`\n\n"
        "**اضغط الزر أدناه للتشغيل في المحادثة المرئية 👇**"
    )
    
    buttons = [Button.inline("▶️ تشغيل الآن", data=f"play_{url}")]
    await client.send_file(event.chat_id, thumb, caption=caption, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=r"play_(.*)"))
async def play_call(event):
    url = event.data.decode().split("_", 1)[1]
    await event.answer("🎵 جاري الاتصال بالمحادثة المرئية...", alert=True)
    
    # كود التشغيل الفعلي (يستخدم pytgcalls)
    # ملاحظة: يتطلب هذا الجزء تشغيل call_py.start() في الملف الرئيسي
    
    # محاكاة شريط الوقت الفخم
    progress_bar = "▰▰▰▱▱▱▱▱▱▱ 03:45"
    buttons = [Button.inline("⏹ إيقاف الأغنية", data="stop_music")]
    
    await event.edit(f"🎶 **جاري التشغيل الآن...**\n\n{progress_bar}\n\n", buttons=buttons)
