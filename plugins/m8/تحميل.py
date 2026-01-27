import __main__
from telethon import events
import asyncio

client = getattr(__main__, 'client', None)

@client.on(events.NewMessage(outgoing=True))
async def loading_anim(event):
    if "$تحميل" in event.text:
        text = event.text
        vortex = ["◜", "◝", "◞", "◟"]
        try:
            while True:
                for f in vortex:
                    animated_text = text.replace("$تحميل", f)
                    await event.edit(animated_text)
                    await asyncio.sleep(0.3) # سرعة الدوران
        except: pass
