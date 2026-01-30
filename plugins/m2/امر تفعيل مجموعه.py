import __main__, asyncio, json, os
from telethon import events, functions, types
from datetime import datetime

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]
BASE_DIR = "group"

if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# --- دالة استخراج المسارات الذكية ---
def get_group_paths(chat_id, title=None):
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            group_path = os.path.join(BASE_DIR, folder)
            return {
                "path": group_path,
                "owner": os.path.join(group_path, "owner.json"),
                "admins": os.path.join(group_path, "admins.txt"),
                "members": os.path.join(group_path, "all_members.txt"),
                "stats": os.path.join(group_path, "stats.json")
            }
    
    if title:
        safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '_')]).strip()
        folder_name = f"{safe_title}_{chat_id}"
        group_path = os.path.join(BASE_DIR, folder_name)
        if not os.path.exists(group_path):
            os.makedirs(group_path)
        return get_group_paths(chat_id)
    return None

# --- دالة تحديث ملفات الأعضاء والرسائل ---
async def refresh_all_data(chat_id, paths):
    admins_list = []
    members_list = []
    # لتحويل الـ stats من JSON إلى قائمة نصية للمشاهدة (اختياري)
    stats_display = []
    
    # جلب الإحصائيات الحالية من الملف
    stats_data = {}
    if os.path.exists(paths["stats"]):
        with open(paths["stats"], "r", encoding="utf-8") as f:
            stats_data = json.load(f)

    async for user in client.iter_participants(chat_id):
        try:
            u_p = await client.get_permissions(chat_id, user.id)
            rank = "المنشئ" if u_p.is_creator else "مشرف" if u_p.is_admin else "عضو"
            u_name = user.first_name or "بدون اسم"
            
            # 1. قائمة الرتب
            line = f"{u_name} | {rank}"
            members_list.append(line)
            if u_p.is_admin or u_p.is_creator:
                admins_list.append(line)
            
            # 2. تحضير الإحصائيات (إذا كان الشخص مسجل بالرسائل)
            msg_count = stats_data.get(str(user.id), {}).get("count", 0)
            stats_display.append(f"{u_name} | {msg_count}")
            
        except: continue
    
    with open(paths["admins"], "w", encoding="utf-8") as f:
        f.write("\n".join(admins_list))
    with open(paths["members"], "w", encoding="utf-8") as f:
        f.write("\n".join(members_list))
        
    return len(members_list)

# ==========================================
# 1. أمر التفعيل (للمنشئ فقط)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل مجموعه$"))
async def enable_group(event):
    if not event.is_group: return
    p = await client.get_permissions(event.chat_id, event.sender_id)
    if not p.is_creator:
        return await event.edit("⚠️ **عذراً، هذا الأمر مخصص لمنشئ المجموعة فقط!**")

    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري تفعيل مجموعتك 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    me = await client.get_me()
    full_user = await client(functions.users.GetFullUserRequest(me.id))
    chat = await event.get_chat()
    paths = get_group_paths(event.chat_id, chat.title)
    
    # إنشاء ملف stats.json فارغ إذا لم يوجد
    if not os.path.exists(paths["stats"]):
        with open(paths["stats"], "w", encoding="utf-8") as f:
            json.dump({}, f)

    owner_info = {"name": me.first_name, "id": me.id, "rank": "المالك الأساسي", "user": "@NETH_RON", "bio": full_user.full_user.about or "لا يوجد"}
    with open(paths["owner"], "w", encoding="utf-8") as f:
        json.dump(owner_info, f, indent=4, ensure_ascii=False)

    num = await refresh_all_data(event.chat_id, paths)
    
    final_text = (
        "★────────☭────────★\n"
        "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
        "★────────☭────────★\n\n"
        "• ⌯ 𝑫𝒐𝒏𝒆 𝑨𝒄𝒕𝒊𝒗𝒆 𝑮𝒓𝒐𝒖𝒑 ✔\n"
        f"• 𝑵𝒂𝒎𝒆 ⌯ {chat.title}\n"
        f"• 𝑶𝒘𝒏𝒆𝒓 ⌯ {me.first_name}\n"
        f"• 𝑵𝒖𝒎𝒃𝒆𝒓 𝑴𝒆𝒎𝒃𝒆𝒓𝒔 ⌯ {num}\n\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
    )
    await event.edit(final_text, link_preview=False)

# ==========================================
# 2. محرك عداد الرسائل وتحديث البيانات تلقائياً
# ==========================================
@client.on(events.NewMessage())
async def message_and_rank_sync(event):
    if not event.is_group or event.edit_date: return
    
    paths = get_group_paths(event.chat_id)
    if not paths or not os.path.exists(paths["owner"]): return

    try:
        user = await event.get_sender()
        if not user or isinstance(user, types.Chat): return
        
        u_id = str(user.id)
        u_name = user.first_name or "بدون اسم"

        # --- أولاً: تحديث عداد الرسائل في stats.json ---
        stats_data = {}
        if os.path.exists(paths["stats"]):
            with open(paths["stats"], "r", encoding="utf-8") as f:
                stats_data = json.load(f)
        
        if u_id not in stats_data:
            stats_data[u_id] = {"name": u_name, "count": 1}
        else:
            stats_data[u_id]["count"] += 1
            stats_data[u_id]["name"] = u_name # تحديث الاسم لو تغير

        with open(paths["stats"], "w", encoding="utf-8") as f:
            json.dump(stats_data, f, indent=4, ensure_ascii=False)

        # --- ثانياً: التأكد من الرتبة في all_members.txt ---
        with open(paths["members"], "r", encoding="utf-8") as f:
            content = f.read()
        
        u_p = await client.get_permissions(event.chat_id, user.id)
        rank = "المنشئ" if u_p.is_creator else "مشرف" if u_p.is_admin else "عضو"
        entry = f"{u_name} | {rank}"

        if entry not in content:
            await refresh_all_data(event.chat_id, paths)
            
    except: pass

@client.on(events.ChatAction())
async def action_sync(event):
    if event.is_group and (event.new_admins or event.new_privileges or event.user_joined or event.user_left):
        paths = get_group_paths(event.chat_id)
        if paths and os.path.exists(paths["owner"]):
            await refresh_all_data(event.chat_id, paths)

# ==========================================
# 3. قائمة المنيو
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م2$"))
async def menu2(event):
    paths = get_group_paths(event.chat_id)
    if not paths or not os.path.exists(paths["owner"]): return
    with open(paths["owner"], "r", encoding="utf-8") as f:
        o = json.load(f)
    if event.sender_id != o["id"]: return 

    text = (
        "★────────☭────────★\n"
        "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
        "★────────☭────────★\n\n"
        f"• 𝑾𝒆𝒍𝒄𝒐𝒎𝒆 ⌯ {o['name']}\n\n"
        "🛡 **أوامر الملفات والرسائل:**\n"
        "• `.تفعيل مجموعه` ➥ أرشفة شاملة وفتح العداد\n"
        "• ملف `stats.json` يسجل كل رسالة الآن 📊\n\n"
        "★────────☭────────★"
    )
    await event.edit(text)
