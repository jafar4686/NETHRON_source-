import __main__
from telethon import events

client = __main__.client
# حط يوزر بوت الميكر مالتك هنا (بدون @)
ASSISTANT_USER = "taltbatbot" 

@client.on(events.NewMessage(outgoing=True))
async def forward_to_bot(event):
    if "youtube.com" in event.text or "youtu.be" in event.text or "tiktok.com" in event.text:
        # إرسال الرابط للمساعد
        await client.send_message(ASSISTANT_USER, event.text)
        # حذف رسالتك الأصلية
        await event.delete()
