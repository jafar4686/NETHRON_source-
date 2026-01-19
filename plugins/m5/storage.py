import __main__
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
import asyncio
import psutil

client = __main__.client

# مخزن للمهمة الحالية (اسم أو بايو)
battery_tasks = {"name": None, "bio": None}

def get_battery_text():
    try:
        battery = psutil.sensors_battery()
        percent = battery.percent
        # يضيف علامة الصاعقة إذا كان الموبايل على الشحن
        status = "⚡" if battery.power_plugged else "🔋"
        return f"{status}{percent}%"
    except:
        return "🔋100%"

async def update_battery_loop(mode):
    while True:
        try:
            battery_text = get_battery_text()
            full = await client(GetFullUserRequest('me'))
            me = full.users[0]
            bio_text = full.full_user.about or "𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁"

            if mode == "name":
                # تنظيف الاسم من أي إضافات قديمة
                clean_name = me.first_name.split(' | ')[0]
                await client(UpdateProfileRequest(first_name=f"{clean_name} | {battery_text}"))
            
            elif mode == "bio":
                # تنظيف البايو وتحديثه مع نسبة الشحن
                clean_bio = bio_text.split(' | ')[0]
                final_bio = f"{clean_bio} | {battery_text}"
                await client(UpdateProfileRequest(about=final_bio[:70]))
            
            await asyncio.sleep(60) # تحديث كل دقيقة
        except asyncio.CancelledError:
            # عند الإيقاف يرجع الحساب كما كان
            full = await client(GetFullUserRequest('me'))
            if mode == "name":
                clean_name = full.users[0].first_name.split(' | ')[0]
                await client(UpdateProfileRequest(first_name=clean_name))
            else:
                clean_bio = (full.full_user.about or "").split(' | ')[0]
                await client(UpdateProfileRequest(about=clean_bio))
            break
        except Exception as e:
            print(f"Battery Error: {e}")
            await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"^\.شحن (اسم|بايو)$"))
async def start_battery(event):
    choice = event.pattern_match.group(1)
    mode = "name" if choice == "اسم" else "bio"
    
    if battery_tasks[mode]:
        return await event.edit(f"⚠️ ميزة الشحن في {choice} مفعلة بالفعل!")
    
    await event.edit(f"✅ تم تفعيل عرض الشحن في {choice}\nسيتحدث خلال دقيقة...")
    battery_tasks[mode] = asyncio.create_task(update_battery_loop(mode))

@client.on(events.NewMessage(pattern=r"^\.ايقاف الشحن$"))
async def stop_battery(event):
    stopped = False
    for k in battery_tasks:
        if battery_tasks[k]:
            battery_tasks[k].cancel()
            battery_tasks[k] = None
            stopped = True
    
    if stopped:
        await event.edit("✅ تم إيقاف عرض الشحن وتنظيف الحساب.")
    else:
        await event.edit("⚠️ لا توجد ميزة شحن تعمل حالياً.")
