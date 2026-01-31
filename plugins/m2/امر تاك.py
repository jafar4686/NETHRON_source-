import __main__, os, asyncio
from telethon import events, functions, types

# استخراج الكلاينت بنفس طريقتك الأصلية
client = getattr(__main__, 'client', None)
BASE_DIR = "group"

# دالة التأكد من المالك (نفس اللي تستخدمها بالكشف)
def get_owner_only(chat_id):
    if not os.path.exists(BASE_DIR): return None
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            owner_path = os.path.join(BASE_DIR, folder, "owner.json")
            if os.path.exists(owner_path):
                import json
                with open(owner_path, "r", encoding="utf-8") as f:
                    return json.load(f).get("id")
    return None

# ==========================================
# 6. أمر التاك الجماعي (.تاك مجموعة)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تاك مجموعة$"))
async def tag_all_members(event):
    if not event.is_group: return
    
    # 1. التحقق أن المستخدم هو المالك المفعل للمجموعة
    owner_id = get_owner_only(event.chat_id)
    if not owner_id or event.sender_id != owner_id:
        return # لا يستجيب إذا لم يكن المالك

    await event.edit("⌯ 〔 جاري جمع سكان المملكة لبدء التاك.. 〕 ⌯")
    
    try:
        # جلب الأعضاء (باستثناء البوتات والحسابات المحذوفة)
        all_users = await client.get_participants(event.chat_id)
        members = [u for u in all_users if not u.bot and not u.deleted]
        
        if not members:
            return await event.edit("⚠️ **المملكة خالية من الأعضاء!**")
        
        await event.delete() # حذف رسالة التحضير
        
        # تقسيم الأعضاء: كل 10 أشخاص برسالة واحدة (لأمان الحساب)
        chunk_size = 10 
        for i in range(0, len(members), chunk_size):
            chunk = members[i:i + chunk_size]
            
            # كليشة التاك بتنسيق سورس عراق ثون
            tag_text = "☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 𝑇𝐴𝐺 • ☭\n★────────☭────────★\n"
            for user in chunk:
                name = user.first_name if user.first_name else "Member"
                # التاك بالآيدي لضمان وصول الإشعار 100%
                tag_text += f"• ⌯ 〔 [{name}](tg://user?id={user.id}) 〕\n"
            
            tag_text += "★────────☭────────★"
            
            # إرسال الدفعة
            await client.send_message(event.chat_id, tag_text)
            
            # انتظار 2 ثانية بين رسالة ورسالة لتجنب الحظر (Flood)
            await asyncio.sleep(2)
            
        await client.send_message(event.chat_id, "• ⌯ **اكتمل نداء جميع أعضاء المملكة!** ✔")

    except Exception as e:
        await client.send_message(event.chat_id, f"⚠️ **حدث خطأ أثناء التاك:**\n`{str(e)}`")
