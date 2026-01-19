import __main__
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
import asyncio
from datetime import datetime
import pytz
import psutil # تأكد انك كتبت pip install psutil بالكونسل

client = __main__.client
# مخزن المهمة الحالية
current_task = {"run": None}

def get_info(info_type):
    if info_type == "time":
        return datetime.now(pytz.timezone('Asia/Baghdad')).strftime("%I:%M")
    else:
        try:
            b = psutil.sensors_battery()
            p = int(b.percent) if b else 100
            s = "⚡" if b and b.power_plugged else "🔋"
            return f"{s}{p}%"
        except:
            return "🔋100%"

async def status_loop(mode, type):
    while True:
        try:
            txt = get_info(type)
            full = await client(GetFullUserRequest('me'))
            
            if mode == "name":
                clean = full.users[0].first_name.split(' | ')[0]
                await client(UpdateProfileRequest(first_name=f"{clean} | {txt}"))
            elif mode == "bio":
                bio = (full.full_user.about or "𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁").split(' | ')[0]
                await client(UpdateProfileRequest(about=f"{bio} | {txt}"[:70]))
            
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            break
        except:
            await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"^\.(وقتي|شحن) (اسم|بايو)$"))
async def start_st(event):
    if not event.out: return
    
    # استخراج النوع والمكان من الأمر
    it_type = "time" if "وقتي" in event.text else "battery"
    it_mode = "name" if "اسم" in event.text else "bio"
    
    # إلغاء أي شي قديم شغال
    if current_task["run"]:
        current_task["run"].cancel()
        await asyncio.sleep(1)

    await event.edit(f"✅ **تم التفعيل بنجاح!**\n⚙️ النوع: {it_type}\n📍 المكان: {it_mode}")
    current_task["run"] = asyncio.create_task(status_loop(it_mode, it_type))

@client.on(events.NewMessage(pattern=r"^\.اطفاء$"))
async def stop_st(event):
    if not event.out: return
    if current_task["run"]:
        current_task["run"].cancel()
        current_task["run"] = None
        await event.edit("✅ تم إطفاء جميع الخدمات وتنظيف الحساب.")
    else:
        await event.edit("⚠️ لا توجد خدمة تعمل.")
