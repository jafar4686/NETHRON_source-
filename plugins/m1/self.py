import __main__
from telethon import events, types
import datetime

client = __main__.client

# مخزن الرسائل في الذاكرة
if not hasattr(__main__, 'msg_cache'):
    __main__.msg_cache = {}

self_status = True 

# 1. أوامر التحكم
@client.on(events.NewMessage(pattern=r"^\.(تفعيل|تعطيل) ذاتيه$"))
async def toggle_self(event):
    global self_status
    self_status = True if "تفعيل" in event.text else False
    await event.edit(f"✅ **تم {'تفعيل' if self_status else 'تعطيل'} حفظ المحذوفات.**")

@client.on(events.NewMessage(pattern=r"^\.فحص ذاتيه$"))
async def check_cache(event):
    cache_count = len(__main__.msg_cache)
    status = "شغال ✅" if self_status else "معطل ❌"
    await event.edit(f"🤖 **نظام الذاتية:** {status}\n📦 **الرسائل المراقبة:** {cache_count}")

# 2. مراقبة وتخزين الرسائل الصادرة والواردة
@client.on(events.NewMessage)
async def cache_messages(event):
    if not self_status or not event.is_private:
        return
    # تخزين الرسالة باستخدام الـ ID
    __main__.msg_cache[event.id] = event.message
    # تنظيف الكاش (أقصى حد 1000 رسالة)
    if len(__main__.msg_cache) > 1000:
        __main__.msg_cache.pop(next(iter(__main__.msg_cache)))

# 3. صيد الحذف باستخدام الـ Raw Update
@client.on(events.Raw(types.UpdateDeleteMessages))
async def handler(event):
    if not self_status:
        return
    
    for msg_id in event.messages:
        if msg_id in __main__.msg_cache:
            original_msg = __main__.msg_cache[msg_id]
            
            # جلب اسم المرسل
            sender = await original_msg.get_sender()
            name = sender.first_name if sender else "مستخدم"
            
            info_text = (
                "⚠️ **كاشف المحذوفات (نيثرون)**\n"
                f"👤 **المرسل:** [{name}](tg://user?id={original_msg.sender_id})\n"
                f"⏰ **وقت الحذف:** {datetime.datetime.now().strftime('%I:%M %p')}\n"
                "👇 **الرسالة المحذوفة:**"
            )
            
            # الإرسال للمحفوظات
            await client.send_message("me", info_text)
            await client.send_message("me", original_msg)
            
            # حذفها من الكاش بعد الصيد
            del __main__.msg_cache[msg_id]