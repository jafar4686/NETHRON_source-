import __main__
from telethon import events, types, functions
import datetime
import asyncio

client = __main__.client

# --- إعدادات سورس نيثرون الفخمة ---
if not hasattr(__main__, 'nethron_self'):
    __main__.nethron_self = {
        "storage_id": None,
        "private_active": False,
        "groups_active": False,
        "auto_clean": False,
        "msg_cache": {} 
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
        f"{FOOTER}"
    )
    await event.edit(text)

# --- [2] إنشاء قناة التخزين ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل ذاتيه$"))
async def setup_storage(event):
    await event.edit("🌀 **جاري إنشاء قناة التخزين...**\n`[▒▒▒▒▒▒▒▒▒▒] 0%` ")
    try:
        result = await client(functions.channels.CreateChannelRequest(
            title=f"تخزين نيثرون {datetime.datetime.now().year}",
            about="تخزين المحذوفات - سورس نيثرون",
            megagroup=False
        ))
        CONFIG["storage_id"] = result.chats[0].id
        await event.edit(f"✅ **تم إنشاء قناة التخزين!**\nآيدي القناة: `{CONFIG['storage_id']}`")
    except Exception as e:
        await event.edit(f"❌ فشل: {str(e)}")
    await asyncio.sleep(10)
    await event.delete()

# --- [3] التفعيل مع شريط تحميل ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل (خاص|مجموعات)$"))
async def toggle_on(event):
    mode = event.pattern_match.group(1)
    key = "private_active" if mode == "خاص" else "groups_active"
    frames = ["🌑", "▒ 50%", "██ 100%"]
    for f in frames:
        await event.edit(f"🌀 **تفعيل صيد {mode}...**\n`{f}`")
        await asyncio.sleep(0.3)
    CONFIG[key] = True
    await event.edit(f"✅ **تم تفعيل صيد {mode} بنجاح!**")
    await asyncio.sleep(10)
    await event.delete()

# --- [4] كاشف المحذوفات (المُصحح الجذري) ---
@client.on(events.NewMessage)
async def cache_all(event):
    # ميزة هيبة: خزن اسم المرسل فوراً لضمان وجوده عند الحذف
    sender = await event.get_sender()
    name = getattr(sender, 'first_name', "مستخدم")
    if not name: name = "مجهول"
    
    CONFIG["msg_cache"][event.id] = {
        "text": event.text,
        "media": event.media,
        "sender_name": name,
        "sender_id": event.sender_id,
        "type": "خاص" if event.is_private else "مجموعة"
    }
    # تنظيف الكاش (أقصى حد 1500 رسالة)
    if len(CONFIG["msg_cache"]) > 1500:
        CONFIG["msg_cache"].pop(next(iter(CONFIG["msg_cache"])))

@client.on(events.Raw(types.UpdateDeleteMessages))
async def on_delete(event):
    if not CONFIG["storage_id"]: return
    
    for msg_id in event.messages:
        if msg_id in CONFIG["msg_cache"]:
            data = CONFIG["msg_cache"][msg_id]
            
            # فحص هل النوع (خاص أو مجموعة) مفعل؟
            if (data["type"] == "خاص" and not CONFIG["private_active"]) or \
               (data["type"] == "مجموعة" and not CONFIG["groups_active"]):
                continue

            log_text = (
                f"{HEADER}"
                "⚠️ **تم صيد رسالة محذوفة**\n"
                f"👤 **المرسل:** [{data['sender_name']}](tg://user?id={data['sender_id']})\n"
                f"🏷 **النوع:** {data['type']}\n"
                f"⏰ **الوقت:** {datetime.datetime.now().strftime('%H:%M:%S')}\n"
                f"{HEADER}\n"
                f"💬 **الرسالة:**\n\n{data['text'] or '«وسائط/ملف»'}"
            )
            
            await client.send_message(CONFIG["storage_id"], log_text, file=data["media"])
            # مسحها من الكاش بعد الصيد لتوفير المساحة
            del CONFIG["msg_cache"][msg_id]

# --- [5] التنظيف التلقائي ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنظيف (تفعيل|تعطيل)$"))
async def auto_clean_toggle(event):
    cmd = event.pattern_match.group(1)
    CONFIG["auto_clean"] = True if cmd == "تفعيل" else False
    await event.edit(f"🗑 **نظام التنظيف:** {'مفعل ✅' if CONFIG['auto_clean'] else 'معطل ❌'}")
    if CONFIG["auto_clean"]: asyncio.create_task(cleaner_loop())

async def cleaner_loop():
    while CONFIG["auto_clean"]:
        await asyncio.sleep(60)
        if CONFIG["storage_id"]:
            try:
                async for msg in client.iter_messages(CONFIG["storage_id"]):
                    if (datetime.datetime.now(msg.date.tzinfo) - msg.date).seconds > 60:
                        await msg.delete()
            except: pass
