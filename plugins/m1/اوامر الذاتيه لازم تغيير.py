import __main__
from telethon import events, types, functions
import datetime
import asyncio

client = __main__.client

# --- إعدادات سورس نيثرون الذكية ---
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

# --- [1] أمر م6 المطور ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م6$"))
async def nethron_m6(event):
    text = (
        f"{HEADER}"
        "   ☭ • **𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁** • ☭\n"
        "      • قسم الذاتية والحذف •\n"
        f"{HEADER}\n"
        "• `.تفعيل ذاتيه` : إنشاء/ربط القناة\n"
        "• `.تفعيل خاص` : صيد محذوفات الخاص\n"
        "• `.تفعيل مجموعات` : صيد محذوفات الكروبات\n"
        "• `.ايقاف خاص` | `.ايقاف مجموعات`\n"
        "• `.تنظيف تفعيل` : مسح القناة كل دقيقة\n"
        f"{FOOTER}"
    )
    await event.edit(text)

# --- [2] إنشاء/فحص القناة (حل مشكلة التكرار) ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل ذاتيه$"))
async def setup_storage(event):
    await event.edit("🔍 **جاري التحقق من وجود قناة تخزين...**")
    
    # البحث عن قناة منشأة مسبقاً بنفس الاسم لتجنب التكرار
    found = False
    async for dialog in client.iter_dialogs():
        if dialog.is_channel and dialog.title == "تخزين محذوفات نيثرون":
            CONFIG["storage_id"] = dialog.id
            found = True
            break
    
    if found:
        await event.edit("✅ **تم العثور على قناة التخزين وربطها بنجاح!**")
    else:
        await event.edit("🌀 **جاري إنشاء قناة تخزين جديدة...**")
        try:
            result = await client(functions.channels.CreateChannelRequest(
                title="تخزين محذوفات نيثرون",
                about="تخزين الرسائل المحذوفة - سورس نيثرون",
                megagroup=False
            ))
            CONFIG["storage_id"] = result.chats[0].id
            await event.edit("✅ **تم إنشاء قناة التخزين وربطها!**")
        except Exception as e:
            await event.edit(f"❌ خطأ: {str(e)}")
            
    await asyncio.sleep(5)
    await event.delete()

# --- [3] أوامر التفعيل والتعطيل ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل (خاص|مجموعات)$"))
async def toggle_on(event):
    mode = event.pattern_match.group(1)
    key = "private_active" if mode == "خاص" else "groups_active"
    
    # شريط تحميل فخم
    bar = ["🌑", "▒ 50%", "██ 100%"]
    for b in bar:
        await event.edit(f"🌀 **تفعيل صيد {mode}...**\n`{b}`")
        await asyncio.sleep(0.4)
        
    CONFIG[key] = True
    await event.edit(f"✅ **تم تفعيل صيد {mode} بنجاح!**")
    await asyncio.sleep(5)
    await event.delete()

# --- [4] كاشف المحذوفات (حل مشكلة المجموعات) ---
@client.on(events.NewMessage)
async def cache_all(event):
    # خزن المعلومات فوراً قبل الحذف
    try:
        sender = await event.get_sender()
        name = "مجهول"
        if sender:
            name = getattr(sender, 'first_name', "مستخدم") or "مجهول"
        
        CONFIG["msg_cache"][event.id] = {
            "text": event.text,
            "media": event.media,
            "sender_name": name,
            "sender_id": event.sender_id,
            "type": "خاص" if event.is_private else "مجموعة"
        }
        # تنظيف الكاش القديم (1000 رسالة)
        if len(CONFIG["msg_cache"]) > 1000:
            CONFIG["msg_cache"].pop(next(iter(CONFIG["msg_cache"])))
    except: pass

@client.on(events.Raw(types.UpdateDeleteMessages))
async def on_delete(event):
    if not CONFIG["storage_id"]: return
    
    for msg_id in event.messages:
        if msg_id in CONFIG["msg_cache"]:
            data = CONFIG["msg_cache"][msg_id]
            
            # فحص النوع المطلوب
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
            
            try:
                await client.send_message(CONFIG["storage_id"], log_text, file=data["media"])
                del CONFIG["msg_cache"][msg_id] # مسح من الذاكرة بعد الصيد
            except: pass

# --- [5] التنظيف التلقائي ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تنظيف (تفعيل|تعطيل)$"))
async def auto_clean_toggle(event):
    cmd = event.pattern_match.group(1)
    CONFIG["auto_clean"] = True if cmd == "تفعيل" else False
    await event.edit(f"🗑 **نظام التنظيف:** {'شغال ✅' if CONFIG['auto_clean'] else 'موقف ❌'}")
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
