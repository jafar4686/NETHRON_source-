import __main__
import asyncio
import re
from telethon import events, types
from telethon.tl.functions.channels import CreateChannelRequest
from datetime import datetime
import pytz

client = __main__.client
IRAQ_TZ = pytz.timezone("Asia/Baghdad")

# =========================
# 🧠 التخزين والبيانات
# =========================
if not hasattr(__main__, "self_delete_config"):
    __main__.self_delete_config = {
        "private": False,
        "groups": False,
        "storage_id": None,
        "cleaner_task": None,
        "clean_interval": 60, # دقيقة واحدة
        "cache": {} # لحفظ الرسائل قبل حذفها
    }

CONFIG = __main__.self_delete_config

HEADER = (
    "★────────☭────────★\n"
    "   ☭ • 𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 • ☭\n"
    "                  ☭ • سورس نيثرون • ☭\n"
    "★────────☭────────★\n"
)

# =========================
# 🛠️ أدوات مساعدة
# =========================
def get_time():
    return datetime.now(IRAQ_TZ).strftime("%I:%M:%S %p")

async def ensure_storage(event):
    """إنشاء قناة التخزين إذا لم تكن موجودة"""
    if CONFIG["storage_id"]:
        return CONFIG["storage_id"]
    
    await event.edit("⚙️ **يتم إنشاء قناة التخزين...**\n`▒▒▒▒▒▒▒▒▒▒ 0%`")
    await asyncio.sleep(1)
    await event.edit("⚙️ **يتم إنشاء قناة التخزين...**\n`██████▒▒▒▒ 60%`")
    
    try:
        result = await client(CreateChannelRequest(
            title="أرشيف حذف نيثرون 🗑️",
            about="هذه القناة مخصصة لحفظ الرسائل المحذوفة تلقائياً بواسطة سورس نيثرون.",
            megagroup=True
        ))
        CONFIG["storage_id"] = result.chats[0].id
        await event.edit("✅ **تم إنشاء قناة التخزين بنجاح!**")
        await asyncio.sleep(2)
        return CONFIG["storage_id"]
    except Exception as e:
        await event.edit(f"❌ **فشل إنشاء القناة:** {str(e)}")
        return None

# =========================
# 🎮 أوامر التحكم (م6)
# =========================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل ذاتيه$"))
async def enable_self_system(event):
    await ensure_storage(event)
    await event.edit(HEADER + "🚀 **نظام الذاتية جاهز للعمل!**\n\nاستخدم `.تفعيل خاص` أو `.تفعيل مجموعات` لبدء المراقبة.")
    await asyncio.sleep(10)
    await event.delete()

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل (خاص|مجموعات)$"))
async def toggle_modes(event):
    mode = event.pattern_match.group(1)
    await ensure_storage(event)
    
    # تحميل فخم
    bar = ""
    for i in range(1, 6):
        bar = "█" * i + "▒" * (5-i)
        await event.edit(f"🛡️ **جاري تفعيل مراقبة {mode}...**\n`{bar}`")
        await asyncio.sleep(0.3)
    
    if mode == "خاص":
        CONFIG["private"] = True
    else:
        CONFIG["groups"] = True
        
    await event.edit(f"✅ **تم تفعيل مراقبة {mode} بنجاح!**")
    await asyncio.sleep(10)
    await event.delete()

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف ذاتيه (خاص|مجموعات)$"))
async def disable_modes(event):
    mode = event.pattern_match.group(1)
    if mode == "خاص":
        CONFIG["private"] = False
    else:
        CONFIG["groups"] = False
    
    await event.edit(f"⛔ **تم إيقاف مراقبة {mode}**")
    await asyncio.sleep(10)
    await event.delete()

# =========================
# 🗑️ نظام تنظيف القناة
# =========================
async def auto_cleaner():
    while True:
        if CONFIG["storage_id"]:
            try:
                # حذف جميع الرسائل في قناة التخزين (تباعاً)
                async for message in client.iter_messages(CONFIG["storage_id"]):
                    await message.delete()
                    await asyncio.sleep(CONFIG["clean_interval"])
            except:
                pass
        await asyncio.sleep(10)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل حذف رسائل$"))
async def start_cleaning(event):
    if CONFIG["cleaner_task"]:
        return await event.edit("⚠️ **النظام يعمل بالفعل.**")
    
    CONFIG["cleaner_task"] = asyncio.create_task(auto_cleaner())
    await event.edit("🧹 **تم تفعيل نظام تنظيف الأرشيف التلقائي (كل دقيقة رسالة).**")
    await asyncio.sleep(10)
    await event.delete()

# =========================
# 🕵️ محرك كشف الحذف
# =========================
@client.on(events.NewMessage)
async def cache_handler(event):
    # تخزين كل الرسائل الواردة في الذاكرة المؤقتة لمقارنتها عند الحذف
    if event.is_private or event.is_group:
        CONFIG["cache"][event.id] = event.message

@client.on(events.Raw(types.UpdateDeleteMessages))
async def delete_handler(event):
    if not CONFIG["storage_id"]:
        return

    for msg_id in event.messages:
        if msg_id in CONFIG["cache"]:
            msg = CONFIG["cache"][msg_id]
            
            # التحقق من الإعدادات (خاص أو مجموعات)
            is_priv = isinstance(msg.to_id, types.PeerUser)
            if is_priv and not CONFIG["private"]: continue
            if not is_priv and not CONFIG["groups"]: continue

            sender = await msg.get_sender()
            name = sender.first_name if sender else "مجهول"
            chat_type = "👤 خاص" if is_priv else "👥 مجموعة"
            
            info = (
                f"{HEADER}\n"
                f"🕵️ **كشف حذف رسالة جديدة**\n"
                f"━━━━━━━━━━━━━━\n"
                f"👤 **المرسل:** {name}\n"
                f"🆔 **الايدي:** `{msg.sender_id}`\n"
                f"📍 **النوع:** {chat_type}\n"
                f"⏰ **وقت الحذف:** `{get_time()}`\n"
                f"━━━━━━━━━━━━━━\n"
                f"📩 **المحتوى:**\n\n{msg.text or 'وسائط/ملف'}"
            )

            try:
                await client.send_message(CONFIG["storage_id"], info)
                if msg.media:
                    await client.send_file(CONFIG["storage_id"], msg.media)
            except:
                pass

# =========================
# 📋 قائمة الأوامر م6
# =========================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م6$"))
async def self_menu(event):
    menu = (
        f"{HEADER}\n"
        "🛠️ **أوامر الذاتية وكشف الحذف:**\n\n"
        "• `.تفعيل ذاتيه` : إنشاء القناة وتهيئة النظام\n"
        "• `.تفعيل خاص` : بدء كشف الحذف في الخاص\n"
        "• `.تفعيل مجموعات` : بدء كشف الحذف في الكروبات\n"
        "• `.ايقاف ذاتيه خاص` : تعطيل الخاص\n"
        "• `.ايقاف ذاتيه مجموعات` : تعطيل المجموعات\n"
        "• `.تفعيل حذف رسائل` : تنظيف تلقائي للأرشيف\n"
        "\n"
        "⚠️ **ملاحظة:** يتم حذف رسالة التفعيل تلقائياً بعد 10 ثوانٍ."
    )
    await event.edit(menu)
