import __main__
from telethon import events, Button
import yt_dlp
import os

client = __main__.client
bot = __main__.bot

HEADER = "★────────☭────────★\n"

@client.on(events.NewMessage(pattern=r"^\.بحث (تيك|يوت|انستا|بنترست) (.*)"))
async def download_media(event):
    platform = event.pattern_match.group(1)
    url = event.pattern_match.group(2)
    await event.edit("🔍 **جاري البحث والتحقق من الرابط...**")
    
    # أزرار الاختيار
    buttons = [
        [Button.inline("🎥 تحميل فيديو", data=f"dl_vid_{platform}"), 
         Button.inline("🎵 تحميل صوت", data=f"dl_aud_{platform}")]
    ]
    
    await event.edit(f"{HEADER}📥 **مستخرج نيثـرون الذكي**\n🌐 المنصة: {platform}\n🔗 الرابط: [اضغط هنا]({url})\n{HEADER}اختر الصيغة المطلوبة:", buttons=buttons, link_preview=False)
    # تخزين الرابط مؤقتاً في ذاكرة البوت (يفضل استخدام قاعدة بيانات أو ملف نصي)
    with open("temp_url.txt", "w") as f: f.write(url)

@bot.on(events.CallbackQuery(pattern=r"dl_(vid|aud)_(.*)"))
async def dl_callback(event):
    data = event.data.decode().split("_")
    mode = data[1] # vid or aud
    with open("temp_url.txt", "r") as f: url = f.read()
    
    await event.edit("⏳ **جاري التحميل والمعالجة...**")
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best' if mode == 'vid' else 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        
    await event.edit("📤 **جاري الرفع إلى تليجرام...**")
    await event.client.send_file(event.chat_id, filename, caption=f"✅ تم التحميل بواسطة نيثـرون\n📌 {info['title']}")
    os.remove(filename)
