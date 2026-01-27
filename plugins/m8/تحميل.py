import __main__, asyncio, json, os
from telethon import events

client = getattr(__main__, 'client', None)

def get_delay():
    if not os.path.exists("anim_settings.json"): return 3.0
    try:
        with open("anim_settings.json", "r") as f: return json.load(f).get("delay", 3.0)
    except: return 3.0

@client.on(events.NewMessage(outgoing=True))
async def loading_anim(event):
    if "$تحميل" in event.text:
        text = event.text
        vortex = ["◜", "◝", "◞", "◟"]
        try:
            while True:
                for f in vortex:
                    await event.edit(text.replace("$تحميل", f))
                    await asyncio.sleep(get_delay())
        except: pass
