import __main__
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
import asyncio
from datetime import datetime
import pytz

client = __main__.client
current_task = {"run": None}

def get_year_progress():
    # حساب نسبة السنة الحالية
    now = datetime.now(pytz.timezone('Asia/Baghdad'))
    year = now.year
    start = datetime(year, 1, 1, tzinfo=pytz.timezone('Asia/Baghdad'))
    end = datetime(year + 1, 1, 1, tzinfo=pytz.timezone('Asia/Baghdad'))
    progress = (now - start) / (end - start)
    percent = int(progress * 100)
    
    # صنع شريط تحميل (Loading Bar)
    filled = int(percent / 10)
    bar = "▰" * filled + "▱" * (10 - filled)
    return f"{bar} {percent}%"

def get_iraq_time():
    return datetime.now(pytz.timezone('Asia/Baghdad')).strftime("%I:%M")

async def status_loop(mode, it_type):
    while True:
        try:
            # اختيار النص: إما وقت أو نسبة السنة
            txt = get_iraq_time() if it_type == "time" else get_year_progress()
            full = await client(GetFullUserRequest('me'))
            
            if mode == "اسم":
                clean = full.users[0].first_name.split(' | ')[0]
                await client(UpdateProfileRequest(first_name=f"{clean} | {txt}"))
            elif mode == "بايو":
                bio = (full.full_user.about or "𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁").split(' | ')[0]
                await client(UpdateProfileRequest(about=f"{bio} | {txt}"[:70]))
            
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            break
        except:
            await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"^\.(وقتي|نسبة) (اسم|بايو)$"))
async def start_st(event):
    if not event.out: return
    
    it_type = "time" if "وقتي" in event.text else "progress"
    it_mode = "اسم" if "اسم" in event.text else "بايو"
    
    if current_task["run"]:
        current_task["run"].cancel()
        await asyncio.sleep(0.5)

    await event.edit(f"✅ **تم التفعيل بنجاح!**\n⚙️ الميزة: {'الوقت' if it_type == 'time' else 'نسبة السنة'}\n📍 المكان: {it_mode}")
    current_task["run"] = asyncio.create_task(status_loop(it_mode, it_type))

@client.on(events.NewMessage(pattern=r"^\.اطفاء الخدمة$"))
async def stop_st(event):
    if not event.out: return
    if current_task["run"]:
        current_task["run"].cancel()
        current_task["run"] = None
        await event.edit("✅ تم إيقاف الخدمات وتنظيف الحساب.")
    else:
        await event.edit("⚠️ لا توجد خدمة تعمل.")
