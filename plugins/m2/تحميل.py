import __main__
import os
from telethon import events
from yt_dlp import YoutubeDL

client = __main__.client


# تحميل صوت
@client.on(events.NewMessage(pattern=r"\.تحميل صوتي (.+)"))
async def audio_dl(event):
    url = event.pattern_match.group(1)

    msg = await event.reply("⏳ جاري التحميل...")

    opts = {
        "format": "bestaudio",
        "outtmpl": "audio.mp3",
        "quiet": True,
    }

    with YoutubeDL(opts) as ydl:
        ydl.download([url])

    await event.client.send_file(event.chat_id, "audio.mp3")
    os.remove("audio.mp3")
    await msg.delete()



# تحميل فيديو
@client.on(events.NewMessage(pattern=r"\.تحميل فيديو (.+)"))
async def video_dl(event):
    url = event.pattern_match.group(1)

    msg = await event.reply("⏳ جاري التحميل...")

    opts = {
        "format": "best",
        "outtmpl": "video.mp4",
        "quiet": True,
    }

    with YoutubeDL(opts) as ydl:
        ydl.download([url])

    await event.client.send_file(event.chat_id, "video.mp4")
    os.remove("video.mp4")
    await msg.delete()

