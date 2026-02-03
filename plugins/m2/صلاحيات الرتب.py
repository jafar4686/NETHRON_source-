import __main__, os, json, asyncio
from telethon import events

client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# التوزيع الإجباري (المرجع الأساسي للصلاحيات المسموحة)
RANK_LIMITS = {
    "مميز": ["تفاعلي"],
    "ادمن": ["كتم", "كشف", "تفاعلي", "فك كتم"],
    "مدير": ["طرد", "كتم", "تفاعلي", "كشف", "فك كتم"],
    "مطور": ["كتم", "فك كتم", "حظر", "الغاء حظر", "تفاعلي", "كشف", "طرد", "تاك"]
}

RANKS = list(RANK_LIMITS.keys())

# دالة جلب مسار ملف الصلاحيات
def get_perms_path(chat_id):
    if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return os.path.join(gp, "permissions.json")
    return None

# دالة تحميل وتنظيف البيانات (تضمن عدم ضياع التفعيل)
def load_perms(path):
    # إذا الملف ما موجود ننشأه بالقيم الافتراضية (False)
    if not os.path.exists(path):
        data = {rank: {p: False for p in RANK_LIMITS[rank]} for rank in RANKS}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return data
    
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except:
            data = {rank: {p: False for p in RANK_LIMITS[rank]} for rank in RANKS}

    # عملية الفلترة الذكية: مسح الصلاحيات غير المسموحة وإضافة الجديدة
    updated = False
    for rank in RANKS:
        if rank not in data:
            data[rank] = {p: False for p in RANK_LIMITS[rank]}
            updated = True
            continue
        
        # حذف أي صلاحية مو بالقائمة المسموحة لهذي الرتبة (مثلاً حظر عند المميز)
        to_delete = [p for p in data[rank] if p not in RANK_LIMITS[rank]]
        for p in to_delete:
            data[rank].pop(p)
            updated = True
            
        # إضافة الصلاحيات المفقودة كـ False (بدون تصفير الموجود)
        for p in RANK_LIMITS[rank]:
            if p not in data[rank]:
                data[rank][p] = False
                updated = True
                
    if updated:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    return data

# ==========================================
# 1. عرض الرتب (.صلاحيات)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.صلاحيات$"))
async def show_ranks(event):
    if not event.is_group: return
    header = "★────────☭────────★\n   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 𝑷𝑬𝑹𝑴𝑺 • ☭\n★────────☭────────★\n\n• ⌯ **قائمة الرتب المتاحة للتحكم :**\n\n"
    body = "".join([f"• 𝑹𝒂𝒏𝒌 ⌯ `{rank}`\n" for rank in RANKS])
    footer = "\n━━━━━━━━━━━━━━━━━━━\n• للتحكم أرسل: `.صلاحيات + الرتبة`"
    await event.edit(header + body + footer)

# ==========================================
# 2. عرض صلاحيات رتبة محددة
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.صلاحيات (مميز|ادمن|مدير|مطور)$"))
async def show_rank_perms(event):
    path = get_perms_path(event.chat_id)
    if not path: return await event.edit("⚠️ **يجب تفعيل المجموعة أولاً!**")
    
    rank_name = event.pattern_match.group(1)
    perms_data = load_perms(path)
    
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري جلب بيانات {rank_name}... 〕 {f} ⌯")
        await asyncio.sleep(0.1)
    
    header = "★────────☭────────★\n" + f"   ☭ • 𝑺𝑬𝑻𝑻𝑰𝑵𝑮𝑺: {rank_name} • ☭\n" + "★────────☭────────★\n\n"
    body = ""
    
    for p, status in perms_data[rank_name].items():
        icon = "✅" if status else "❌"
        body += f"• {p} ⌯ {icon}\n"
    
    footer = "\n━━━━━━━━━━━━━━━━━━━\n• للتعديل: `.تفعيل/تعطيل [الصلاحية] [الرتبة]`"
    await event.edit(header + body + footer)

# ==========================================
# 3. التفعيل والتعطيل (الحفظ الفوري)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(تفعيل|تعطيل) (.*) (مميز|ادمن|مدير|مطور)$"))
async def toggle_perms(event):
    action = event.pattern_match.group(1)
    perm_name = event.pattern_match.group(2).strip()
    rank_name = event.pattern_match.group(3)
    
    path = get_perms_path(event.chat_id)
    if not path: return await event.edit("⚠️ المجموعة غير مفعلة.")

    # 1. التأكد هل الصلاحية مسموحة لهذه الرتبة؟
    if perm_name not in RANK_LIMITS[rank_name]:
        return await event.edit(f"⚠️ **عذراً، رتبة {rank_name} لا تدعم صلاحية {perm_name}!**")

    # 2. تحميل البيانات وتعديلها
    perms_data = load_perms(path)
    is_on = (action == "تفعيل")
    
    if perms_data[rank_name].get(perm_name) == is_on:
        return await event.edit(f"🔔 **صلاحية {perm_name} لـ {rank_name} هي بالفعل {action}ة!**")

    perms_data[rank_name][perm_name] = is_on

    # 3. الحفظ الفوري في الملف
    with open(path, "w", encoding="utf-8") as f:
        json.dump(perms_data, f, indent=4, ensure_ascii=False)
    
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري حفظ التعديلات... 〕 {f} ⌯")
        await asyncio.sleep(0.1)
    
    status_icon = "✅" if is_on else "❌"
    res = "★────────☭────────★\n   ☭ • 𝑼𝑷𝑫𝑨𝑻𝑬 𝑺𝑼𝑪𝑪𝑬𝑺𝑺 • ☭\n★────────☭────────★\n\n" + \
          f"• **الرتبة:** `{rank_name}`\n" + \
          f"• **الإجراء:** {action} {perm_name} {status_icon}\n" + \
          "━━━━━━━━━━━━━━━━━━━\n• تم تحديث قاعدة بيانات المجموعة بنجاح."
    await event.edit(res)
