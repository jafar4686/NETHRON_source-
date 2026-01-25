import __main__
import asyncio
from telethon import events

client = __main__.client

# 1. أنيميشن القمر العملاق (تحول كامل للأطوار)
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.قمر"))
async def moon_anim(event):
    frames = [
        "🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘", "🌑"
    ]
    for _ in range(2):
        for frame in frames:
            await event.edit(f"**ـہہـ٨ـہہـ٨ـ {frame} NETHRON {frame} ـہہـ٨ـہہـ٨ـ**")
            await asyncio.sleep(0.2)

# 2. أنيميشن "مصفوفة الهكر" (Matrix Falling) - رسم نقاط عمودي
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.هكر"))
async def matrix_anim(event):
    frames = [
        "░\n░\n░", "▓\n░\n░", "▓\n▓\n░", "▓\n▓\n▓",
        "💎\n▓\n▓", "░\n💎\n▓", "░\n░\n💎", "✅"
    ]
    for frame in frames:
        await event.edit(f"**جاري اختراق النظام...**\n`{frame}`")
        await asyncio.sleep(0.3)

# 3. أنيميشن "نبض القلب الاحترافي" (ECG Line) - رسم خطي
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نبضي"))
async def heart_line(event):
    frames = [
        "ـہہـ٨ـہہـ٨ـ",
        "ـہہـ٨ـہہـ٨ـ❤️",
        "ـہہـ٨ـہہـ٨ـ❤️ـہہـ٨ـ",
        "❤️ـہہـ٨ـہہـ٨ـ❤️",
        "⚡ NETHRON ⚡"
    ]
    for frame in frames:
        await event.edit(f"**`{frame}`**")
        await asyncio.sleep(0.4)

# 4. أنيميشن "الدوامة" (The Swirl) - حركية دائرية
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.دوامة"))
async def swirl_anim(event):
    frames = ["◜", "◝", "◞", "◟"]
    for _ in range(5):
        for frame in frames:
            await event.edit(f"**{frame} جاري المعالجة {frame}**")
            await asyncio.sleep(0.2)
    await event.edit("✅ **اكتمـل العمل**")

# 5. أنيميشن "البرق المدمر" (Lightning Art)
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.صاعقة"))
async def thunder_anim(event):
    frames = [
        "☁️", 
        "☁️\n  ⚡", 
        "☁️\n  ⚡\n   💥", 
        "✨ NETHRON ✨"
    ]
    for frame in frames:
        await event.edit(f"**{frame}**")
        await asyncio.sleep(0.4)
