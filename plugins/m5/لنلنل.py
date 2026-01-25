import __main__
import asyncio
from telethon import events

client = __main__.client

# 1. أنيميشن "الوجه الحزين" (يتحرك من الهدوء للبكاء)
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حزين"))
async def sad_anim(event):
    frames = [
        " ( •_• ) ",
        " ( •_•)>💧",
        " ( •_•)💧💧",
        " ( ╥﹏╥ ) ",
        "💔 **نـيـثـرون يـتـألـم** 💔"
    ]
    for f in frames:
        await event.edit(f"`{f}`")
        await asyncio.sleep(0.6)

# 2. أنيميشن "القطة الكرتونية" (تمشي في الشات)
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.بزونة"))
async def cat_anim(event):
    frames = [
        "      ✨\n   拟\n ( •ω•)  🐾",
        "    ✨\n   拟\n (•ω• )  🐾",
        "  ✨\n 拟\n( •ω•)   🐾",
        "✨ **نـورت الـبـزونـة** ✨"
    ]
    for f in frames:
        await event.edit(f"`{f}`")
        await asyncio.sleep(0.5)

# 3. أنيميشن "رسمة أنمي" (البنت الخجولة)
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.انمي"))
async def anime_anim(event):
    frames = [
        "  (  -_-)",
        "  (  -_-)>✨",
        "  (づ￣ ³￣)づ",
        "  (◕‿◕✿)",
        "🌸 **نـيـثـرون لـلأنـمـي** 🌸"
    ]
    for f in frames:
        await event.edit(f"`{f}`")
        await asyncio.sleep(0.6)

# 4. أنيميشن "الرجل الراقص" (حركة كاملة)
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.رقص"))
async def dance_anim(event):
    frames = [
        "   ヘ(^_^ヘ)",
        "   (ノ^_^)ノ",
        "   ＼(^o^ )／",
        "   (^_^♪)",
        "🔥 **الـهـيـبـة تـرقـص** 🔥"
    ]
    for _ in range(2): # تكرار الرقصة مرتين
        for f in frames:
            await event.edit(f"`{f}`")
            await asyncio.sleep(0.4)

# 5. أنيميشن "الانفجار الضخم" (رسمة انفجار بالنقاط)
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.بوم"))
async def bomb_anim(event):
    frames = [
        "      💣",
        "    💥  💣",
        "  💥  💥  💥",
        " 💥  NETHRON  💥",
        "  💥  💥  💥",
        "      ✨"
    ]
    for f in frames:
        await event.edit(f"`{f}`")
        await asyncio.sleep(0.4)
