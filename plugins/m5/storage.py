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
        if b is None:
            return "🔋100%" # إذا كان السيرفر لا يقرأ البطارية
        p = int(b.percent)
        # إذا حاطه على الشحن يخلي صاعقة ⚡ وإذا لا يخلي بطارية 🔋
        s = "⚡" if b.power_plugged else "🔋"
        return f"{s}{p}%"
    except Exception as e:
        print(f"Battery Read Error: {e}")
        return "🔋100%"

async def battery_loop(mode):
    while True:
        try:
            txt = get_batt()
            # جلب معلومات الحساب
            full = await client(GetFullUserRequest('me'))
            
            if mode == "بايو":
                # تنظيف البايو من الإضافات القديمة
                current_about = full.full_user.about or "𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁"
                clean_bio = current_about.split(' | ')[0]
                final_text = f"{clean_bio} | {txt}"
                # تحديث البايو
                await client(UpdateProfileRequest(about=final_text[:70]))
            
            elif mode == "اسم":
                name = full.users[0].first_name.split(' | ')[0]
                await client(UpdateProfileRequest(first_name=f"{name} | {txt}"))
            
            await asyncio.sleep(60) # تحديث كل دقيقة
        except asyncio.CancelledError:
            # تنظيف عند الإيقاف
            break
        except Exception as e:
            print(f"Loop Error: {e}")
            await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"^\.شحن (اسم|بايو)$"))
async def start_batt(event):
    # التأكد من أن الرسالة من المطور
    if not event.out:
        return

    mode = event.pattern_match.group(1)
    
    # إيقاف أي مهمة شحن سابقة
    if battery_task["run"]:
        battery_task["run"].cancel()
        await asyncio.sleep(0.5)

    # محاولة تحديث أولية فورية للتأكد من العمل
    await event.edit(f"⚙️ **جاري تفعيل عرض الشحن في {mode}...**")
    
    battery_task["run"] = asyncio.create_task(battery_loop(mode))
    battery_task["mode"] = mode
    
    await asyncio.sleep(2)
    await event.edit(f"✅ **تم تفعيل الشحن في {mode} بنجاح!**\n🔋 الحالة الحالية: {get_batt()}")

@client.on(events.NewMessage(pattern=r"^\.ايقاف الشحن$"))
async def stop_batt(event):
    if not event.out: return
    if battery_task["run"]:
        battery_task["run"].cancel()
        battery_task["run"] = None
        await event.edit("✅ تم إيقاف عرض الشحن.")
    else:
        await event.edit("⚠️ لا توجد ميزة شحن تعمل حالياً.")
