import __main__
from telethon import events, types, functions
import datetime
import asyncio

client = __main__.client

# --- إعدادات الحالة الفخمة ---
if not hasattr(__main__, 'nethron_self'):
    __main__.nethron_self = {
        "storage_id": None,
        "private_active": False,
        "groups_active": False,
        "auto_clean": False,
        "clean_interval": 60,
        "msg_cache": {} # الذاكرة المؤقتة للرسائل
    }

CONFIG = __main__.nethron_self
HEADER = "★────────☭────────★\n"
FOOTER = "\n★────────☭────────★"

# --- [1] قائمة الأوامر م6 ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م6$"))
async def nethron_m6(event):
    text = (
        f"{HEADER}"
        "   ☭ • **𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁** • ☭\n"
        "      • قسم الذاتية والحذف •\n"
        f"{HEADER}\n"
        "• `.تفعيل ذاتيه` : لإنشاء قناة التخزين\n"
        "• `.تفعيل خاص` : صيد محذوفات الخاص\n"
        "• `.تفعيل مجموعات` : صيد محذوفات الكروبات\n"
        "• `.ايقاف خاص` | `.ايقاف مجموعات`\n"
        "• `.تنظيف تفعيل` : حذف تلقائي للقناة (1د)\n"
        "• `.تنظيف تعطيل` : إيقاف الحذف التلقائي\n"
        f"{FOOTER}"
    )
    await event.edit(text)

# --- [2] إنشاء قناة التخزين (تلقائي) ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل ذاتيه$"))
async def setup_storage(event):
    await event.edit("🌀 **جاري إنشاء قناة التخزين...**\n`[▒▒▒▒▒▒▒▒▒▒] 0%` ")
    await asyncio.sleep(1)
    try:
        result = await client(functions.channels.CreateChannelRequest(
            title=f"تخزين نيثرون - {datetime.datetime.now().strftime('%Y')}",
            about="هذه القناة مخصصة لحفظ الرسائل المحذوفة (سورس نيثرون)",
            megagroup=False
        ))
        CONFIG["storage_id"] = result.chats[0].id
        await event.edit("✅ **تم إنشاء قناة التخزين بنجاح!**\n`[██████████] 100%` \n"
                         f"آيدي القناة: `{CONFIG['storage_id']}`")
    except Exception as e:
        await event.edit(f"❌ **فشل إنشاء القناة:** {str(e)}")
    
    await asyncio.sleep(10)
    await event.delete()

# --- [3] أوامر التفعيل والتعطيل مع شريط التحميل ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل (خاص|مجموعات)$"))
async def toggle_on(event):
    mode = event.pattern_match.group(1)
    key = "private_active" if mode == "خاص" else "groups_active"
    
    frames = ["🌑", "░ 20%", "▒ 50%", "▓ 80%", "██ 100%"]
    for f in frames:
        await event.edit(f"🌀 **جاري تفعيل صيد {mode}...**\n`{f}`")
        await asyncio.sleep(0.3)
    
    CONFIG[key] = True
    await event.edit(f"✅ **تم تفعيل صيد محذوفات {mode} بنجاح!**")
    await asyncio.sleep(10)
    await event.delete()

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف (خاص|مجموعات)$"))
async def toggle_off(event):
    mode = event.pattern_match.group(1)
    key = "private_active" if mode == "خاص" else "groups_active"
    CONFIG[key] = False
    await event.edit(f"📴 **تم إيقاف صيد {mode}.**")
    await asyncio.sleep(10)
    await event.delete()

# --- [4] كاشف المحذوفات (المُصحح) ---
@client.on(events.NewMessage)
async def cache_all(event):
    # التصحيح: خزن رسائل الخاص والمجموعات معاً
    CONFIG["msg_cache"][event.id] = {
        "msg": event.message,
        "type": "خاص" if event.is_private else "مجموعة"
    }
    # تنظيف الكاش (أقصى حد 2000 رسالة لعدم تعليق السيرفر)
    if len(CONFIG["msg_cache"]) > 2000:
        CONFIG["msg_cache"].pop(next(iter(CONFIG["msg_cache"])))

@client.on(events.Raw(types.UpdateDeleteMessages))
async def on_delete(event):
    if not CONFIG["storage_id"]: return
    
    for msg_id in event.messages:
        if msg_id in CONFIG["msg_cache"]:
            data = CONFIG["msg_cache"][msg_id]
            msg = data["msg"]
            m_type = data["type"]
            
            # التحقق من نوع التفعيل
            if (m_type == "خاص" and not CONFIG["private_active"]) or \
               (m_type == "مجموعة" and not CONFIG["groups_active"]):
                continue

            try:
                sender = await msg.get_sender()
                name = getattr(sender, 'first_name', "مجهول")
                user_id = getattr(sender, 'id', "غير معروف")
                
                log_text = (
                    f"{HEADER}"
                    "⚠️ **تم صيد رسالة محذوفة**\n"
                    f"👤 **المرسل:** [{name}](tg://user?id={user_id})\n"
                    f"🏷 **النوع:** {m_type}\n"
                    f"⏰ **وقت الحذف:** {datetime.datetime.now().strftime('%H:%M:%S')}\n"
                    f"{HEADER}\n"
                    f"💬 **الرسالة:**\n\n{msg.text or '«وسائط/ملف»'}"
                )
                
                await client.send_message(CONFIG["storage_id"], log_text, file=msg.media)
            except: pass

# --- [5] نظام التنظيف التلقائي ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنظيف (تفعيل|تعطيل)$"))
async def auto_clean_toggle(event):
    cmd = event.pattern_match.group(1)
    CONFIG["auto_clean"] = True if cmd == "تفعيل" else False
    await event.edit(f"🗑 **نظام تنظيف القناة أصبح:** {'مفعل ✅' if CONFIG['auto_clean'] else 'معطل ❌'}")
    
    if CONFIG["auto_clean"]:
        asyncio.create_task(cleaner_loop())

async def cleaner_loop():
    while CONFIG["auto_clean"]:
        await asyncio.sleep(60) # فحص كل دقيقة
        if CONFIG["storage_id"]:
            try:
                async for msg in client.iter_messages(CONFIG["storage_id"]):
                    now = datetime.datetime.now(msg.date.tzinfo)
                    if (now - msg.date).total_seconds() > 60:
                        await msg.delete()
            except: pass
