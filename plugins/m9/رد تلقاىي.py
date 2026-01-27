import __main__, asyncio, json, os
from telethon import events, Button

# استدعاء الكلاينت (حسابك) والبوت المساعد (الميكر)
client = getattr(__main__, 'client', None)
tgbot = getattr(__main__, 'tgbot', None) 

FAR_DB = "far_config.json"

def load_data():
    if not os.path.exists(FAR_DB):
        return {"status": False, "msg": "", "limit": 3, "users": {}}
    with open(FAR_DB, "r") as f: return json.load(f)

def save_data(data):
    with open(FAR_DB, "w") as f: json.dump(data, f)

# --- أوامر التحكم بالحساب ---
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة فار (.+)"))
async def add_far(event):
    data = load_data()
    data["msg"] = event.pattern_match.group(1)
    save_data(data)
    await event.edit("✅ **تم حفظ الكليشة بنجاح.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(تفعيل|ايقاف) الفار$"))
async def toggle_far(event):
    data = load_data()
    data["status"] = True if "تفعيل" in event.text else False
    save_data(data)
    status = "شغال ✅" if data["status"] else "مطفي ❌"
    await event.edit(f"⚙️ **نظام الفار الآن: {status}**")

# --- محرك الربط: حسابك يراقب والبوت المساعد يرسل ---
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def far_engine(event):
    data = load_data()
    me = await client.get_me()
    
    # فحص الأمان لتجنب الأخطاء البرمجية
    sender = await event.get_sender()
    if not data["status"] or event.sender_id == me.id or (sender and getattr(sender, 'bot', False)):
        return
    
    uid = str(event.sender_id)
    u_data = data["users"].get(uid, 0)
    
    # نظام التحذيرات والكتم
    if u_data >= data["limit"]:
        return 

    u_data += 1
    data["users"][uid] = u_data
    save_data(data)

    if u_data == 1: # يرسل عبر البوت في أول رسالة فقط
        final_msg = data["msg"].replace("$warn", str(data["limit"] - u_data))
        
        # الأزرار اللي تطلع للمستخدم
        buttons = [
            [Button.inline("طلب تحدث 💬", data=f"ask_{uid}")],
            [Button.url("مراسلة الأدمن 👤", url="t.me/xxnnxg")],
            [Button.inline("إرسال رسالة واحدة ✉️", data=f"once_{uid}")]
        ]
        
        # الأمر المباشر للبوت المساعد بالإرسال لهذا الشخص
        try:
            await tgbot.send_message(event.chat_id, final_msg, buttons=buttons)
        except Exception as e:
            print(f"Error via Bot: {e}")

# --- معالجة الأزرار (تتم عبر البوت المساعد) ---
@tgbot.on(events.CallbackQuery)
async def buttons_callback(event):
    query_data = event.data.decode()
    me = await client.get_me()

    if query_data.startswith("ask_"):
        user_id = query_data.split("_")[1]
        await event.answer("تم إرسال طلبك للمالك..", alert=True)
        # إرسال إشعار لحسابك الشخصي
        await client.send_message(me.id, f"👤 المستخدم [{user_id}](tg://user?id={user_id}) يطلب التحدث معك.")

    elif query_data.startswith("once_"):
        await event.edit("✉️ **اكتب رسالتك الآن وسيتم توجيهها للمالك.**")
