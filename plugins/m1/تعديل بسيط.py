import __main__
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
import asyncio
from datetime import datetime
import pytz # مكتبة المناطق الزمنية

client = __main__.client
time_tasks = {"name": None, "bio": None}

# دالة لجلب وقت العراق حصراً
def get_iraq_time():
    iraq_tz = pytz.timezone('Asia/Baghdad')
    return datetime.now(iraq_tz).strftime("%I:%M")

async def update_time_loop(mode):
    while True:
        try:
            # استخدام توقيت العراق بدلاً من توقيت السيرفر
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
            # الكود الخاص بالإلغاء يبقى كما هو
            full = await client(GetFullUserRequest('me'))
            if mode == "name":
                clean_name = full.users[0].first_name.split(' | ')[0]
                await client(UpdateProfileRequest(first_name=clean_name))
            elif mode == "bio":
                if full.full_user.about:
                    clean_bio = full.full_user.about.split(' | ')[0]
                    await client(UpdateProfileRequest(about=clean_bio))
            break
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(60)

@client.on(events.NewMessage(pattern=r"^\.وقتي (اسم|بايو)$"))
async def start_time(event):
    choice = event.pattern_match.group(1)
    mode = "name" if choice == "اسم" else "bio"
    if time_tasks[mode]:
        return await event.edit(f"⚠️ الوقت في {choice} شغال بالفعل!")
    
    await event.edit(f"✅ تم تفعيل الوقت في {choice}\nسيتحدث بتوقيت العراق 🇮🇶")
    time_tasks[mode] = asyncio.create_task(update_time_loop(mode))

@client.on(events.NewMessage(pattern=r"^\.ايقاف وقتي$"))
async def stop_time(event):
    for k in time_tasks:
        if time_tasks[k]:
            time_tasks[k].cancel()
            time_tasks[k] = None
    await event.edit("✅ تم إيقاف الوقت وتنظيف الحساب بنجاح.")
