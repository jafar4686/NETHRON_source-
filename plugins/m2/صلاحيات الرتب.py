import __main__, os, json, asyncio
from telethon import events

client = getattr(__main__, 'client', None)
BASE_DIR = "group"

# قائمة الصلاحيات المتوفرة (كتم، طرد، حظر، إلخ)
PERMISSIONS_LIST = ["كتم", "طرد", "حظر", "تفاعلي", "كشف", "تاك"]
RANKS = ["مميز", "ادمن", "مدير", "مطور"]

# --- دالة جلب مسار ملف الصلاحيات ---
def get_perms_path(chat_id):
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            return os.path.join(BASE_DIR, folder, "permissions.json")
    return None

# --- إنشاء إعدادات افتراضية إذا الملف مو موجود ---
def load_permissions(path):
    if not os.path.exists(path):
        data = {rank: {p: False for p in PERMISSIONS_LIST} for rank in RANKS}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return data
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ==========================================
# 1. أمر عرض الصلاحيات (.صلاحيات)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.صلاحيات$"))
async def show_perms(event):
    if not event.is_group: return
    path = get_perms_path(event.chat_id)
    if not path: return await event.edit("⚠️ **المجموعة غير مفعلة.**")

    perms = load_permissions(path)
    
    msg = "🌀 **إعدادات صلاحيات رتب عراق ثون**\n"
    msg += "━━━━━━━━━━━━━━━━━━━\n"
    for rank in RANKS:
        msg += f"👤 **رتبة {rank}:**\n"
        for p in PERMISSIONS_LIST:
            status = "✅" if perms[rank].get(p) else "❌"
            msg += f"  ├ {p} ← {status}\n"
        msg += "━━━━━━━━━━━━━━━━━━━\n"
    
    msg += "\n💡 **للتحكم استخدم الأوامر التالية:**\n"
    msg += "▫️ `.تفعيل [الصلاحية] [الرتبة]`\n"
    msg += "▫️ `.تعطيل [الصلاحية] [الرتبة]`\n"
    msg += "▫️ *مثال:* `.تفعيل كتم مميز`"
    
    await event.edit(msg)

# ==========================================
# 2. أمر التفعيل والتعطيل (.تفعيل / .تعطيل)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(تفعيل|تعطيل) (.*) (مميز|ادمن|مدير|مطور)$"))
async def toggle_perms(event):
    if not event.is_group: return
    
    action = event.pattern_match.group(1) # تفعيل أو تعطيل
    perm_name = event.pattern_match.group(2).strip() # اسم الصلاحية
    rank_name = event.pattern_match.group(3) # الرتبة
    
    if perm_name not in PERMISSIONS_LIST:
        return await event.edit(f"⚠️ **الصلاحية `{perm_name}` غير موجودة!**\nالمتوفر: (كتم، طرد، حظر، تفاعلي، كشف، تاك)")

    path = get_perms_path(event.chat_id)
    perms = load_permissions(path)
    
    # تحديث الحالة
    new_status = True if action == "تفعيل" else False
    perms[rank_name][perm_name] = new_status
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(perms, f, indent=4, ensure_ascii=False)
    
    status_icon = "✅" if new_status else "❌"
    await event.edit(f"⚙️ **تم {action} صلاحية ({perm_name}) لرتبة ({rank_name})** {status_icon}")

# ==========================================
# دالة نستخدمها بملفات الأوامر (الكتم، الطرد..) لفحص الصلاحية
# ==========================================
def can_use_cmd(chat_id, user_id, action_key):
    # 1. نجيب رتبة الشخص من member_rank.json
    # (هنا تفترض وجود دالة تجيب رتبة الشخص)
    # 2. نفتح permissions.json ونشوف القيمة True لو False
    # ترجع True أو False
    pass
