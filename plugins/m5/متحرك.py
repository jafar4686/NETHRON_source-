import __main__
import asyncio
from telethon import events

client = __main__.client

# 1. ميزة الكلام المتحرك (بناء الجملة حرف حرف)
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.متحرك (.*)"))
async def animated_text(event):
    text = event.pattern_match.group(1)
    display_text = ""
    for char in text:
        display_text += char
        await event.edit(f"✨ {display_text} ⚡")
        await asyncio.sleep(0.2)
    await event.edit(f"🔥 **{text}** 🔥")

# 2. ميزة الرسم بالنقاط (إيموجي يتحول لشكل)
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.رسم"))
async def point_art(event):
    frames = [
        "🌑", "🌘", "🌗", "🌖", "🌕", "🌔", "🌓", "🌒", "🌑",
        "🌀 جاري رسم الهيبة...",
        "░░░░░░░░░░ 0%",
        "▓▓▓░░░░░░░ 30%",
        "▓▓▓▓▓▓░░░░ 60%",
        "▓▓▓▓▓▓▓▓▓▓ 100%",
        "✨ **NETHRON SOURCE** ✨"
    ]
    for frame in frames:
        await event.edit(frame)
        await asyncio.sleep(0.4)

# 3. ميزة القلب المتحرك (خرافي للمقالب أو الإهداءات)
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.قلب"))
async def heart_anim(event):
    hearts = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎"]
    for i in range(10):
        for h in hearts:
            await event.edit(f"{h} **نـيـثـرون** {h}")
            await asyncio.sleep(0.2)

# 4. ميزة التحميل الوهمي (تخوف بيها صاحبك)
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اختراق"))
async def hack_anim(event):
    stages = [
        "🔍 جاري فحص الحماية...",
        "🔓 تم كشف الثغرة: 192.168.1.1",
        "📥 جاري سحب الصور...",
        "[███▒▒▒▒▒▒▒] 30%",
        "[███████▒▒▒] 70%",
        "[██████████] 100%",
        "✅ تم الاختراق بنجاح! هههههههه"
    ]
    for stage in stages:
        await event.edit(f"🛡️ **HACKER MODE**\n`{stage}`")
        await asyncio.sleep(0.7)
