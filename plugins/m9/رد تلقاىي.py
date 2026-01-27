import __main__, asyncio, json, os
from telethon import events, Button

# استدعاء الكلاينت وتوكن البوت المساعد من الميكر مباشرة
client = getattr(__main__, 'client', None)
tgbot = getattr(__main__, 'tgbot', None) 

FAR_DB = "far_config.json"

def load_data():
    if not os.path.exists(FAR_DB):
        return {"status": False, "msg": "", "limit": 3, "users": {}}
    with open(FAR_DB, "r") as f: return json.load(f)

def save_data(data):
    with open(FAR_DB, "w") as f: json.dump(data, f)

# 1. أوامر التحكم (تنكتب بالحساب الرسمي)
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة فار (.+)"))
async def add_far(event):
    msg = event.pattern_match.group(1)
    data = load_data()
    data["msg"] = msg
    save_data(data)
    await event.edit("✅ **تم حفظ كليشة الفار بنجاح.**\n• لا تنسى استخدام $warn للتحذيرات.")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(تفعيل|ايقاف) الفار$"))
async def toggle_far(event):
    data = load_data()
    data["status"] = True if "تفعيل" in event.text else False
    save_data(data)
    status = "شغال ✅" if data["status"] else "معطل ❌"
    await event.edit(f"⚙️ **نظام الفار الآن: {status}**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حذف فار$"))
async def del_far(event):
    if os.path.exists(FAR_DB): os.remove(FAR_DB)
    await event.edit("🗑️ **تم حذف بيانات الفار بالكامل.**")

# 2. محرك الحماية (يرد على الناس بالخاص)
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def far_engine(event):
    data = load_data()
    me = await client.get_me()
    if not data["status"] or event.sender_id == me.id or event.is_bot: return
    
    uid = str(event.sender_id)
    u_data = data["users"].get(uid, 0)
    
    # إذا تجاوز حد التحذيرات
    if u_data >= data["limit"]:
        return # هنا الشخص مكتوم تلقائياً لأن السورس ما راح يرد عليه بعد

    u_data += 1
    data["users"][uid] = u_data
    save_data(data)

    if u_data <= data["limit"]:
        warn_left = data["limit"] - u_data
        # استبدال متغير التحذير بالنص
        final_msg = data["msg"].replace("$warn", str(warn_left))
        
        # الأزرار الشفافة عبر البوت المساعد
        buttons = [
            [Button.inline("طلب تحدث 💬", data=f"ask_{uid}")],
            [Button.url("مراسلة الأدمن 👤", url="t.me/xxnnxg")],
            [Button.inline("إرسال رسالة واحدة ✉️", data=f"once_{uid}")]
        ]
        
        try:
            await tgbot.send_message(event.chat_id, final_msg, buttons=buttons)
        except:
            await event.reply(final_msg)

# 3. معالج ضغطات الأزرار (عبر التوكن)
@tgbot.on(events.CallbackQuery)
async def buttons_callback(event):
    data = event.data.decode()
    uid = event.sender_id
    me = await client.get_me()

    if data.startswith("ask_"):
        await event.answer("تم إرسال طلبك.. انتظر الرد.", alert=True)
        await client.send_message(me.id, f"👤 المستخدم [{uid}](tg://user?id={uid}) يطلب التحدث معك.")

    elif data.startswith("once_"):
        await event.edit("✉️ **اكتب رسالتك الآن وسيتم توجيهها للمالك فوراً.**")
        # يتم توجيه الرسالة القادمة للمالك (اختياري)
