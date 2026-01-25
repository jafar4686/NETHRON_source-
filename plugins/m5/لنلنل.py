import __main__
import asyncio
from telethon import events

client = __main__.client

# 1. قلب ينبض (يكبر ويصغر)
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نبض"))
async def heart_pump(event):
    frames = [
        "❤️", "❤️‍🔥", "💓", "💗", "💖", "💝", "💥", "❤️"
    ]
    for _ in range(3): # تكرار النبض 3 مرات
        for f in frames:
            await event.edit(f"**ـہہـ٨ـہہـ٨ـ {f} نـيـثـرون {f} ـہہـ٨ـہہـ٨ـ**")
            await asyncio.sleep(0.3)

# 2. الصاروخ الصاعد (رسم نقاط)
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.صاروخ"))
async def rocket_art(event):
    frames = [
        "      🚀\n      .\n      .",
        "      🚀\n      .\n     *.",
        "      🚀\n     *.*\n    *.*.*",
        "     *.*\n    *.*.*\n   *.*.*.*",
        "    *.*.*\n   *.*.*.*\n  *.*.*.*.*",
        "✨ **تـم الانـطـلاق بـنـجـاح** ✨"
    ]
    for f in frames:
        await event.edit(f"`{f}`")
        await asyncio.sleep(0.4)

# 3. رسم الساعة الرملية المتحركة
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.وقت"))
async def time_art(event):
    frames = ["⏳", "⌛"]
    for i in range(10):
        await event.edit(f"✨ **جاري الانتظار {frames[i%2]}** ✨")
        await asyncio.sleep(0.4)

# 4. الرادار الكاشف (نقاط دائرية)
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.رادار"))
async def radar_art(event):
    frames = [
        "📡 `[ . . . . ]`",
        "📡 `[ ● . . . ]`",
        "📡 `[ . ● . . ]`",
        "📡 `[ . . ● . ]`",
        "📡 `[ . . . ● ]`",
        "📡 `[ . . . . ]` ✅"
    ]
    for f in frames:
        await event.edit(f"🛡️ **نظام نيثرون للكشف:**\n{f}")
        await asyncio.sleep(0.3)

# 5. أنيميشن الوردة المتفتحة (نقاط وفواصل)
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.وردة"))
async def flower_art(event):
    frames = [
        "     ☘️",
        "   ☘️ 🌷",
        " ☘️ 🌷 ☘️",
        "🌷 ☘️ 🌷 ☘️",
        "✨ **أحلى وردة لمستخدم نيثرون** ✨"
    ]
    for f in frames:
        await event.edit(f)
        await asyncio.sleep(0.5)
