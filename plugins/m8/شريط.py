import __main__, asyncio, json, os
from telethon import events

client = getattr(__main__, 'client', None)

def get_delay():
    if not os.path.exists("anim_settings.json"): return 3.0
    try:
        with open("anim_settings.json", "r") as f: return json.load(f).get("delay", 3.0)
    except: return 3.0

@client.on(events.NewMessage(outgoing=True))
async def bar_anim(event):
    if "$بار" in event.text:
        text = event.text
        bar_frames = ["[▒░░░░░]", "[▒▒░░░░]", "[▒▒▒░░░]", "[▒▒▒▒░░]", "[▒▒▒▒▒░]", "[▒▒▒▒▒▒]"]
        try:
            while True:
                for b in bar_frames:
                    await event.edit(text.replace("$بار", b))
                    await asyncio.sleep(get_delay())
        except: pass
