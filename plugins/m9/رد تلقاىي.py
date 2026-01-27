import __main__, asyncio, json, os
from telethon import events, Button

# استدعاء الربط من الميكر
client = getattr(__main__, 'client', None)
tgbot = getattr(__main__, 'tgbot', None) 

FAR_DB = "far_config.json"

def load_data():
    if not os.path.exists(FAR_DB):
        return {"status": False, "msg": "", "limit": 3, "users": {}}
    with open(FAR_DB, "r") as f: return json.load(f)

def save_data(data):
    with open(FAR_DB, "w") as f: json.dump(data, f)

# --- أوامر التحكم (بالحساب الشخصي) ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة فار (.+)"))
async def add_far(event):
    data = load_data()
    data["msg"] = event.pattern_match.group(1)
    save_data(data)
    await event.edit("✅ **تم حفظ كليشة الفار بنجاح.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(تفعيل|ايقاف) الفار$"))
async def toggle_far(event):
    data = load_data()
    data["status"] = True if "تفعيل" in event.text else False
    save_data(data)
    status = "شغال ✅" if data["status"] else "مطفي ❌"
    await event.edit(f"⚙️ **نظام الفار الآن: {status}**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حذف فار$"))
async def del_far(event):
    if os.path.exists(FAR_DB): os.remove(FAR_DB)
    await event.edit("🗑️ **تم حذف بيانات الفار.**")

# --- محرك الحماية (حسابك يراقب والبوت يرسل) ---
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def far_engine(event):
    data = load_data()
    me = await client.get_me()
    
    # فحص الأمان لتجنب خطأ AttributeError
    sender = await event.get_sender()
    is_bot = getattr(sender, 'bot', False) 
    
    if not data["status"] or event.sender_id == me.id or is_bot:
        return
    
    uid = str(event.sender_id)
    u_data = data["users"].get(uid, 0)
    
    # إذا تجاوز الحد، يتوقف السورس عن الرد (كتم تلقائي)
    if u_data >= data["limit"]:
        return 

    u_data += 1
    data["users"][uid] = u_data
    save_data(data)

    if u_data == 1: # الإرسال في أول رسالة فقط
        # معالجة متغير التحذيرات $warn
        warn_text = str(data["limit"] - u_data)
        final_msg = data["msg"].replace("$warn", warn_text)
        
        # الأزرار الشفافة
        buttons = [
            [Button.inline("طلب تحدث 💬", data=f"ask_{uid}")],
            [Button.url("مراسلة الأدمن 👤", url="https://t.me/xxnnxg")],
            [Button.inline("إرسال رسالة واحدة ✉️", data=f"once_{uid}")]
        ]
        
        # الإرسال عبر البوت المساعد المربوط tgbot
        try:
            await tgbot.send_message(event.chat_id, final_msg, buttons=buttons)
        except: pass

# --- معالج الأزرار (عبر البوت المساعد tgbot) ---
@tgbot.on(events.CallbackQuery)
async def buttons_callback(event):
    query = event.data.decode()
    me = await client.get_me()

    if query.startswith("ask_"):
        await event.answer("تم إرسال طلبك للمالك..", alert=True)
        await client.send_message(me.id, f"👤 المستخدم [{event.sender_id}](tg://user?id={event.sender_id}) يطلب التحدث.")

    elif query.startswith("once_"):
        await event.edit("✉️ **اكتب رسالتك الآن وسيتم توجيهها للمالك فوراً.**")
