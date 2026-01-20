import __main__
from telethon import events, Button
from ntgcalls import NTgCalls
import asyncio

client = __main__.client
# الميوزك يحتاج البوت المساعد للرد في المجموعات
bot = getattr(__main__, 'bot', None) 
call_py = NTgCalls(client)

@client.on(events.NewMessage(pattern=r"^\.ميوزك$"))
async def start_in_group(event):
    # السماح للأمر بالعمل فقط إذا كنت أنت من أرسله (event.out)
    if not event.out: return
    
    await event.edit("🔄 **جاري الربط بالمحادثة المرئية للمجموعة...**")
    try:
        # التأكد من تشغيل المحرك
        if not call_py.active:
            await call_py.start()
        
        await event.edit("✅ **تم تفعيل نظام الميوزك في هذه المجموعة!**\n🎶 نيثـرون جاهز الآن.")
    except Exception as e:
        await event.edit(f"❌ **لازم تفتح المحادثة المرئية أولاً!**\nالخطأ: `{e}`")

@client.on(events.NewMessage(pattern=r"^\.م٥$"))
async def m5_group(event):
    if not event.out: return
    await event.edit("🍎 **قائمة ميوزك المجموعات**\n\n• `.ميوزك يوت` + رابط\n• `.ايقاف` لقطع الصوت\n\n**تأكد من وجود البوت المساعد مشرفاً!**")
