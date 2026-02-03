import __main__, os, json, asyncio
from telethon import events

client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# تعريف الرتب حسب القوة (من الأضعف للأقوى)
RANK_HIERARCHY = {"مميز": 1, "ادمن": 2, "مدير": 3, "مطور": 4, "owner": 5}

# توزيع الصلاحيات الافتراضي حسب طلبك
DEFAULT_PERMS = {
    "مميز": ["تفاعلي"],
    "ادمن": ["كتم", "كشف", "تفاعلي"],
    "مدير": ["طرد", "كتم", "تفاعلي", "كشف"],
    "مطور": ["كتم", "حظر", "تفاعلي", "كشف", "طرد"]
}

PERMISSIONS_LIST = ["كتم", "طرد", "حظر", "تفاعلي", "كشف", "تاك"]
RANKS = ["مميز", "ادمن", "مدير", "مطور"]

def get_paths(chat_id):
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return os.path.join(gp, "permissions.json"), os.path.join(gp, "member_rank.json"), os.path.join(gp, "owner.json")
    return None, None, None

def load_permissions(path):
    if not os.path.exists(path):
        data = {rank: {p: (p in DEFAULT_PERMS[rank]) for p in PERMISSIONS_LIST} for rank in RANKS}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return data
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# --- دالة فحص الهرمية (الرتبة ضد الرتبة) ---
async def check_hierarchy(event, target_id):
    path_perms, path_ranks, path_owner = get_paths(event.chat_id)
    if not path_ranks: return True # مسموح إذا ماكو بيانات
    
    # 1. جلب رتبة المنفذ
    sender_rank = "مميز"
    with open(path_owner, "r") as f: 
        if json.load(f).get("id") == event.sender_id: sender_rank = "owner"
    
    if sender_rank != "owner":
        with open(path_ranks, "r") as f:
            ranks = json.load(f)
            sender_rank = ranks.get(str(event.sender_id), {}).get("rank", "مميز")

    # 2. جلب رتبة الهدف
    target_rank = "مميز"
    with open(path_owner, "r") as f:
        if json.load(f).get("id") == target_id: target_rank = "owner"
    
    if target_rank != "owner":
        with open(path_ranks, "r") as f:
            ranks = json.load(f)
            target_rank = ranks.get(str(target_id), {}).get("rank", "مميز")

    # المقارنة
    if RANK_HIERARCHY[sender_rank] <= RANK_HIERARCHY[target_rank] and sender_rank != "owner":
        warn = await event.edit(f"⚠️ **عذراً، لا يمكنك تنفيذ هذا الأمر على رتبة {target_rank} (أعلى منك أو مساوية لك)!**")
        await asyncio.sleep(10)
        await warn.delete()
        return False
    return True

# ==========================================
# 1. عرض الصلاحيات (مع الالتزام بالتوزيع الجديد)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.صلاحيات (مميز|ادمن|مدير|مطور)$"))
async def show_rank_perms(event):
    path_perms, _, _ = get_paths(event.chat_id)
    rank_name = event.pattern_match.group(1)
    
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري جلب صلاحيات {rank_name}... 〕 {f} ⌯")
        await asyncio.sleep(0.1)
    
    perms = load_permissions(path_perms)
    header = "★────────☭────────★\n" + f"   ☭ • 𝑷𝑬𝑹𝑴𝑺 {rank_name.upper()} • ☭\n" + "★────────☭────────★\n\n"
    body = f"• 𝑹𝒂𝒏𝒌 ⌯ `{rank_name}`\n━━━━━━━━━━━━━━━━━━━\n"
    
    # فلترة العرض حسب المسموح لكل رتبة في النظام الهرمي
    for p in PERMISSIONS_LIST:
        if p not in DEFAULT_PERMS[rank_name] and rank_name != "مطور":
            continue
        status = "✅" if perms.get(rank_name, {}).get(p) else "❌"
        body += f"• {p} ⌯ {status}\n"
    
    footer = "━━━━━━━━━━━━━━━━━━━\n• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    await event.edit(header + body + footer)

# ==========================================
# 2. مثال لكيفية استخدام الحماية (في الكتم مثلاً)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كتم$"))
async def mute_cmd(event):
    if not event.is_reply: return
    reply = await event.get_reply_message()
    
    # فحص الهرمية قبل التنفيذ
    if not await check_hierarchy(event, reply.sender_id):
        return # يتوقف التنفيذ ويمسح الرسالة بعد 10 ثواني كما في الدالة

    # إذا عبر الفحص، يكمل الكود طبيعي...
    await event.edit("✅ **تم الكتم بنجاح (رتبتك تسمح بذلك).**")

# ==========================================
# 3. أمر التفعيل/التعطيل
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(تفعيل|تعطيل) (.*) (مميز|ادمن|مدير|مطور)$"))
async def toggle_perms(event):
    action = event.pattern_match.group(1)
    perm_name = event.pattern_match.group(2).strip()
    rank_name = event.pattern_match.group(3)
    
    # منع تفعيل صلاحيات خارج النطاق المسموح للرتبة
    if perm_name not in DEFAULT_PERMS[rank_name] and rank_name != "مطور":
        return await event.edit(f"⚠️ **رتبة {rank_name} لا تدعم صلاحية {perm_name} أصلاً!**")

    path_perms, _, _ = get_paths(event.chat_id)
    perms = load_permissions(path_perms)
    
    perms[rank_name][perm_name] = (action == "تفعيل")
    with open(path_perms, "w", encoding="utf-8") as f:
        json.dump(perms, f, indent=4, ensure_ascii=False)
    
    await event.edit(f"⚙️ **تم {action} {perm_name} لـ {rank_name} بنجاح ✅**")
