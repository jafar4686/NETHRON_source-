import __main__, os, asyncio, json
from telethon import events, functions, types

client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# --- دالة فحص الصلاحية المشتركة (تاك) ---
def get_group_paths(chat_id):
    if not os.path.exists(BASE_DIR): return None
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return {
                "owner": os.path.join(gp, "owner.json"),
                "ranks": os.path.join(gp, "member_rank.json"),
                "perms": os.path.join(gp, "permissions.json")
            }
    return None

async def can_tag(event, paths):
    uid = event.sender_id
    # 1. المالك له الحق دائماً
    if os.path.exists(paths["owner"]):
        with open(paths["owner"], "r", encoding="utf-8") as f:
            if json.load(f).get("id") == uid: return True
            
    # 2. فحص الرتبة والصلاحية (التاك مسموح للمطور فقط حسب هرميتك)
    if os.path.exists(paths["ranks"]):
        with open(paths["ranks"], "r", encoding="utf-8") as f:
            ranks = json.load(f)
            if str(uid) in ranks:
                u_rank = ranks[str(uid)]["rank"]
                # التاك حصراً للمطور كما طلبت في توزيع الرتب
                if u_rank == "مطور":
                    if os.path.exists(paths["perms"]):
                        with open(paths["perms"], "r", encoding="utf-8") as f:
                            perms = json.load(f)
                            return perms.get("مطور", {}).get("تاك", False)
    return False

# ==========================================
# أمر التاك الجماعي المربوط (.تاك مجموعة)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تاك مجموعة$"))
async def tag_all_members(event):
    if not event.is_group: return
    
    paths = get_group_paths(event.chat_id)
    if not paths: return

    # التحقق من الصلاحية (مالك أو مطور مفعل له التاك)
    if not await can_tag(event, paths):
        warn = await event.edit("⚠️ **عذراً، هذا الأمر مخصص للمالك أو المطور (بعد التفعيل) فقط!**")
        await asyncio.sleep(5)
        return await warn.delete()

    await event.edit("⌯ 〔 جاري جمع سكان المملكة لبدء التاك.. 〕 ⌯")
    
    try:
        # جلب الأعضاء
        all_users = await client.get_participants(event.chat_id)
        members = [u for u in all_users if not u.bot and not u.deleted]
        
        if not members:
            return await event.edit("⚠️ **المملكة خالية من الأعضاء!**")
        
        await event.delete() 
        
        chunk_size = 10 
        for i in range(0, len(members), chunk_size):
            chunk = members[i:i + chunk_size]
            
            # كليشة التاك (𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 𝑇𝐴𝐺)
            tag_text = "☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 𝑇𝐴𝐺 • ☭\n"
            tag_text += "★────────☭────────★\n"
            for user in chunk:
                name = user.first_name if user.first_name else "Member"
                tag_text += f"• ⌯ 〔 [{name}](tg://user?id={user.id}) 〕\n"
            
            tag_text += "★────────☭────────★\n"
            tag_text += "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
            
            await client.send_message(event.chat_id, tag_text)
            await asyncio.sleep(2) # تجنب الفلود
            
        await client.send_message(event.chat_id, "• ⌯ **اكتمل نداء جميع أعضاء المملكة!** ✅")

    except Exception as e:
        await client.send_message(event.chat_id, f"⚠️ **حدث خطأ أثناء التاك:**\n`{str(e)}`")
