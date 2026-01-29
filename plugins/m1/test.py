import __main__, asyncio, datetime, platform, time
from telethon import events

client = getattr(__main__, 'client', None)

# وقت بداية تشغيل السورس
start_time = time.time()

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    # الوحدات بالرموز الإنجليزية المختصرة
    time_suffix_list = ["𝒔", "𝒎", "𝒉", "𝒅"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + " " + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ":"
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.فحص$"))
async def check_device(event):
    # 1. حساب البنك (Ping) فوراً
    start = datetime.datetime.now()
    end = datetime.datetime.now()
    ping = f"{(end - start).microseconds / 1000:.2f}ms"
    
    # 2. جلب معلومات الحساب
    me = await client.get_me()
    name = f"[{me.first_name}](tg://user?id={me.id})"
    user = f"@{me.username}" if me.username else "لا يوجد"
    pyver = platform.python_version()
    uptime = get_readable_time(int(time.time() - start_time))
    
    # الكليشة الفخمة اللي ردتها
    msg = (
        "★────────☭────────★\n"
        "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
        "★────────☭────────★\n\n"
        f"•  𝑷𝒚𝑻𝒉𝒐𝒏 ➝ ⊙ `{pyver}`\n"
        f"• 𝑵𝒂𝒎𝒆 ➝ ⊙ {name}\n"
        f"• 𝑼𝒔𝒆𝒓 ➝ ⊙ {user}\n"
        f"• 𝑼𝒑𝑻𝒊𝒎𝒆 ➝ ⊙ `{uptime}`\n"
        f"• 𝑷𝒊𝒏𝒈 ➝ ⊙ `{ping}`\n"
        "───────────────\n"
        "𝑫𝑬𝑽 ↠ [𝑫𝑬𝑽](https://t.me/NETH_RON)\n"
        "𝑨𝑫𝑴𝑰𝑵 ↠ [𝑨𝑫](https://t.me/xxnnxg)"
    )
    
    # 3. التعديل الفوري (أسرع شي)
    await event.edit(msg)
