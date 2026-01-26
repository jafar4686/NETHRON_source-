import os, sys, asyncio, glob, importlib.util, __main__, subprocess, random, string, json
from telethon import TelegramClient, events, Button, types, functions
from telethon.sessions import StringSession
from datetime import datetime, timedelta
# تم حذف dateutil لتجنب خطأ ModuleNotFoundError
from config import api_id, api_hash

# --- الإعدادات الأساسية ---
BOT_TOKEN = "8136996400:AAEO4uDFUweXXiz49bs91hI_jmvBqh8CStI"
DB_FILE = "nethron_vips.json"
DEV_ID = "@NETH_RON"
DEV2_ID = "@xxnnxg"

bot = TelegramClient('MakerBot', api_id, api_hash).start(bot_token=BOT_TOKEN)

# --- إدارة قاعدة البيانات ---
def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "codes": {}}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"users": {}, "codes": {}}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_nethron_code(days):
    rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{days}D_NETHRON_{rand}"

# ==========================================
# 1. الترحيب والقائمة الرئيسية
# ==========================================
@bot.on(events.NewMessage(pattern=r"/start"))
async def start(event):
    db = load_db()
    uid = str(event.sender_id)
    status = "غير مشترك ❌"
    
    if uid in db["users"]:
        exp = datetime.fromisoformat(db["users"][uid])
        if exp > datetime.now():
            status = f"مشترك ✅ (ينتهي: {exp.strftime('%Y-%m-%d')})"
    
    msg = (
        "★──────────☭──────────★\n"
        "   ☭ • **𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 𝑉𝐼𝑃** • ☭\n"
        "★──────────☭──────────★\n\n"
        f"👤 **حالتك:** {status}\n\n"
        "مرحباً بك في نظام التنصيب التلقائي المدفوع.\n"
        "➥ 𝑫𝑬𝑽 : " + DEV_ID + "\n"
        "➥ 𝑨𝑫𝑴𝑰𝑵 : " + DEV2_ID + "\n"
        "★──────────☭──────────★"
    )
    buttons = [
        [Button.inline("🌟 شراء اشتراك (نجوم)", b"buy_menu")],
        [Button.inline("🎟️ تفعيل كود", b"use_code")],
        [Button.inline("📱 لوحة التنصيب /P", b"open_panel")]
    ]
    await event.respond(msg, buttons=buttons)

# ==========================================
# 2. نظام الدفع وتوليد الأكواد
# ==========================================
@bot.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode()
    uid = str(event.sender_id)
    db = load_db()

    if data == "buy_menu":
        btns = [[Button.inline("شهر (15⭐)", b"pay_30"), Button.inline("شهرين (25⭐)", b"pay_60")]]
        await event.edit("💎 **اختر المدة:**", buttons=btns)

    elif data.startswith("pay_"):
        days = int(data.split("_")[1])
        price = 15 if days == 30 else 25
        invoice = types.InputMediaInvoice(
            title=f"اشتراك {days} يوم",
            description=f"تفعيل سورس نيثرون لمدة {days} يوم",
            invoice_payload=f"pay_{days}_{uid}",
            provider="", currency="XTR",
            prices=[types.LabeledPrice(label="النجوم", amount=price)],
            start_param="nethron"
        )
        await bot.send_message(event.chat_id, "📥 **ادفع النجوم للاشتراك:**", file=invoice)

    elif data == "use_code":
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("🎟️ **أرسل كود التفعيل:**")
            res = await conv.get_response()
            code = res.text.strip()
            if code in db["codes"]:
                days = db["codes"][code]["days"]
                db["users"][uid] = (datetime.now() + timedelta(days=days)).isoformat()
                del db["codes"][code]
                save_db(db)
                await conv.send_message(f"🎉 **تم التفعيل لـ {days} يوم!**")
            else:
                await conv.send_message("❌ **الكود خاطئ!**")

    elif data == "open_panel":
        await control_panel(event)

# التحقق من الدفع وتصحيح خطأ AttributeError
@bot.on(events.Raw(types.UpdateBotPrecheckoutQuery))
async def precheckout(event):
    await bot(functions.messages.SetBotPrecheckoutResultsRequest(query_id=event.query_id, success=True))

@bot.on(events.NewMessage)
async def payment_receiver(event):
    if event.message.action and isinstance(event.message.action, types.MessageActionPaymentSentMe):
        db = load_db()
        payload = event.message.action.payload.decode()
        days, uid = int(payload.split("_")[1]), payload.split("_")[2]
        new_code = generate_nethron_code(days)
        db["codes"][new_code] = {"days": days}
        save_db(db)
        await bot.send_message(int(uid), f"✅ **تم الدفع! كودك هو:**\n`{new_code}`")

# ==========================================
# 3. لوحة التنصيب /P
# ==========================================
async def control_panel(event):
    db = load_db()
    uid = str(event.sender_id)
    if uid not in db["users"] or datetime.fromisoformat(db["users"][uid]) < datetime.now():
        return await event.respond("⚠️ **يجب الاشتراك أولاً.**")

    buttons = [[Button.inline("➕ إضافة حساب", b"add_acc")]]
    await event.respond("⚙️ **لوحة التحكم**", buttons=buttons)

@bot.on(events.CallbackQuery(data=b"add_acc"))
async def add_acc(event):
    async with bot.conversation(event.chat_id) as conv:
        await conv.send_message("📱 **أرسل الرقم مع الرمز (+964...):**")
        phone = (await conv.get_response()).text.strip().replace(" ", "")
        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()
        try:
            await client.send_code_request(phone)
            await conv.send_message("📥 **أرسل الكود:**")
            code = (await conv.get_response()).text.replace(" ", "")
            await client.sign_in(phone, code)
            with open("database.txt", "a") as f: f.write(f"{client.session.save()}\n")
            await conv.send_message("✅ **تم التنصيب بنجاح!**")
        except Exception as e: await conv.send_message(f"❌ خطأ: {e}")
