import __main__
from telethon import events, types, functions
import datetime
import asyncio

client = __main__.client

# إعدادات النظام في الذاكرة
if not hasattr(__main__, 'self_config'):
    __main__.self_config = {
        'status': False,
        'private': False,
        'groups': False,
        'storage_id': None,
        'auto_clean': False,
        'clean_interval': 60, # ثانية (1 دقيقة)
        'cache': {}
    }

# --- دالة إنشاء قناة التخزين ---
async def get_storage(event):
    if __main__.self_config['storage_id']:
        return __main__.self_config['storage_id']
    
    # البحث عن قناة موجودة
    async for dialog in client.iter_dialogs():
        if dialog.is_channel and dialog.title == "مخزن الذاتية 📦":
            __main__.self_config['storage_id'] = dialog.id
            return dialog.id
            
    # إذا لم توجد، يتم إنشاؤها
    await event.edit("⚙️ **جاري إنشاء قناة التخزين...**")
    result = await client(functions.channels.CreateChannelRequest(
        title="مخزن الذاتية 📦",
        about="هذه القناة مخصصة لحفظ الرسائل المحذوفة تلقائياً.",
        megagroup=False
    ))
    __main__.self_config['storage_id'] = result.chats[0].id
    await event.respond("✅ **تم إنشاء قناة التخزين بنجاح!**")
    return result.chats[0].id

# --- أوامر التفعيل والتحكم ---

@client.on(events.NewMessage(pattern=r"^\.تفعيل ذاتيه$"))
async def start_self(event):
    __main__.self_config['status'] = True
    await get_storage(event)
    await event.edit("🚀 **تم تفعيل نظام الذاتية الشامل.**\nيتم الآن مراقبة المحذوفات وتحويلها للمخزن.")

@client.on(events.NewMessage(pattern=r"^\.تفعيل خاص$"))
async def toggle_pv(event):
    __main__.self_config['private'] = True
    # شريط تحميل فخم
    bar = ["⬜", "⬛", "⬛", "⬛", "⬛"]
    for i in range(len(bar)):
        bar[i] = "🟦"
        await event.edit(f"**جاري تفعيل الخاص..**\n\n{''.join(bar)} {i*25}%")
        await asyncio.sleep(0.3)
    await event.edit("✅ **تم تفعيل الذاتية للخاص بنجاح!**")

@client.on(events.NewMessage(pattern=r"^\.تفعيل مجموعات$"))
async def toggle_groups(event):
    __main__.self_config['groups'] = True
    await event.edit("✅ **تم تفعيل الذاتية للمجموعات.**")

@client.on(events.NewMessage(pattern=r"^\.ايقاف ذاتيه$"))
async def stop_all(event):
    __main__.self_config['status'] = False
    __main__.self_config['private'] = False
    __main__.self_config['groups'] = False
    await event.edit("❌ **تم إيقاف نظام الذاتية بالكامل.**")

# --- مراقبة الحذف والأرشفة ---

@client.on(events.NewMessage)
async def cache_all(event):
    conf = __main__.self_config
    if not conf['status']: return
    
    # حفظ الرسائل بناءً على النوع المفعل
    if (event.is_private and conf['private']) or (event.is_group and conf['groups']):
        conf['cache'][event.id] = event.message

@client.on(events.Raw(types.UpdateDeleteMessages))
async def on_delete(event):
    conf = __main__.self_config
    if not conf['status']: return

    for msg_id in event.messages:
        if msg_id in conf['cache']:
            msg = conf['cache'][msg_id]
            sender = await msg.get_sender()
            name = sender.first_name if sender else "مجهول"
            chat_type = "خاص 👤" if msg.is_private else "مجموعة 👥"
            
            info = (
                f"🗑 **رسالة محذوفة جديدة**\n"
                f"👤 **المرسل:** [{name}](tg://user?id={msg.sender_id})\n"
                f"📍 **النوع:** {chat_type}\n"
                f"⏰ **وقت الحذف:** {datetime.datetime.now().strftime('%I:%M %p')}\n"
                f"💬 **المحتوى:** 👇"
            )
            
            storage = await get_storage(None)
            await client.send_message(storage, info)
            await client.send_message(storage, msg)
            del conf['cache'][msg_id]

# --- نظام التنظيف التلقائي ---

@client.on(events.NewMessage(pattern=r"^\.تفعيل حذف رسائل$"))
async def auto_clean(event):
    __main__.self_config['auto_clean'] = True
    await event.edit("🧹 **تم تفعيل التنظيف التلقائي لمخزن الذاتية.**\nسيتم حذف الرسائل كل دقيقة.")
    
    while __main__.self_config['auto_clean']:
        await asyncio.sleep(__main__.self_config['clean_interval'])
        storage = await get_storage(None)
        await client(functions.channels.DeleteHistoryRequest(channel=storage, max_id=0))

# --- كليشة الأوامر م6 ---

@client.on(events.NewMessage(pattern=r"^\.م6$"))
async def help_menu(event):
    menu = (
        "🛠 **قائمة أوامر الذاتية والحذف**\n"
        "--- --- --- --- --- --- ---\n"
        "🔹 `.تفعيل ذاتيه` : إنشاء المخزن وتفعيل النظام\n"
        "🔹 `.تفعيل خاص` : مراقبة حذف رسائل الخاص\n"
        "🔹 `.تفعيل مجموعات` : مراقبة حذف رسائل الكروبات\n"
        "🔹 `.ايقاف ذاتيه` : إيقاف النظام بالكامل\n"
        "🔹 `.تفعيل حذف رسائل` : تنظيف المخزن تلقائياً\n"
        "🔹 `.فحص ذاتيه` : لمعرفة حالة النظام والذاكرة\n"
        "--- --- --- --- --- --- ---\n"
        "⚙️ **المطور:** نظام نيثرون الذكي"
    )
    await event.edit(menu)
