import __main__, asyncio, json, os, pytz
from datetime import datetime
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest

client = getattr(__main__, 'client', None)
TIME_DIR = "Time_Data"
time_tasks = {"name": None, "bio": None}
VORTEX = ["◜", "◝", "◞", "◟"]

# إنشاء المجلد في بداية التشغيل
if not os.path.exists(TIME_DIR):
    os.makedirs(TIME_DIR)

# دالة جلب مسار ملف الإعدادات لكل حساب
async def get_time_db():
    me = await client.get_me()
    return os.path.join(TIME_DIR, f"time_{me.id}.json")

# دالة الحفظ والقراءة
async def load_settings():
    path = await get_time_db()
    if not os.path.exists(path): 
        return {"name": False, "bio": False}
    try:
        with open(path, "r", encoding='utf-8') as f: 
            return json.load(f)
    except:
        return {"name": False, "bio": False}

async def save_settings(data):
    path = await get_time_db()
    with open(path, "w", encoding='utf-8') as f: 
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_iraq_time():
    iraq_tz = pytz.timezone('Asia/Baghdad')
    return datetime.now(iraq_tz).strftime("%I:%M")

async def update_time_loop(mode):
    while True:
        try:
            # التحقق من حالة التشغيل من الملف
            settings = await load_settings()
            if not settings.get(mode): 
                break

            current_time = get_iraq_time()
            full = await client(GetFullUserRequest('me'))
            me = full.users[0]
            bio_text = full.full_user.about or "𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁"

            if mode == "name":
                clean_name = me.first_name.split(' | ')[0]
                await client(UpdateProfileRequest(first_name=f"{clean_name} | {current_time}"))
            
            elif mode == "bio":
                clean_bio = bio_text.split(' | ')[0]
                final_bio = f"{clean_bio} | {current_time}"
                if len(final_bio) > 70:
                    final_bio = f"{clean_bio[:55]} | {current_time}"
                await client(UpdateProfileRequest(about=final_bio))
            
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error in time loop: {e}")
            await asyncio.sleep(60)

# --- نظام التشغيل التلقائي عند بدء السورس ---
async def auto_start_time():
    await asyncio.sleep(15) # انتظار استقرار البوت
    try:
        settings = await load_settings()
        if settings.get("name"):
            time_tasks["name"] = asyncio.create_task(update_time_loop("name"))
        if settings.get("bio"):
            time_tasks["bio"] = asyncio.create_task(update_time_loop("bio"))
    except:
        pass

# تفعيل التشغيل التلقائي
asyncio.create_task(auto_start_time())

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.وقتي (اسم|بايو)$"))
async def start_time(event):
    choice = event.pattern_match.group(1)
    mode = "name" if choice == "اسم" else "bio"
    
    settings = await load_settings()
    if settings.get(mode):
        msg = await event.edit(f"◈〔 اكو وقت موجود حبيبي شغال بـ {choice} 〕◈")
        await asyncio.sleep(10)
        return await msg.delete()
    
    # --- أنيميشن التفعيل القديم ---
    for i in range(10): 
        f = VORTEX[i % 4]
        await event.edit(f"{f} 〔صبرك جاي يتفعل〕 {f}")
        await asyncio.sleep(0.4)
    
    # حفظ الإعداد في الملف وتشغيل المهمة
    settings[mode] = True
    await save_settings(settings)
    time_tasks[mode] = asyncio.create_task(update_time_loop(mode))
    
    # --- رسالة التأكيد القديمة ---
    msg = await event.edit(
        "◆━━━━━━━━━━━━━━━━━◆\n"
        "✅ اشتغل الوقت ضلعي روح شوف\n"
        f"⦿ النوع: {choice}\n"
        "⦿ التوقيت: العراق 🇮🇶\n"
        "◆━━━━━━━━━━━━━━━━━◆"
    )
    
    await asyncio.sleep(10)
    await msg.delete()

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف وقتي$"))
async def stop_time(event):
    settings = await load_settings()
    if not any(settings.values()):
        msg = await event.edit("◈〔 ماكو وقت شغال حتى اوقفة 〕◈")
        await asyncio.sleep(10)
        return await msg.delete()

    # --- أنيميشن الإيقاف القديم ---
    for i in range(10): 
        f = VORTEX[i % 4]
        await event.edit(f"{f} 〔صبرك جاي يتوقف〕 {f}")
        await asyncio.sleep(0.4)

    # تعطيل في الخزن وإيقاف المهام
    for k in ["name", "bio"]:
        settings[k] = False
        if time_tasks[k]:
            time_tasks[k].cancel()
            time_tasks[k] = None
    
    await save_settings(settings)
    
    # تنظيف الحساب من الوقت فوراً
    try:
        full = await client(GetFullUserRequest('me'))
        clean_name = full.users[0].first_name.split(' | ')[0]
        await client(UpdateProfileRequest(first_name=clean_name))
        if full.full_user.about:
            clean_bio = full.full_user.about.split(' | ')[0]
            await client(UpdateProfileRequest(about=clean_bio))
    except:
        pass
    
    # --- رسالة الإيقاف القديمة ---
    msg = await event.edit(
        "◆━━━━━━━━━━━━━━━━━◆\n"
        "✅ اتوقف الوقت حبيبي روح شوف\n"
        "⦿ تم تنظيف الحساب بنجاح\n"
        "◆━━━━━━━━━━━━━━━━━◆"
    )
    
    await asyncio.sleep(10)
    await msg.delete()
