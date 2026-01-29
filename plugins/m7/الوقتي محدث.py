import __main__, asyncio, pytz, os
from datetime import datetime
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest

client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]
time_tasks = {"name": None, "bio": None}

# مسار الصورة داخل مجلد assets
IMG_PATH = "assets/TIME.jpg"

def get_iraq_time():
    return datetime.now(pytz.timezone('Asia/Baghdad')).strftime("%I:%M")

async def time_worker(mode):
    while True:
        try:
            current_time = get_iraq_time()
            full = await client(GetFullUserRequest('me'))
            
            if mode == "name":
                if " | " not in (full.users[0].first_name or ""): 
                    time_tasks["name"] = None
                    break
                clean_name = full.users[0].first_name.split(' | ')[0]
                await client(UpdateProfileRequest(first_name=f"{clean_name} | {current_time}"))
            
            elif mode == "bio":
                bio_text = full.full_user.about or ""
                if " | " not in bio_text: 
                    time_tasks["bio"] = None
                    break
                clean_bio = bio_text.split(' | ')[0]
                final_bio = f"{clean_bio} | {current_time}"
                if len(final_bio) > 70: 
                    final_bio = f"{clean_bio[:55]} | {current_time}"
                await client(UpdateProfileRequest(about=final_bio))
            
            await asyncio.sleep(60)
        except: 
            await asyncio.sleep(60)

async def startup_engine():
    await asyncio.sleep(15) 
    try:
        full = await client(GetFullUserRequest('me'))
        if " | " in (full.users[0].first_name or ""):
            if not time_tasks["name"]:
                time_tasks["name"] = asyncio.create_task(time_worker("name"))
        if " | " in (full.full_user.about or ""):
            if not time_tasks["bio"]:
                time_tasks["bio"] = asyncio.create_task(time_worker("bio"))
    except: 
        pass

client.loop.create_task(startup_engine())

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.وقتي (اسم|بايو)$"))
async def start_time(event):
    choice = event.pattern_match.group(1)
    mode = "name" if choice == "اسم" else "bio"
    
    if time_tasks[mode]:
        msg = await event.edit(f"◈〔 اكو وقت موجود حبيبي شغال بـ {choice} 〕◈")
        await asyncio.sleep(10)
        return await msg.delete()
    
    # --- أنيميشن التفعيل القديم ---
    for i in range(10): 
        f = VORTEX[i % 4]
        await event.edit(f"{f} 〔صبرك جاي يتفعل〕 {f}")
        await asyncio.sleep(0.4)
    
    full = await client(GetFullUserRequest('me'))
    now = get_iraq_time()
    
    if mode == "name":
        clean_name = (full.users[0].first_name or "").split(' | ')[0]
        await client(UpdateProfileRequest(first_name=f"{clean_name} | {now}"))
    else:
        clean_bio = (full.full_user.about or "𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁").split(' | ')[0]
        await client(UpdateProfileRequest(about=f"{clean_bio} | {now}"))

    time_tasks[mode] = asyncio.create_task(time_worker(mode))
    
    # حذف رسالة الأمر وإرسال الصورة مع الكليشة
    await event.delete()
    caption = (
        "◆━━━━━━━━━━━━━━━━━◆\n"
        "✅ اشتغل الوقت ضلعي روح شوف\n"
        f"⦿ النوع: {choice}\n"
        "⦿ التوقيت: العراق 🇮🇶\n"
        "◆━━━━━━━━━━━━━━━━━◆"
    )
    
    if os.path.exists(IMG_PATH):
        await client.send_file(event.chat_id, IMG_PATH, caption=caption)
    else:
        await event.respond(caption) # إذا الصورة مو موجودة يرسل بس نص

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف وقتي$"))
async def stop_time(event):
    is_running = any(time_tasks.values())
    if not is_running:
        msg = await event.edit("◈〔 ماكو وقت شغال حتى اوقفة 〕◈")
        await asyncio.sleep(10)
        return await msg.delete()

    # --- أنيميشن الإيقاف القديم ---
    for i in range(10): 
        f = VORTEX[i % 4]
        await event.edit(f"{f} 〔صبرك جاي يتوقف〕 {f}")
        await asyncio.sleep(0.4)

    for k in time_tasks:
        if time_tasks[k]:
            time_tasks[k].cancel()
            time_tasks[k] = None
    
    try:
        full = await client(GetFullUserRequest('me'))
        if " | " in (full.users[0].first_name or ""):
            clean_name = full.users[0].first_name.split(' | ')[0]
            await client(UpdateProfileRequest(first_name=clean_name))
        
        if full.full_user.about and " | " in full.full_user.about:
            clean_bio = full.full_user.about.split(' | ')[0]
            await client(UpdateProfileRequest(about=clean_bio))
    except: 
        pass
    
    # حذف رسالة الأمر وإرسال صورة الإيقاف
    await event.delete()
    caption = (
        "◆━━━━━━━━━━━━━━━━━◆\n"
        "✅ اتوقف الوقت حبيبي روح شوف\n"
        "⦿ تم تنظيف الحساب بنجاح\n"
        "◆━━━━━━━━━━━━━━━━━◆"
    )
    
    if os.path.exists(IMG_PATH):
        await client.send_file(event.chat_id, IMG_PATH, caption=caption)
    else:
        await event.respond(caption)
