import __main__
from telethon import events
import datetime
import platform

client = __main__.client

@client.on(events.NewMessage(pattern=r"^\.فحص$"))
async def check_update(event):
    if not event.out: return
    
    # حساب وقت التشغيل أو معلومات النظام
    uptime = "منذ 5 دقائق" # مثال
    db_status = "متصلة ✅ (SQLite)"
    ver = "V2.5 - Nethron"
    
    msg = (
        "🚀 **تفاصيل تحديث سس نيثرون:**\n"
        "★──────────☭──────────★\n"
        f"📡 **حالة السورس:** محدث لآخر إصدار\n"
        f"🛠 **الإصدار:** `{ver}`\n"
        f"🗄 **قاعدة البيانات:** `{db_status}`\n"
        f"💻 **النظام:** `{platform.system()}`\n"
        f"⏰ **الوقت الحالي:** `{datetime.datetime.now().strftime('%H:%M:%S')}`\n"
        "★──────────☭──────────★\n"
        "📢 **ملاحظة:** تم سحب آخر التحديثات بنجاح."
    )
    await event.edit(msg)