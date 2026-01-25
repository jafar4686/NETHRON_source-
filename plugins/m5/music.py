import __main__
import asyncio
from telethon import events

client = __main__.client

# قائمة ببوتات تحميل قوية (تقدر تغيرها)
# بوت يوتيوب: @utubebot أو @YtbDownBot
# بوت تيك توك: @TikTokDownloaderBot
YT_BOT = "@C_5BOT"
TIK_BOT = "@VAFBoT"

@client.on(events.NewMessage(outgoing=True))
async def forward_to_external(event):
    text = event.text
    
    # إذا كان رابط يوتيوب
    if "youtube.com" in text or "youtu.be" in text:
        await event.edit("🔄 **جاري التحويل لبوت يوتيوب العالمي...**")
        await client.send_message(YT_BOT, text)
        await asyncio.sleep(2) # انتظار بسيط للتأكد من الإرسال
        await event.delete()

    # إذا كان رابط تيك توك
    elif "tiktok.com" in text:
        await event.edit("🔄 **جاري التحويل لبوت تيك توك العالمي...**")
        await client.send_message(TIK_BOT, text)
        await asyncio.sleep(2)
        await event.delete()
