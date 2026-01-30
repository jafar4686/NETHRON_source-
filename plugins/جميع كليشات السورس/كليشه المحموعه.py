import __main__, asyncio, json, os
from telethon import events, functions, types

client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]
BASE_DIR = "group"

# --- دالة المسارات (تضمن إنشاء كل شيء داخل مجلد المجموعة) ---
def get_paths(chat_id):
    group_folder = os.path.join(BASE_DIR, f"group_{chat_id}")
    if not os.path.exists(group_folder):
        os.makedirs(group_folder)
    return {
        "folder": group_folder,
        "owner": os.path.join(group_folder, "owner.json"),
        "members": os.path.join(group_folder, "members.txt"),
        "mutes": os.path.join(group_folder, "mutes.json"),
        "settings": os.path.join(group_folder, "settings.json")
    }

# --- فلتر التحقق من المالك عبر ملف owner.json ---
async def verify_owner(event):
    if not event.out: return False
    paths = get_paths(event.chat_id)
    if not os.path.exists(paths["owner"]): return False
    try:
        with open(paths["owner"], "r", encoding="utf-8") as f:
            data = json.load(f)
            return event.sender_id == data.get("id")
    except: return False

# ==========================================
# 1. قائمة المنيو .م2
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م2$"))
async def menu2(event):
    if not await verify_owner(event): return
    paths = get_paths(event.chat_id)
    with open(paths["owner"], "r", encoding="utf-8") as f: o = json.load(f)
    
    text = (
        "★────────☭────────★\n"
        "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
        "★────────☭────────★\n\n"
        f"• 𝑾𝒆𝒍𝒄𝒐𝒎𝒆 ⌯ {o['name']}\n"
        f"• 𝑹𝒂𝒏𝒌 ⌯ {o['rank']}\n\n"
        "🛡 **أوامر المجموعة:**\n"
        "• `.تفعيل مجموعه` ➥ أرشفة الأعضاء والقفل\n"
        "• `.كتم` ➥ كتم الشخص (بالرد)\n"
        "• `.فك كتم` ➥ فك الكتم (بالرد)\n"
        "• `.تفاعلي` ➥ عرض ملف المالك\n"
        "• `.كشف` ➥ كشف حساب شخص (بالرد)\n\n"
        "★────────☭────────★"
    )
    await event.edit(text)

# ==========================================
# 2. أمر التفعيل (سحب الأعضاء وإنشاء الهيكل)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل مجموعه$"))
async def enable_group(event):
    if not event.is_group: return
    cid = event.chat_id
    paths = get_paths(cid)

    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري تهيئة ملفات المجموعة 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    me = await client.get_me()
    p = await client.get_permissions(cid, me.id)
    rank = "مالك الكروب" if p.is_creator else "مشرف" if p.is_admin else "عضو"

    # 1. إنشاء ملف المالك داخل مجلد الكروب
    owner_info = {
        "name": me.first_name,
        "user": f"@{me.username}" if me.username else "None",
        "id": me.id,
        "rank": rank
    }
    with open(paths["owner"], "w", encoding="utf-8") as f:
        json.dump(owner_info, f, indent=4, ensure_ascii=False)

    # 2. أرشفة جميع الأعضاء (members.txt)
    await event.edit("⏳ **جاري سحب الأعضاء وتصنيف الرتب...**")
    members_data = []
    async for user in client.iter_participants(cid):
        try:
            u_p = await client.get_permissions(cid, user.id)
            u_rank = "owner" if u_p.is_creator else "admin" if u_p.is_admin else "member"
            members_data.append(f"{user.first_name or 'NoName'} | {u_rank}")
        except: continue

    with open(paths["members"], "w", encoding="utf-8") as f:
        f.write("\n".join(members_data))

    # 3. ملف المكتومين والإعدادات
    with open(paths["mutes"], "w") as f: json.dump([], f)
    with open(paths["settings"], "w") as f: json.dump({"active": True}, f)

    await event.edit(f"⌯ {VORTEX[0]} 〔 تم التفعيل وحصر الأوامر بآيديك 〕 {VORTEX[0]} ⌯")
    await asyncio.sleep(5); await event.delete()

# ==========================================
# 3. الأوامر الرئيسية (كتم، كشف، تفاعلي)
# ==========================================
@client.on(events.NewMessage(outgoing=True))
async def group_actions(event):
    if not event.is_group or not await verify_owner(event): return
    
    cmd = event.raw_text
    paths = get_paths(event.chat_id)

    if cmd == ".كتم" and event.is_reply:
        reply = await event.get_reply_message()
        with open(paths["mutes"], "r") as f: mutes = json.load(f)
        if reply.sender_id not in mutes:
            mutes.append(reply.sender_id)
            with open(paths["mutes"], "w") as f: json.dump(mutes, f)
        await event.edit("⌯〔 تم الكتم وحفظه بمجلد المجموعة 〕⌯")

    elif cmd == ".فك كتم" and event.is_reply:
        reply = await event.get_reply_message()
        with open(paths["mutes"], "r") as f: mutes = json.load(f)
        if reply.sender_id in mutes:
            mutes.remove(reply.sender_id)
            with open(paths["mutes"], "w") as f: json.dump(mutes, f)
        await event.edit("⌯〔 تم فك الكتم من السجلات 〕⌯")

    elif cmd == ".كشف" and event.is_reply:
        reply = await event.get_reply_message()
        user = await client.get_entity(reply.sender_id)
        p = await client.get_permissions(event.chat_id, user.id)
        u_rank = "مالك" if p.is_creator else "مشرف" if p.is_admin else "عضو"
        
        text = (
            "★────────☭────────★\n"
            "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {user.first_name}\n"
            f"• 𝑹𝒂𝒏𝒌 ⌯ {u_rank}\n"
            f"• 𝑰𝒅 ⌯ `{user.id}`\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )
        photo = await client.download_profile_photo(user.id)
        await client.send_file(event.chat_id, photo, caption=text); await event.delete()

# ==========================================
# 4. المحرك (حذف المكتومين وتحديث الأعضاء)
# ==========================================
@client.on(events.NewMessage())
async def handler(event):
    if not event.is_group: return
    paths = get_paths(event.chat_id)
    if not os.path.exists(paths["owner"]): return

    # حذف المكتومين
    try:
        with open(paths["mutes"], "r") as f: mutes = json.load(f)
        if event.sender_id in mutes:
            await event.delete()
    except: pass

    # إضافة الأعضاء الجدد لملف members.txt تلقائياً
    try:
        user = await event.get_sender()
        u_name = user.first_name or "NoName"
        with open(paths["members"], "a+", encoding="utf-8") as f:
            f.seek(0)
            if u_name not in f.read():
                u_p = await client.get_permissions(event.chat_id, user.id)
                u_rank = "owner" if u_p.is_creator else "admin" if u_p.is_admin else "member"
                f.write(f"\n{u_name} | {u_rank}")
    except: pass
