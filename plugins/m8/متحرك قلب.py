import __main__, asyncio
from telethon import events
from plugins.settings_manager import get_anim_delay

client = getattr(__main__, 'client', None)

@client.on(events.NewMessage(outgoing=True))
async def loading_anim(event):
    if "$تحميل" in event.text:
        text = event.text
        vortex = ["◜", "◝", "◞", "◟"]
        try:
            while True:
                for f in vortex:
                    await event.edit(text.replace("$تحميل", f))
                    await asyncio.sleep(get_anim_delay())
        except: pass
