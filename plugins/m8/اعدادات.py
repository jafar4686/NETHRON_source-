import json, os
from telethon import events
import __main__

client = getattr(__main__, 'client', None)
SETTINGS_FILE = "anim_settings.json"

def get_anim_delay():
    if not os.path.exists(SETTINGS_FILE):
        return 3.0
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f).get("delay", 3.0)
    except: return 3.0

@client.on(events.NewMessage(pattern=r"^\.وقت الحركة (\d+)$"))
async def set_delay(event):
    if not event.out: return
    try:
        new_delay = int(event.pattern_match.group(1))
        if new_delay < 2 or new_delay > 5:
            return await event.edit("⚠️ **اقل وقت 2 واكثر وقت 5 ثواني للأمان!**")
        
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"delay": float(new_delay)}, f)
        await event.edit(f"✅ **تم ضبط سرعة الحركة على: {new_delay} ثانية**")
    except: pass
