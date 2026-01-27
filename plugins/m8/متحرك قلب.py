import __main__, asyncio
from telethon import events
from plugins.settings_manager import get_anim_delay

client = getattr(__main__, 'client', None)

@client.on(events.NewMessage(outgoing=True))
async def hearts_anim(event):
    if "$قلب" in event.text:
        text = event.text
        hearts = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎"]
        try:
            while True:
                for h in hearts:
                    await event.edit(text.replace("$قلب", h))
                    await asyncio.sleep(get_anim_delay())
        except: pass
