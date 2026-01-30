import json, os
from telethon import events
import __main__

client = getattr(__main__, 'client', None)

@client.on(events.NewMessage(pattern=r"^\.وقت الحركة (\d+)$"))
async def set_delay(event):
    if not event.out: return
    try:
        new_delay = int(event.pattern_match.group(1))
        if new_delay < 2 or new_delay > 5:
            return await event.edit("⚠️ اقل وقت 2 واكثر وقت 5 ثواني!")
        
        with open("anim_settings.json", "w") as f:
            json.dump({"delay": float(new_delay)}, f)
        await event.edit(f"✅ تم ضبط السرعة على: {new_delay} ثانية")
    except Exception as e:
        await event.edit(f"خطأ: {str(e)}")
