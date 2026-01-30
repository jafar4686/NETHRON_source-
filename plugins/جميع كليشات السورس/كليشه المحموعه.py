import __main__, asyncio, json, os
from telethon import events, functions, types

client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]
BASE_DIR = "group"

# --- دالة استخراج المسارات المنظمة ---
def get_paths(chat_id):
    # مسار المجلد: group/اسم_الكروب_ID
    group_folder = os.path.join(BASE_DIR, f"group_{chat_id}")
    return {
        "folder": group_folder,
        "owner": os.path.join(group_folder, "owner.json"),
        "settings": os.path.join(group_folder, "settings.json"),
        "members": os.path.join(group_folder, "members.json"),
        "mutes": os.path.join(group_folder, "mutes.json")
    }

# --- فلتر التحقق الصارم من المالك عبر الملف ---
async def verify_owner(event):
    if not event.out: return False
    paths = get_paths(event.chat_id)
    if not os.path.exists(paths["owner"]): return False
    
    try:
        with open(paths["owner"], "r") as f:
            data = json.load(f)
            return event.sender_id == data.get("id")
    except: return False

# ==========================================
# 1. أمر التفعيل (البوابة الوحيدة للتشغيل)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل مجموعه$"))
async def enable_group(event):
    if not event.is_group: return
    cid = event.chat_id
    paths = get_paths(cid)
    
    if not os.path.exists(paths["folder"]):
        os.makedirs(paths["folder"])

    for f in VORTEX:
        await event.edit(f"⌯ {f} 〔 جاري إنشاء قاعدة بيانات الكروب 〕 {f} ⌯")
        await asyncio.sleep(0.1)

    me = await client.get_me()
    p = await client.get_permissions(cid, me.id)
    rank = "مالك" if p.is_creator else "مشرف" if p.is_admin else "عضو"

    # ملف المالك (القفل)
    with open(paths["owner"], "w") as f:
        json.dump({
            "name": me.first_name,
            "id": me.id,
            "user": f"@{me.username}" if me.username else "None",
            "rank": rank
        }, f, indent=4)

    # ملفات الإعدادات والمكتومين والأعضاء
    with open(paths["settings"], "w") as f: json.dump({"active": True}, f)
    with open(paths["mutes"], "w") as f: json.dump([], f)
    with open(paths["members"], "w") as f: json.dump({}, f)

    await event.edit(f"⌯ {VORTEX[0]} 〔 تم التفعيل وحصر الأوامر بآيديك 〕 {VORTEX[0]} ⌯")
    await asyncio.sleep(5); await event.delete()

# ==========================================
# 2. معالج الأوامر (لا يستجيب إلا للمالك المسجل بالملف)
# ==========================================
@client.on(events.NewMessage(outgoing=True))
async def group_commands(event):
    if not event.is_group: return
    cmd = event.raw_text
    cid = event.chat_id
    paths = get_paths(cid)

    # التحقق: هل المجموعة مفعلة وهل أنت المالك المسجل بالملف؟
    if not await verify_owner(event):
        return 

    # --- أمر الكتم ---
    if cmd == ".كتم" and event.is_reply:
        reply = await event.get_reply_message()
        uid = reply.sender_id
        with open(paths["mutes"], "r") as f: mutes = json.load(f)
        
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري كتم الشخص 〕 {f} ⌯")
            await asyncio.sleep(0.1)
            
        if uid not in mutes:
            mutes.append(uid)
            with open(paths["mutes"], "w") as f: json.dump(mutes, f)
        await event.edit(f"⌯ {VORTEX[0]} 〔 تم الكتم بنجاح 〕 {VORTEX[0]} ⌯")

    # --- أمر فك الكتم ---
    elif cmd == ".فك كتم" and event.is_reply:
        reply = await event.get_reply_message()
        uid = reply.sender_id
        with open(paths["mutes"], "r") as f: mutes = json.load(f)
        
        if uid in mutes:
            mutes.remove(uid)
            with open(paths["mutes"], "w") as f: json.dump(mutes, f)
        await event.edit(f"⌯ {VORTEX[0]} 〔 تم فك الكتم بنجاح 〕 {VORTEX[0]} ⌯")

    # --- أمر تفاعلي (يجلب الرتبة من الملف) ---
    elif cmd == ".تفاعلي":
        with open(paths["owner"], "r") as f: o = json.load(f)
        with open(paths["members"], "r") as f: members = json.load(f)
        msgs = members.get(str(o["id"]), 0)
        
        text = (
            "★────────☭────────★\n"
            "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {o['name']}\n"
            f"• 𝑹𝒂𝒏𝒌 ⌯ {o['rank']}\n"
            f"• 𝑰𝒅 ⌯ `{o['id']}`\n"
            f"• 𝑴𝒂𝒔𝒔𝒆𝒈𝒆 ⌯ {msgs}\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )
        await event.edit(text, link_preview=False)

# ==========================================
# 3. المحرك (حذف المكتومين وتحديث عداد الأعضاء)
# ==========================================
@client.on(events.NewMessage())
async def core_engine(event):
    if not event.is_group: return
    paths = get_paths(event.chat_id)
    
    if not os.path.exists(paths["mutes"]): return

    try:
        # 1. تحديث العداد في ملف الأعضاء
        with open(paths["members"], "r") as f: members = json.load(f)
        uid = str(event.sender_id)
        members[uid] = members.get(uid, 0) + 1
        with open(paths["members"], "w") as f: json.dump(members, f)

        # 2. حذف المكتومين
        with open(paths["mutes"], "r") as f: mutes = json.load(f)
        if event.sender_id in mutes:
            await event.delete()
    except: pass
