import __main__, asyncio, json, os
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]
BASE_DIR = "group"

# إنشاء المجلد الرئيسي
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# --- 1. دالة جلب المسارات بناءً على آيدي المجموعة ---
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
        if not os.path.exists(group_path): os.makedirs(group_path)
        return get_group_paths(chat_id)
    return None

# --- 2. دالة تحديث الأرشيف (أعضاء + رتب) ---
async def refresh_all_data(chat_id, paths):
    admins_list, members_list = [], []
    async for user in client.iter_participants(chat_id):
        try:
            if user.bot: continue
            u_p = await client.get_permissions(chat_id, user.id)
            rank = "المنشئ" if u_p.is_creator else "مشرف" if u_p.is_admin else "عضو"
            u_name = user.first_name or "بدون اسم"
            line = f"{u_name} | {rank}"
            members_list.append(line)
            if u_p.is_admin or u_p.is_creator: admins_list.append(line)
        except: continue
    with open(paths["admins"], "w", encoding="utf-8") as f: f.write("\n".join(admins_list))
    with open(paths["members"], "w", encoding="utf-8") as f: f.write("\n".join(members_list))
    return len(members_list)

# ==========================================
# 3. أمر التفعيل (للمنشئ فقط)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل مجموعه$"))
async def enable_group(event):
    if not event.is_group: return
    p = await client.get_permissions(event.chat_id, event.sender_id)
    if not p.is_creator: return await event.edit("⚠️ **هذا الأمر للمنشئ فقط!**")

    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري تهيئة ملفات المملكة 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    me = await client.get_me()
    chat = await event.get_chat()
    paths = get_group_paths(event.chat_id, chat.title)
    
    if not os.path.exists(paths["stats"]):
        with open(paths["stats"], "w", encoding="utf-8") as f: json.dump({}, f)

    owner_info = {"name": me.first_name, "id": me.id, "rank": "المالك", "user": "@NETH_RON"}
    with open(paths["owner"], "w", encoding="utf-8") as f:
        json.dump(owner_info, f, indent=4, ensure_ascii=False)

    num = await refresh_all_data(event.chat_id, paths)
    await event.edit(f"★────────☭────────★\n• ⌯ 𝑫𝒐𝒏𝒆 𝑨𝒄𝒕𝒊𝒗𝒆 ✔\n• 𝑵𝒂𝒎𝒆 ⌯ {chat.title}\n• 𝑴𝒆𝒎𝒃𝒆𝒓𝒔 ⌯ {num}\n★────────☭────────★")

# ==========================================
# 4. محرك عداد الرسائل (زيادة 1 فقط بدقة)
# ==========================================
# نستخدم incoming=True لمنع حساب رسائل البوت نفسه، ونتجاهل الرسائل المعدلة
@client.on(events.NewMessage(incoming=True))
async def live_stats_engine(event):
    if not event.is_group or event.edit_date:
        return
    
    # استخراج المسارات
    paths = get_group_paths(event.chat_id)
    if not paths or not os.path.exists(paths["stats"]):
        return

    try:
        sender = await event.get_sender()
        if not sender or sender.bot: return # تجاهل البوتات

        u_id = str(sender.id)
        u_name = sender.first_name or "بدون اسم"

        # فتح وحفظ البيانات مع قفل بسيط لتجنب التكرار
        async with asyncio.Lock():
            with open(paths["stats"], "r+", encoding="utf-8") as f:
                try:
                    stats_data = json.load(f)
                except:
                    stats_data = {}
                
                if u_id not in stats_data:
                    stats_data[u_id] = {"name": u_name, "count": 1}
                else:
                    # الزيادة بمقدار 1 فقط
                    stats_data[u_id]["count"] += 1
                    stats_data[u_id]["name"] = u_name
                
                f.seek(0)
                json.dump(stats_data, f, indent=4, ensure_ascii=False)
                f.truncate()
    except:
        pass

# ==========================================
# 5. مراقب التغيرات (تلقائي)
# ==========================================
@client.on(events.ChatAction())
async def watch_changes(event):
    if event.is_group and (event.new_admins or event.user_joined or event.user_left):
        paths = get_group_paths(event.chat_id)
        if paths and os.path.exists(paths["owner"]):
            await refresh_all_data(event.chat_id, paths)
