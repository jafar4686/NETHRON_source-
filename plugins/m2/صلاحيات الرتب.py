import __main__, os, json, asyncio
from telethon import events

client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# التوزيع الإجباري اللي ردته (المرجع الأساسي)
RANK_LIMITS = {
    "مميز": ["تفاعلي"],
    "ادمن": ["كتم", "كشف", "تفاعلي", "فك كتم"],
    "مدير": ["طرد", "كتم", "تفاعلي", "كشف", "فك كتم"],
    "مطور": ["كتم", "فك كتم", "حظر", "الغاء حظر", "تفاعلي", "كشف", "طرد", "تاك"]
}

PERMISSIONS_LIST = ["كتم", "طرد", "حظر", "تفاعلي", "كشف", "تاك", "فك كتم", "الغاء حظر"]
RANKS = ["مميز", "ادمن", "مدير", "مطور"]

def get_paths(chat_id):
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return os.path.join(gp, "permissions.json")
    return None

# دالة ذكية: تحدث الملف وتمسح أي صلاحية "زايدة" للمميز أو غيره
def load_and_fix_permissions(path):
    if not os.path.exists(path):
        # إنشاء من الصفر حسب النظام الجديد
        data = {rank: {p: False for p in PERMISSIONS_LIST} for rank in RANKS}
    else:
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = {rank: {p: False for p in PERMISSIONS_LIST} for rank in RANKS}
    
    # الفلترة الصارمة: أي صلاحية مو بالقائمة المسموحة للرتبة تنمسح أو تتصفر
    updated = False
    for rank in RANKS:
        if rank not in data:
            data[rank] = {p: False for p in PERMISSIONS_LIST}
            updated = True
        
        # التأكد من أن الصلاحيات الموجودة مطابقة للمسموح به فقط
        current_rank_perms = list(data[rank].keys())
        for p in current_rank_perms:
            if p not in RANK_LIMITS[rank]: # إذا لقى صلاحية "حظر" عند "مميز" يمسحها
                data[rank].pop(p)
                updated = True
        
        # إضافة الصلاحيات المسموحة إذا كانت مفقودة
        for p in RANK_LIMITS[rank]:
            if p not in data[rank]:
                data[rank][p] = False
                updated = True
                
    if updated:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    return data

# ==========================================
# 1. القائمة الرئيسية (.صلاحيات)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.صلاحيات$"))
async def show_ranks(event):
    if not event.is_group: return
    header = "★────────☭────────★\n   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n★────────☭────────★\n\n• ⌯ **قائمة الرتب المتوفرة :**\n\n"
    body = "".join([f"• 𝑹𝒂𝒏𝒌 ⌯ `{rank}`\n" for rank in RANKS])
    footer = "\n━━━━━━━━━━━━━━━━━━━\n• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯\n💡 للاختيار أرسل: `.صلاحيات + الرتبة`"
    await event.edit(header + body + footer)

# ==========================================
# 2. عرض صلاحيات رتبة (فلترة صارمة)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.صلاحيات (مميز|ادمن|مدير|مطور)$"))
async def show_rank_perms(event):
    path = get_paths(event.chat_id)
    if not path: return await event.edit("⚠️ المجموعة غير مفعلة.")
    rank_name = event.pattern_match.group(1)
    
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري جلب صلاحيات {rank_name}... 〕 {f} ⌯")
        await asyncio.sleep(0.1)
    
    perms = load_and_fix_permissions(path)
    header = "★────────☭────────★\n" + f"   ☭ • 𝑷𝑬𝑹𝑴𝑺 {rank_name.upper()} • ☭\n" + "★────────☭────────★\n\n"
    body = f"• 𝑹𝒂𝒏𝒌 ⌯ `{rank_name}`\n━━━━━━━━━━━━━━━━━━━\n"
    
    # عرض الصلاحيات المسموحة فقط (المميز راح يظهر عنده بس تفاعلي)
    for p, status in perms[rank_name].items():
        icon = "✅" if status else "❌"
        body += f"• {p} ⌯ {icon}\n"
    
    footer = "━━━━━━━━━━━━━━━━━━━\n• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    await event.edit(header + body + footer)

# ==========================================
# 3. التفعيل والتعطيل (مع منع التجاوز)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(تفعيل|تعطيل) (.*) (مميز|ادمن|مدير|مطور)$"))
async def toggle_perms(event):
    action = event.pattern_match.group(1)
    perm_name = event.pattern_match.group(2).strip()
    rank_name = event.pattern_match.group(3)
    
    # منع تفعيل أي شي مو مسموح للرتبة
    if perm_name not in RANK_LIMITS[rank_name]:
        return await event.edit(f"⚠️ **رتبة {rank_name} لا تملك صلاحية {perm_name} أصلاً!**")

    path = get_paths(event.chat_id)
    perms = load_and_fix_permissions(path)
    
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري {action} {perm_name}... 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    perms[rank_name][perm_name] = (action == "تفعيل")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(perms, f, indent=4, ensure_ascii=False)
    
    status_icon = "✅" if action == "تفعيل" else "❌"
    res = "★────────☭────────★\n   ☭ • 𝑼𝑷𝑫𝑨𝑻𝑬 𝑫𝑶𝑵𝑬 • ☭\n★────────☭────────★\n\n" + \
          f"• **تم {action} {perm_name} لـ {rank_name}** {status_icon}\n━━━━━━━━━━━━━━━━━━━\n• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    await event.edit(res)
