import __main__, asyncio, json, os
from telethon import events, functions, types

client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]
BASE_DIR = "group"

# --- دالة المسارات لضمان الترتيب داخل المجلد ---
def get_group_paths(chat_id, title):
    safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '_')]).strip()
    folder_name = f"{safe_title}_{chat_id}"
    group_path = os.path.join(BASE_DIR, folder_name)
    
    if not os.path.exists(group_path):
        os.makedirs(group_path)
        
    return {
        "path": group_path,
        "owner": os.path.join(group_path, "owner.json"),
        "admins": os.path.join(group_path, "admins.txt"),
        "members": os.path.join(group_path, "all_members.txt")
    }

# ==========================================
# 1. أمر التفعيل (الإنشاء الأولي)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل مجموعه$"))
async def enable_group(event):
    if not event.is_group: return

    # التحقق من المنشئ
    p = await client.get_permissions(event.chat_id, event.sender_id)
    if not p.is_creator:
        return await event.edit("⚠️ **عذراً، هذا الأمر للمنشئ فقط!**")

    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري تهيئة ملفات مجموعتك 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    me = await client.get_me()
    chat = await event.get_chat()
    paths = get_group_paths(event.chat_id, chat.title)

    # أرشفة الأعضاء والمشرفين فوراً
    admins_list = []
    members_list = []
    
    async for user in client.iter_participants(event.chat_id):
        try:
            u_p = await client.get_permissions(event.chat_id, user.id)
            rank = "المنشئ" if u_p.is_creator else "مشرف" if u_p.is_admin else "عضو"
            line = f"{user.first_name or 'بدون اسم'} | {rank}"
            
            members_list.append(line)
            if u_p.is_admin or u_p.is_creator:
                admins_list.append(line)
        except: continue

    # كتابة الملفات (تأكد من الحفظ)
    with open(paths["owner"], "w", encoding="utf-8") as f:
        json.dump({"name": me.first_name, "id": me.id, "rank": "المالك", "user": "@NETH_RON"}, f, indent=4, ensure_ascii=False)
    
    with open(paths["admins"], "w", encoding="utf-8") as f:
        f.write("\n".join(admins_list))
        
    with open(paths["members"], "w", encoding="utf-8") as f:
        f.write("\n".join(members_list))

    # رسالة النجاح
    final_text = (
        "★────────☭────────★\n"
        "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
        "★────────☭────────★\n\n"
        "• ⌯ 𝑫𝒐𝒏𝒆 𝑨𝒄𝒕𝒊𝒗𝒆 𝑮𝒓𝒐𝒖𝒑 ✔\n"
        f"• 𝑵𝒂𝒎𝒆 ⌯ {chat.title}\n"
        f"• 𝑶𝒘𝒏𝒆𝒓 ⌯ {me.first_name}\n"
        f"• 𝑵𝒖𝒎𝒃𝒆𝒓 𝑴𝒆𝒎𝒃𝒆𝒓𝒔 ⌯ {len(members_list)}\n\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
    )
    await event.edit(final_text, link_preview=False)

# ==========================================
# 2. المحرك الذكي (تحديث تلقائي للملفات)
# ==========================================
@client.on(events.NewMessage())
async def auto_update_members(event):
    if not event.is_group: return
    
    # جلب مسار ملفات هذه المجموعة
    chat = await event.get_chat()
    safe_title = "".join([c for c in chat.title if c.isalnum() or c in (' ', '_')]).strip()
    group_folder = os.path.join(BASE_DIR, f"{safe_title}_{event.chat_id}")
    members_file = os.path.join(group_folder, "all_members.txt")

    # إذا المجموعة مفعلة (الملف موجود)
    if os.path.exists(members_file):
        try:
            user = await event.get_sender()
            u_name = user.first_name or "بدون اسم"
            
            # قراءة الملف للتأكد إذا العضو موجود
            with open(members_file, "r+", encoding="utf-8") as f:
                content = f.read()
                if u_name not in content:
                    # إذا مو موجود، نجيب رتبته ونضيفه
                    u_p = await client.get_permissions(event.chat_id, user.id)
                    rank = "المنشئ" if u_p.is_creator else "مشرف" if u_p.is_admin else "عضو"
                    f.write(f"\n{u_name} | {rank}")
        except: pass
