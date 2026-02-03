import __main__, os, json, asyncio
from telethon import events

client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# تعريف الهرمية (للاستخدام لاحقاً في ملفات الأوامر)
RANK_HIERARCHY = {"مميز": 1, "ادمن": 2, "مدير": 3, "مطور": 4, "owner": 5}

# تقييد الصلاحيات حسب طلبك
RANK_LIMITS = {
    "مميز": ["تفاعلي"],
    "ادمن": ["كتم", "كشف", "تفاعلي", "فك كتم"],
    "مدير": ["طرد", "كتم", "تفاعلي", "كشف", "فك كتم"],
    "مطور": ["كتم", "فك كتم", "حظر", "الغاء حظر", "تفاعلي", "كشف", "طرد", "تاك"]
}

PERMISSIONS_LIST = ["كتم", "طرد", "حظر", "تفاعلي", "كشف", "تاك", "فك كتم", "الغاء حظر"]
RANKS = ["مميز", "ادمن", "مدير", "مطور"]

# --- جلب المسارات ---
def get_paths(chat_id):
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return os.path.join(gp, "permissions.json"), os.path.join(gp, "member_rank.json")
    return None, None

# --- تحميل وتحديث الصلاحيات تلقائياً ---
def load_permissions(path):
    if not os.path.exists(path):
        data = {rank: {p: False for p in PERMISSIONS_LIST} for rank in RANKS}
    else:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    
    # التأكد من وجود كل الرتب والصلاحيات (تحديث الملف القديم)
    updated = False
    for rank in RANKS:
        if rank not in data:
            data[rank] = {p: False for p in PERMISSIONS_LIST}
            updated = True
        for p in PERMISSIONS_LIST:
            if p not in data[rank]:
                data[rank][p] = False
                updated = True
    
    if updated:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    return data

# ==========================================
# 1. أمر عرض الرتب (.صلاحيات)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.صلاحيات$"))
async def show_ranks(event):
    if not event.is_group: return
    
    header = (
        "★────────☭────────★\n"
        "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
        "★────────☭────────★\n\n"
        "• ⌯ **قائمة الرتب المتوفرة :**\n\n"
    )
    body = ""
    for rank in RANKS:
        body += f"• 𝑹𝒂𝒏𝒌 ⌯ `{rank}`\n"
    
    footer = (
        "\n━━━━━━━━━━━━━━━━━━━\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯\n"
        "💡 للاختيار أرسل: `.صلاحيات + الرتبة`"
    )
    await event.edit(header + body + footer)

# ==========================================
# 2. عرض صلاحيات رتبة (مقيدة حسب الهرمية)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.صلاحيات (مميز|ادمن|مدير|مطور)$"))
async def show_rank_perms(event):
    path_perms, _ = get_paths(event.chat_id)
    if not path_perms: return await event.edit("⚠️ المجموعة غير مفعلة.")
    
    rank_name = event.pattern_match.group(1)
    
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري جلب صلاحيات {rank_name}... 〕 {f} ⌯")
        await asyncio.sleep(0.1)
    
    perms = load_permissions(path_perms)
    header = "★────────☭────────★\n" + f"   ☭ • 𝑷𝑬𝑹𝑴𝑺 {rank_name.upper()} • ☭\n" + "★────────☭────────★\n\n"
    body = f"• 𝑹𝒂𝒏𝒌 ⌯ `{rank_name}`\n━━━━━━━━━━━━━━━━━━━\n"
    
    # عرض الصلاحيات المسموحة فقط لهذه الرتبة
    allowed = RANK_LIMITS.get(rank_name, [])
    for p in allowed:
        status = "✅" if perms.get(rank_name, {}).get(p) else "❌"
        body += f"• {p} ⌯ {status}\n"
    
    footer = "━━━━━━━━━━━━━━━━━━━\n• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    await event.edit(header + body + footer)

# ==========================================
# 3. أمر التفعيل والتعطيل (تحديث permissions.json)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(تفعيل|تعطيل) (.*) (مميز|ادمن|مدير|مطور)$"))
async def toggle_perms(event):
    action = event.pattern_match.group(1)
    perm_name = event.pattern_match.group(2).strip()
    rank_name = event.pattern_match.group(3)
    
    # فحص القيود
    if perm_name not in RANK_LIMITS[rank_name]:
        return await event.edit(f"⚠️ **رتبة {rank_name} لا تدعم صلاحية {perm_name}!**")

    path_perms, _ = get_paths(event.chat_id)
    perms = load_permissions(path_perms)
    
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري {action} {perm_name}... 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    perms[rank_name][perm_name] = (action == "تفعيل")
    with open(path_perms, "w", encoding="utf-8") as f:
        json.dump(perms, f, indent=4, ensure_ascii=False)
    
    status_icon = "✅" if action == "تفعيل" else "❌"
    res = (
        "★────────☭────────★\n"
        "   ☭ • 𝑼𝑷𝑫𝑨𝑻𝑬 𝑫𝑶𝑵𝑬 • ☭\n"
        "★────────☭────────★\n\n"
        f"• **تم {action} {perm_name} لـ {rank_name}** {status_icon}\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )
    await event.edit(res)
