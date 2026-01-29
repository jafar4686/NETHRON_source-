import __main__, asyncio, datetime, platform, time
from telethon import events

client = getattr(__main__, 'client', None)

# حساب وقت بداية تشغيل السورس (للأب تايم)
start_time = time.time()

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["ثانية", "دقيقة", "ساعة", "يوم"]
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
        ping_time += time_list.pop() + ", "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.فحص$"))
async def check_device(event):
    # 1. حساب البنك (Ping)
    start = datetime.datetime.now()
    await event.edit("⟳")
    end = datetime.datetime.now()
    ping = f"{(end - start).microseconds / 1000:.2f}ms"
    
    # 2. حساب الأب تايم (Uptime)
    uptime = get_readable_time(int(time.time() - start_time))
    
    # 3. إصدار البايثون
    pyver = platform.python_version()
    
    # 4. المنشن (Name with Link)
    me = await client.get_me()
    mention = f"[{me.first_name}](tg://user?id={me.id})"
    
    # الكليشة مالتك المرتبة
    msg = (
        "╓══════✧══❖══✧════╖\n"
        f"┃ ⟢ ᴠᴇʀ : `{pyver}`\n"
        f"┃ ⟢ ᴜᴘᴛɪᴍᴇ : `{uptime}`\n"
        f"┃ ⟢ ɴᴀᴍᴇ : {mention}\n"
        f"┃ ⟢ ᴘɪɴɢ : `{ping}`\n"
        "╙══════✧══❖══✧════╜"
    )
    
    # التعديل النهائي
    await event.edit(msg)
