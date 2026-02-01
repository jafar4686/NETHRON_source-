import __main__, os, json, asyncio
from telethon import events

client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# قائمة الصلاحيات والرتب المعتمدة في عراق ثون
PERMISSIONS_LIST = ["كتم", "طرد", "حظر", "تفاعلي", "كشف", "تاك"]
RANKS = ["مميز", "ادمن", "مدير", "مطور"]

# --- دالة جلب المسارات ---
def get_perms_path(chat_id):
    if not os.path.exists(BASE_DIR): return None
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            return os.path.join(BASE_DIR, folder, "permissions.json")
    return None

# --- دالة تحميل وحفظ البيانات ---
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
    if not path: return await event.edit("⚠️ **المجموعة غير مفعلة!**")

    # تحميل البيانات
    perms = load_permissions(path)
    
    # تنسيق الرسالة (عراق ثون ستايل)
    msg = "🌀 **إعدادات صلاحيات رتب عراق ثون**\n"
    msg += "━━━━━━━━━━━━━━━━━━━\n"
    
    for rank in RANKS:
        msg += f"👤 **الرتبة : {rank}**\n"
        # عرض الصلاحيات بشكل مصفوفة مرتبة
        p_status = []
        for p in PERMISSIONS_LIST:
            icon = "✅" if perms[rank].get(p) else "❌"
            p_status.append(f" {p} {icon}")
        
        # تقسيم الصلاحيات لسطرين لجمالية المنظر
        msg += f"├ {p_status[0]} | {p_status[1]} | {p_status[2]}\n"
        msg += f"└ {p_status[3]} | {p_status[4]} | {p_status[5]}\n"
        msg += "━━━━━━━━━━━━━━━━━━━\n"
    
    msg += "💡 **للتحكم بالصلاحيات أرسل:**\n"
    msg += "▫️ `.تفعيل [الصلاحية] [الرتبة]`\n"
    msg += "▫️ `.تعطيل [الصلاحية] [الرتبة]`\n"
    msg += "━━━━━━━━━━━━━━━━━━━"
    
    await event.edit(msg)

# ==========================================
# 2. أمر التفعيل والتعطيل مع الدوامة
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(تفعيل|تعطيل) (.*) (مميز|ادمن|مدير|مطور)$"))
async def toggle_perms(event):
    if not event.is_group: return
    
    action = event.pattern_match.group(1) # تفعيل أو تعطيل
    perm_name = event.pattern_match.group(2).strip() # اسم الصلاحية
    rank_name = event.pattern_match.group(3) # الرتبة
    
    path = get_perms_path(event.chat_id)
    if not path: return
    
    if perm_name not in PERMISSIONS_LIST:
        return await event.edit(f"⚠️ **الصلاحية `{perm_name}` غير موجودة!**")

    # تأثير الدوامة الفخم
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري {action} الصلاحية... 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    # تحديث البيانات
    perms = load_permissions(path)
    new_status = True if action == "تفعيل" else False
    perms[rank_name][perm_name] = new_status
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(perms, f, indent=4, ensure_ascii=False)
    
    status_icon = "✅" if new_status else "❌"
    await event.edit(f"⚙️ **عراق ثون: تم {action} ({perm_name}) لرتبة ({rank_name})** {status_icon}")

# ==========================================
# 3. دالة فحص الصلاحية (لاستخدامها في الملفات الأخرى)
# ==========================================
def check_global_permission(chat_id, user_rank, action_key):
    path = get_perms_path(chat_id)
    if not path or not os.path.exists(path): return False
    
    with open(path, "r", encoding="utf-8") as f:
        perms = json.load(f)
        return perms.get(user_rank, {}).get(action_key, False)
