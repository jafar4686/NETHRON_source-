import __main__, asyncio, json, os, pytz
from datetime import datetime
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest

client = getattr(__main__, 'client', None)
TIME_DIR = "Time_Data"
time_tasks = {"name": None, "bio": None}
VORTEX = ["◜", "◝", "◞", "◟"]

# إنشاء المجلد إذا لم يكن موجوداً
if not os.path.exists(TIME_DIR):
    os.makedirs(TIME_DIR)

# دالة جلب مسار ملف الإعدادات لكل حساب
async def get_time_db():
    me = await client.get_me()
    return os.path.join(TIME_DIR, f"time_{me.id}.json")

# دالة الحفظ والقراءة
async def load_settings():
    path = await get_time_db()
    if not os.path.exists(path): return {"name": False, "bio": False}
    with open(path, "r") as f: return json.load(f)

async def save_settings(data):
    path = await get_time_db()
    with open(path, "w") as f: json.dump(data, f)

def get_iraq_time():
    iraq_tz = pytz.timezone('Asia/Baghdad')
    return datetime.now(iraq_tz).strftime("%I:%M")

async def update_time_loop(mode):
    while True:
        try:
            # التحقق إذا كان الوضع لا يزال مفعلاً في الخزن
            settings = await load_settings()
            if not settings.get(mode): break

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
            # تنظيف الحساب عند الإيقاف
            full = await client(GetFullUserRequest('me'))
            if mode == "name":
                clean_name = full.users[0].first_name.split(' | ')[0]
                await client(UpdateProfileRequest(first_name=clean_name))
            elif mode == "bio":
                if full.full_user.about:
                    clean_bio = full.full_user.about.split(' | ')[0]
                    await client(UpdateProfileRequest(about=clean_bio))
            break
        except:
            await asyncio.sleep(60)

# --- نظام التشغيل التلقائي عند بدء السورس ---
async def auto_start_time():
    try:
        await asyncio.sleep(15) # انتظار استقرار الاتصال
        settings = await load_settings()
        for mode in ["name", "bio"]:
            if settings.get(mode):
                time_tasks[mode] = asyncio.create_task(update_time_loop(mode))
    except: pass

# تشغيل الفحص التلقائي
loop = asyncio.get_event_loop()
loop.create_task(auto_start_time())

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.وقتي (اسم|بايو)$"))
async def start_time(event):
    choice = event.pattern_match.group(1)
    mode = "name" if choice == "اسم" else "bio"
    
    settings = await load_settings()
    if settings.get(mode):
        msg = await event.edit(f"◈〔 اكو وقت موجود حبيبي شغال بـ {choice} 〕◈")
        await asyncio.sleep(10)
        return await msg.delete()
    
    # --- أنيميشن التفعيل القديم مالتك ---
    for i in range(10): 
        f = VORTEX[i % 4]
        await event.edit(f"{f} 〔صبرك جاي يتفعل〕 {f}")
        await asyncio.sleep(0.4)
    
    # حفظ الإعداد وتشغيل المهمة
    settings[mode] = True
    await save_settings(settings)
    time_tasks[mode] = asyncio.create_task(update_time_loop(mode))
    
    # --- رسالة التأكيد القديمة مالتك ---
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

    # --- أنيميشن الإيقاف القديم مالتك ---
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
    
    # --- رسالة الإيقاف القديمة مالتك ---
    msg = await event.edit(
        "◆━━━━━━━━━━━━━━━━━◆\n"
        "✅ اتوقف الوقت حبيبي روح شوف\n"
        "⦿ تم تنظيف الحساب بنجاح\n"
        "◆━━━━━━━━━━━━━━━━━◆"
    )
    
    await asyncio.sleep(10)
    await msg.delete()
