import __main__
from telethon import events
import asyncio

client = getattr(__main__, 'client', None)

@client.on(events.NewMessage(outgoing=True))
async def hearts_anim(event):
    if "$قلب" in event.text:
        text = event.text
        hearts = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎"]
        try:
            while True:
                for h in hearts:
                    animated_text = text.replace("$قلب", h)
                    await event.edit(animated_text)
                    await asyncio.sleep(0.5)
        except: pass
