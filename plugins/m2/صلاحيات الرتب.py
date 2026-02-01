import __main__, os, json, asyncio
from telethon import events

client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# الإعدادات الأساسية
PERMISSIONS_LIST = ["كتم", "طرد", "حظر", "تفاعلي", "كشف", "تاك"]
RANKS = ["مميز", "ادمن", "مدير", "مطور"]

def get_perms_path(chat_id):
    if not os.path.exists(BASE_DIR): return None
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            return os.path.join(BASE_DIR, folder, "permissions.json")
    return None

def load_permissions(path):
    if not os.path.exists(path):
        data = {rank: {p: False for p in PERMISSIONS_LIST} for rank in RANKS}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return data
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ==========================================
# 1. القائمة الرئيسية (.صلاحيات)
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
# 2. عرض صلاحيات رتبة محددة (.صلاحيات مطور)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.صلاحيات (مميز|ادمن|مدير|مطور)$"))
async def show_rank_perms(event):
    path = get_perms_path(event.chat_id)
    rank_name = event.pattern_match.group(1)
    
    # دوامة التحميل (الفورتكس)
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري جلب صلاحيات {rank_name}... 〕 {f} ⌯")
        await asyncio.sleep(0.1)
    
    perms = load_permissions(path)
    
    header = (
        "★────────☭────────★\n"
        f"   ☭ • 𝑷𝑬𝑹𝑴𝑺 {rank_name.upper()} • ☭\n"
        "★────────☭────────★\n\n"
    )
    
    body = f"• 𝑹𝒂𝒏𝒌 ⌯ `{rank_name}`\n"
    body += "━━━━━━━━━━━━━━━━━━━\n"
    for p in PERMISSIONS_LIST:
        status = "✅" if perms[rank_name].get(p) else "❌"
        body += f"• {p} ⌯ {status}\n"
    
    footer = (
        "━━━━━━━━━━━━━━━━━━━\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯\n"
        f"💡 للتحكم: `.تفعيل [الصلاحية] {rank_name}`"
    )
    
    await event.edit(header + body + footer)

# ==========================================
# 3. أمر التفعيل والتعطيل مع الدوامة
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(تفعيل|تعطيل) (.*) (مميز|ادمن|مدير|مطور)$"))
async def toggle_perms(event):
    action = event.pattern_match.group(1)
    perm_name = event.pattern_match.group(2).strip()
    rank_name = event.pattern_match.group(3)
    
    path = get_perms_path(event.chat_id)
    if not path: return
    
    perms = load_permissions(path)
    if perm_name not in PERMISSIONS_LIST:
        return await event.edit(f"⚠️ **الصلاحية `{perm_name}` غير موجودة!**")

    # دوامة التحديث
    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري {action} {perm_name}... 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    perms[rank_name][perm_name] = True if action == "تفعيل" else False
    
    with open(path, "w", encoding="utf-8") as f:
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
