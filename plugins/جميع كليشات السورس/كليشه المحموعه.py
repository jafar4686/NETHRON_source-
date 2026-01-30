import __main__, asyncio, json, os
from telethon import events, functions, types
from datetime import datetime

# استخراج الكلاينت
client = getattr(__main__, 'client', None)

# الثوابت والتنسيقات
VORTEX = ["◜", "◝", "◞", "◟"]
BASE_DIR = "group"

if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# --- دالة جلب المسارات المنظمة لكل حساب ومجموعة ---
async def get_paths(chat_id):
    me = await client.get_me()
    # الهيكلية: group / chat_ID / owner_ID /
    group_folder = os.path.join(BASE_DIR, f"chat_{chat_id}")
    owner_folder = os.path.join(group_folder, f"owner_{me.id}")
    
    if not os.path.exists(owner_folder):
        os.makedirs(owner_folder)
    
    return {
        "owner": os.path.join(owner_folder, "owner_info.json"),
        "settings": os.path.join(owner_folder, "settings.json"),
        "members": os.path.join(owner_folder, "members.json")
    }

# --- فلتر المالك الصارم ---
async def is_owner(event):
    me = await client.get_me()
    return event.out and event.sender_id == me.id

# ==========================================
# 1. قائمة المنيو .م2
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م2$"))
async def menu2(event):
    if not await is_owner(event): return
    text = (
        "★────────☭────────★\n"
        "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
        "                  ☭ • سورس عراق ثون • ☭\n"
        "★────────☭────────★\n\n"
        "🛡 **أوامر المجموعات المنظمة:**\n\n"
        "• `.تفعيل مجموعه` ➥ إنشاء المجلدات والملفات\n"
        "• `.كتم` ➥ كتم الشخص وحفظه بالملف (بالرد)\n"
        "• `.فك كتم` ➥ حذف الشخص من ملف الكتم (بالرد)\n"
        "• `.تفاعلي` ➥ عرض معلوماتك من ملف المالك\n"
        "• `.كشف` ➥ عرض ملف الشخص وصورته\n\n"
        "★────────☭────────★\n"
        "💬 ملاحظة: النظام يعمل بنظام الملفات المعزولة."
    )
    await event.edit(text)

# ==========================================
# 2. الأوامر الأساسية (تفعيل، كتم، فك)
# ==========================================

@client.on(events.NewMessage(outgoing=True))
async def main_commands(event):
    if not await is_owner(event) or not event.is_group: return
    
    cmd = event.raw_text
    cid = event.chat_id
    paths = await get_paths(cid)

    # --- أمر التفعيل ---
    if cmd == ".تفعيل مجموعه":
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري تهيئة المملكة 〕 {f} ⌯")
            await asyncio.sleep(0.1)
        
        me = await client.get_me()
        p = await client.get_permissions(cid, me.id)
        rank = "مالك الكروب" if p.is_creator else "مشرف" if p.is_admin else "عضو"

        # حفظ ملف المالك
        owner_data = {
            "name": me.first_name,
            "rank": rank,
            "id": me.id,
            "user": f"@{me.username}" if me.username else "None",
            "status": "اونلاين"
        }
        with open(paths["owner"], "w") as f: json.dump(owner_data, f, indent=4)

        # حفظ ملف الإعدادات
        with open(paths["settings"], "w") as f:
            json.dump({"active": True, "date": str(datetime.now())}, f, indent=4)

        # حفظ ملف الأعضاء
        if not os.path.exists(paths["members"]):
            with open(paths["members"], "w") as f:
                json.dump({"muted": [], "stats": {}}, f, indent=4)

        await event.edit(f"⌯ {VORTEX[0]} 〔 تم التفعيل وإنشاء ملفاتك بنجاح 〕 {VORTEX[0]} ⌯")
        await asyncio.sleep(10); await event.delete()

    # --- أمر الكتم ---
    elif cmd == ".كتم" and event.is_reply:
        if not os.path.exists(paths["members"]): return await event.edit("⚠️ فعل المجموعة أولاً")
        reply = await event.get_reply_message()
        uid = reply.sender_id
        if uid == (await client.get_me()).id: return await event.edit("⚠️ لا يمكنك كتم نفسك")

        with open(paths["members"], "r") as f: m_data = json.load(f)
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري كتم الشخص 〕 {f} ⌯"); await asyncio.sleep(0.1)
        
        if uid not in m_data["muted"]:
            m_data["muted"].append(uid)
            with open(paths["members"], "w") as f: json.dump(m_data, f, indent=4)
        await event.edit(f"⌯ {VORTEX[0]} 〔 تم كتم الشخص وحفظه بالملف 〕 {VORTEX[0]} ⌯")

    # --- أمر فك الكتم ---
    elif cmd == ".فك كتم" and event.is_reply:
        if not os.path.exists(paths["members"]): return
        reply = await event.get_reply_message()
        uid = reply.sender_id
        
        with open(paths["members"], "r") as f: m_data = json.load(f)
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري فتح الكتم 〕 {f} ⌯"); await asyncio.sleep(0.1)
        
        if uid in m_data.get("muted", []):
            m_data["muted"].remove(uid)
            with open(paths["members"], "w") as f: json.dump(m_data, f, indent=4)
        await event.edit(f"⌯ {VORTEX[0]} 〔 تم فك كتم الشخص من الملف 〕 {VORTEX[0]} ⌯")

# ==========================================
# 3. الأوامر التفاعلية (تفاعلي، كشف)
# ==========================================

    elif cmd == ".تفاعلي":
        if not os.path.exists(paths["owner"]): return
        with open(paths["owner"], "r") as f: o = json.load(f)
        with open(paths["members"], "r") as f: m = json.load(f)
        count = m.get("stats", {}).get(str(o["id"]), 0)

        text = (
            "★────────☭────────★\n"
            "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {o['name']}\n"
            f"• 𝑹𝒂𝒏𝒌 ⌯ {o['rank']}\n"
            f"• 𝑰𝒅 ⌯ `{o['id']}`\n"
            f"• 𝑼𝒔𝒆𝒓 ⌯ {o['user']}\n"
            f"• 𝑴𝒂𝒔𝒔𝒆𝒈𝒆 ⌯ {count}\n"
            f"• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ {o['status']}\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )
        await event.edit(text, link_preview=False)

    elif cmd == ".كشف" and event.is_reply:
        if not os.path.exists(paths["members"]): return
        reply = await event.get_reply_message()
        user = await client.get_entity(reply.sender_id)
        full = await client(functions.users.GetFullUserRequest(user.id))
        
        with open(paths["members"], "r") as f: m = json.load(f)
        count = m.get("stats", {}).get(str(user.id), 0)
        p = await client.get_permissions(cid, user.id)
        rank = "مالك الكروب" if p.is_creator else "مشرف" if p.is_admin else "عضو"
        status = "مكتوم 🔇" if user.id in m["muted"] else "غير مكتوم ✅"

        text = (
            "★────────☭────────★\n"
            "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {user.first_name}\n"
            f"• 𝑼𝒔𝒆𝒓 ⌯ @{user.username or 'None'}\n"
            f"• 𝑩𝒊𝒐 ⌯ {full.full_user.about or 'لا يوجد'}\n"
            f"• 𝑴𝒂𝒔𝒔𝒆𝒈𝒆 ⌯ {count}\n"
            f"• 𝑹𝒂𝒏𝒌 ⌯ {rank}\n"
            f"• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ {status}\n"
            f"• 𝑰𝒅 ⌯ `{user.id}`\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )
        photo = await client.download_profile_photo(user.id)
        await client.send_file(cid, photo, caption=text, link_preview=False)
        await event.delete()

# ==========================================
# 4. المحرك الرئيسي (حذف المكتومين + العداد)
# ==========================================
@client.on(events.NewMessage())
async def core_engine(event):
    if not event.is_group: return
    me = await client.get_me()
    group_path = os.path.join(BASE_DIR, f"chat_{event.chat_id}", f"owner_{me.id}")
    members_file = os.path.join(group_path, "members.json")

    if not os.path.exists(members_file): return

    try:
        with open(members_file, "r") as f: m_data = json.load(f)
        uid = str(event.sender_id)
        
        # تحديث عداد الرسائل في الملف
        m_data["stats"][uid] = m_data["stats"].get(uid, 0) + 1
        with open(members_file, "w") as f: json.dump(m_data, f)

        # حذف المكتومين بناءً على ملف المجموعة
        if event.sender_id in m_data.get("muted", []):
            await event.delete()
    except: pass
