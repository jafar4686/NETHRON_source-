import __main__, asyncio, json, os, re
from telethon import events

# استدعاء الكلاينت من المحرك الأساسي
client = getattr(__main__, 'client', None)
FAR_DB = "far_data.json"

def load_data():
    if not os.path.exists(FAR_DB):
        return {"status": False, "msg": "", "warn_limit": 10, "users": {}}
    with open(FAR_DB, "r") as f: return json.load(f)

def save_data(data):
    with open(FAR_DB, "w") as f: json.dump(data, f)

# 1. أمر الإضافة مع تحديد عدد التحذيرات تلقائياً
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة فار (.+)"))
async def add_far(event):
    input_text = event.pattern_match.group(1)
    data = load_data()
    
    # البحث عن رقم التحذيرات بعد السلاش مثل $warn/5
    match = re.search(r"\$warn/(\d+)", input_text)
    if match:
        data["warn_limit"] = int(match.group(1))
        # تنظيف الكليشة من الرقم لإبقائها نظيفة عند الرد
        data["msg"] = input_text.replace(f"/{match.group(1)}", "")
    else:
        data["msg"] = input_text
        data["warn_limit"] = 10 # الافتراضي
        
    save_data(data)
    await event.edit(f"✅ **تم حفظ كليشة الفار:**\n• عدد التحذيرات: {data['warn_limit']}\n• النص: {data['msg']}")

# 2. أوامر التحكم
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(تفعيل|ايقاف) فار$"))
async def toggle_far(event):
    data = load_data()
    data["status"] = True if "تفعيل" in event.text else False
    data["users"] = {} # تصفير القائمة لبدء التحذير من جديد
    save_data(data)
    await event.edit(f"⚙️ **نظام الفار الآن: {'شغال ✅' if data['status'] else 'مطفي ❌'}**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حذف الفار$"))
async def del_far(event):
    if os.path.exists(FAR_DB): os.remove(FAR_DB)
    await event.edit("🗑️ **تم حذف إعدادات الفار بالكامل.**")

# 3. محرك الرد والتحذير (الذكاء الاصطناعي للفار)
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def far_engine(event):
    data = load_data()
    me = await client.get_me()
    
    if not data["status"] or event.sender_id == me.id or event.is_bot: return
    
    uid = str(event.sender_id)
    user_warns = data["users"].get(uid, 0)
    
    # إذا تجاوز الحد المسموح
    if user_warns >= data["warn_limit"]:
        return # يتوقف السورس عن الرد (كتم)

    # زيادة العداد
    user_warns += 1
    data["users"][uid] = user_warns
    save_data(data)

    # الرد بالكليشة
    warn_left = data["warn_limit"] - user_warns
    # استبدال المتغير بالعدد المتبقي
    final_reply = data["msg"].replace("$warn", str(warn_left))
    
    # إضافة تعليمات التواصل كـ نص (لأنها أسهل برمجياً وأضمن)
    final_reply += f"\n\n👤 لمراسلة الأدمن: @xxnnxg\n✉️ اترك رسالتك الآن وسيتم الرد عليك."
    
    await event.reply(final_reply)

# 4. قائمة الأوامر .م10
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م10$"))
async def menu10(event):
    text = (
        "🛡️ **قائمة نظام الفار (الحماية):**\n"
        "•──────────────•\n"
        "• `.اضافة فار` [الكليشة] $warn/10\n"
        "• `.تفعيل فار` / `.ايقاف فار` \n"
        "• `.حذف الفار` \n"
        "•──────────────•\n"
        "💡 **ملاحظة:** ضع $warn/ متبوعاً برقم لتحديد عدد التحذيرات."
    )
    await event.edit(text)
