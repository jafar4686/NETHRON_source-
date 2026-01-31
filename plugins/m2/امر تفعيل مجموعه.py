import __main__, asyncio, json, os
from telethon import events, functions, types

# استخراج الكلاينت من الملف الرئيسي
client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]
BASE_DIR = "group"
processed_msgs = set() # لمنع تكرار الحساب 100%

# إنشاء المجلد الرئيسي
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# --- 1. دالة إدارة المسارات ---
def get_group_paths(chat_id, title=None):
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return {
                "path": gp,
                "stats": os.path.join(gp, "stats.json"),
                "owner": os.path.join(gp, "owner.json"),
                "mute": os.path.join(gp, "mute.json"),
                "admins": os.path.join(gp, "admins.txt"),
                "members": os.path.join(gp, "all_members.txt")
            }
    if title:
        safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '_')]).strip()
        folder_name = f"{safe_title}_{chat_id}"
        gp = os.path.join(BASE_DIR, folder_name)
        if not os.path.exists(gp): os.makedirs(gp)
        return get_group_paths(chat_id)
    return None

# --- 2. دالة أرشفة البيانات (أعضاء + رتب) ---
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
# 3. أمر التفعيل بالكليشة المطلوبة
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل مجموعه$"))
async def enable_group(event):
    if not event.is_group: return
    p = await client.get_permissions(event.chat_id, event.sender_id)
    if not p.is_creator: return await event.edit("⚠️ **هذا الأمر للمنشئ فقط!**")

    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري تهيئة سجلات المملكة 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    me = await client.get_me()
    chat = await event.get_chat()
    paths = get_group_paths(event.chat_id, chat.title)
    
    if not os.path.exists(paths["stats"]):
        with open(paths["stats"], "w", encoding="utf-8") as f: json.dump({}, f)
    if not os.path.exists(paths["mute"]):
        with open(paths["mute"], "w", encoding="utf-8") as f: json.dump([], f)

    owner_info = {"name": me.first_name, "id": me.id, "rank": "المالك", "user": f"@{me.username}"}
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
# 4. محرك العداد (تعديل 100% - اسم | عدد)
# ==========================================
@client.on(events.NewMessage(incoming=True))
async def live_stats_engine(event):
    # نفلتر: لازم كروب، مو تعديل، ومو بوت
    if not event.is_group or event.edit_date or not event.sender_id:
        return

    # أهم قفل: يتجاهل رسائل السورس نفسه لضمان عدم الزيادة 2
    me = await client.get_me()
    if event.sender_id == me.id:
        return

    # قفل البصمة لمنع تكرار نفس الرسالة
    msg_key = f"{event.chat_id}_{event.id}"
    if msg_key in processed_msgs:
        return
    processed_msgs.add(msg_key)
    
    if len(processed_msgs) > 500:
        processed_msgs.clear()

    paths = get_group_paths(event.chat_id)
    if not paths or not os.path.exists(paths["stats"]):
        return

    try:
        u_id = str(event.sender_id)
        
        with open(paths["stats"], "r", encoding="utf-8") as f:
            try: stats_data = json.load(f)
            except: stats_data = {}
        
        if u_id not in stats_data:
            sender = await event.get_sender()
            u_name = getattr(sender, 'first_name', "بدون اسم")
            # الصيغة المطلوبة في stats.json
            stats_data[u_id] = {
                "name": u_name,
                "count": 1,
                "full_info": f"{u_name} | 1"
            }
        else:
            # زيادة حقيقية 1 فقط لكل رسالة جديدة
            stats_data[u_id]["count"] += 1
            u_name = stats_data[u_id]["name"]
            stats_data[u_id]["full_info"] = f"{u_name} | {stats_data[u_id]['count']}"

        with open(paths["stats"], "w", encoding="utf-8") as f:
            json.dump(stats_data, f, indent=4, ensure_ascii=False)
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
