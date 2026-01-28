import __main__, asyncio, json, os, pytz
from datetime import datetime
from telethon import events, functions, types
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest

client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]

# المسار المباشر كما في الصورة مالتك
TIME_DIR = "/home/container/Time_Data"
time_tasks = {"name": None, "bio": None}

# التأكد من وجود المجلد
if not os.path.exists(TIME_DIR):
    try: os.makedirs(TIME_DIR)
    except: pass

async def get_acc_file():
    me = await client.get_me()
    return os.path.join(TIME_DIR, f"{me.id}.json")

async def save_cfg(mode, status):
    path = await get_acc_file()
    data = {"name": False, "bio": False}
    if os.path.exists(path):
        try:
            with open(path, "r") as f: data = json.load(f)
        except: pass
    data[mode] = status
    with open(path, "w") as f: json.dump(data, f)

async def load_cfg():
    try:
        path = await get_acc_file()
        if os.path.exists(path):
            with open(path, "r") as f: return json.load(f)
    except: pass
    return {"name": False, "bio": False}

def get_iraq_time():
    return datetime.now(pytz.timezone('Asia/Baghdad')).strftime("%I:%M")

async def time_worker(mode):
    while True:
        try:
            cfg = await load_cfg()
            if not cfg.get(mode): break
            
            now = get_iraq_time()
            full = await client(GetFullUserRequest('me'))
            
            if mode == "name":
                name = full.users[0].first_name.split(' | ')[0]
                await client(UpdateProfileRequest(first_name=f"{name} | {now}"))
            elif mode == "bio":
                bio = (full.full_user.about or "𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁").split(' | ')[0]
                final_bio = f"{bio} | {now}"
                if len(final_bio) > 70: final_bio = f"{bio[:55]} | {now}"
                await client(UpdateProfileRequest(about=final_bio))
            
            await asyncio.sleep(60)
        except: await asyncio.sleep(60)

async def startup_engine():
    # ننتظر شوي لحد ما الحساب يسوي اتصال كامل
    await asyncio.sleep(15)
    try:
        cfg = await load_cfg()
        if cfg.get("name"):
            time_tasks["name"] = asyncio.create_task(time_worker("name"))
        if cfg.get("bio"):
            time_tasks["bio"] = asyncio.create_task(time_worker("bio"))
    except: pass

# تشغيل المحرك التلقائي
client.loop.create_task(startup_engine())

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.وقتي (اسم|بايو)$"))
async def start_t(event):
    choice = event.pattern_match.group(1)
    mode = "name" if choice == "اسم" else "bio"
    cfg = await load_cfg()
    
    if cfg.get(mode):
        msg = await event.edit(f"◈〔 اكو وقت موجود حبيبي شغال بـ {choice} 〕◈")
        await asyncio.sleep(5)
        return await msg.delete()
    
    for i in range(10): 
        f = VORTEX[i % 4]
        await event.edit(f"{f} 〔صبرك جاي يتفعل〕 {f}")
        await asyncio.sleep(0.4)
    
    await save_cfg(mode, True)
    time_tasks[mode] = asyncio.create_task(time_worker(mode))
    
    msg = await event.edit(
        "◆━━━━━━━━━━━━━━━━━◆\n"
        "✅ اشتغل الوقت ضلعي روح شوف\n"
        f"⦿ النوع: {choice}\n"
        "⦿ التوقيت: العراق 🇮🇶\n"
        "◆━━━━━━━━━━━━━━━━━◆"
    )
    await asyncio.sleep(5)
    await msg.delete()

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف وقتي$"))
async def stop_t(event):
    cfg = await load_cfg()
    if not any(cfg.values()):
        msg = await event.edit("◈〔 ماكو وقت شغال حتى اوقفة 〕◈")
        await asyncio.sleep(5)
        return await msg.delete()

    for i in range(10): 
        f = VORTEX[i % 4]
        await event.edit(f"{f} 〔صبرك جاي يتوقف〕 {f}")
        await asyncio.sleep(0.4)

    await save_cfg("name", False)
    await save_cfg("bio", False)
    
    for k in time_tasks:
        if time_tasks[k]: time_tasks[k].cancel(); time_tasks[k] = None
    
    # تنظيف فوري للاسم
    try:
        full = await client(GetFullUserRequest('me'))
        clean_name = full.users[0].first_name.split(' | ')[0]
        await client(UpdateProfileRequest(first_name=clean_name))
    except: pass
    
    msg = await event.edit(
        "◆━━━━━━━━━━━━━━━━━◆\n"
        "✅ اتوقف الوقت حبيبي روح شوف\n"
        "⦿ تم تنظيف الحساب بنجاح\n"
        "◆━━━━━━━━━━━━━━━━━◆"
    )
    await asyncio.sleep(5)
    await msg.delete()
