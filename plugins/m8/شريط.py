import __main__, asyncio
from telethon import events
from plugins.settings_manager import get_anim_delay

client = getattr(__main__, 'client', None)

@client.on(events.NewMessage(outgoing=True))
async def bar_anim(event):
    if "$بار" in event.text:
        text = event.text
        bar_frames = ["[▒░░░░░]", "[▒▒░░░░]", "[▒▒▒░░░]", "[▒▒▒▒░░]", "[▒▒▒▒▒░]", "[▒▒▒▒▒▒]"]
        try:
            while True:
                for b in bar_frames:
                    await event.edit(text.replace("$بار", b))
                    await asyncio.sleep(get_anim_delay())
        except: pass
