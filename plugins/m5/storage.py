import __main__
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
import asyncio
import psutil

client = __main__.client

# مخزن لمهمة الشحن
battery_task = {"run": None, "mode": None}

def get_batt():
    try:
        b = psutil.sensors_battery()
        p = b.percent
        # إذا حاطه على الشحن يخلي صاعقة ⚡ وإذا لا يخلي بطارية 🔋
        s = "⚡" if b.power_plugged else "🔋"
        return f"{s}{p}%"
    except:
        return "🔋100%"

async def battery_loop(mode):
    while True:
        try:
            # جلب النسبة الحالية
            txt = get_batt()
            full = await client(GetFullUserRequest('me'))
            
            if mode == "اسم":
                name = full.users[0].first_name.split(' | ')[0]
                await client(UpdateProfileRequest(first_name=f"{name} | {txt}"))
            
            elif mode == "بايو":
                bio = (full.full_user.about or "𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁").split(' | ')[0]
                await client(UpdateProfileRequest(about=f"{bio} | {txt}"[:70]))
            
            await asyncio.sleep(60) # يحدث كل دقيقة
        except asyncio.CancelledError:
            # عند الإيقاف نرجع الحساب نظيف
            full = await client(GetFullUserRequest('me'))
            if mode == "اسم":
                name = full.users[0].first_name.split(' | ')[0]
                await client(UpdateProfileRequest(first_name=name))
            else:
                bio = (full.full_user.about or "").split(' | ')[0]
                await client(UpdateProfileRequest(about=bio))
            break
        except:
            await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"^\.شحن (اسم|بايو)$"))
async def start_batt(event):
    mode = event.pattern_match.group(1)
    
    # فحص إذا كان هناك وقت شغال بملف التايم مانجر (اختياري)
    # لكن هنا سنركز على إيقاف مهام الشحن السابقة في هذا الملف
    if battery_task["run"]:
        battery_task["run"].cancel()
        await asyncio.sleep(1)

    await event.edit(f"✅ **تم تفعيل عرض الشحن في {mode}**\n⚡ سيتم تحديث الحالة تلقائياً.")
    battery_task["run"] = asyncio.create_task(battery_loop(mode))
    battery_task["mode"] = mode

@client.on(events.NewMessage(pattern=r"^\.ايقاف الشحن$"))
async def stop_batt(event):
    if battery_task["run"]:
        battery_task["run"].cancel()
        battery_task["run"] = None
        await event.edit("✅ تم إيقاف عرض الشحن وتنظيف الحساب.")
    else:
        await event.edit("⚠️ لا توجد ميزة شحن تعمل حالياً.")
