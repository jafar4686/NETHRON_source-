import __main__, asyncio
from telethon import events
from plugins.settings_manager import get_anim_delay

client = getattr(__main__, 'client', None)

@client.on(events.NewMessage(outgoing=True))
async def real_pulse_anim(event):
    if "$نبض" in event.text:
        text = event.text
        wave_frames = ["ﮩﮩـ", "ﮩﮩـﮩ", "ﮩﮩـ٨ﮩـ", "ﮩﮩـ٨ﮩﮩـ"]
        try:
            while True:
                for w in wave_frames:
                    await event.edit(text.replace("$نبض", w))
                    await asyncio.sleep(get_anim_delay())
        except: pass
