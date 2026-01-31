import __main__, os, asyncio, json, re
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
BASE_DIR = "group"
VORTEX = ["◜", "◝", "◞", "◟"]

# --- دالات المساعدة ---
def get_paths(chat_id):
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            gp = os.path.join(BASE_DIR, folder)
            return gp, os.path.join(gp, "ban.json"), os.path.join(gp, "owner.json")
    return None, None, None

def is_owner(chat_id, sender_id):
    _, _, owner_path = get_paths(chat_id)
    if owner_path and os.path.exists(owner_path):
        with open(owner_path, "r", encoding="utf-8") as f:
            return json.load(f).get("id") == sender_id
    return False

# ==========================================
# 10. أمر الغاء الحظر (رد / آيدي / يوزر)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.الغاء حظر(?:\s+(.*))?$"))
async def unban_user(event):
    if not event.is_group: return
    if not is_owner(event.chat_id, event.sender_id): return 

    input_str = event.pattern_match.group(1)
    user_id = None

    # 1. تحديد المستخدم (رد أو آيدي أو يوزر)
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        user_id = reply_msg.sender_id
    elif input_str:
        if input_str.isdigit():
            user_id = int(input_str)
        else:
            try:
                user_entity = await client.get_entity(input_str)
                user_id = user_entity.id
            except:
                return await event.edit("⚠️ **لم أستطع العثور على هذا المستخدم!**")
    else:
        return await event.edit("⚠️ **رد على الشخص أو أرسل آيديه/يوزره لفك الحظر!**")

    await event.edit("⌯ 〔 جاري مراجعة سجلات العفو... 〕 ⌯")

    try:
        gp_path, ban_file, _ = get_paths(event.chat_id)
        
        # حركات الدوامة (VORTEX)
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري مسح القيود وإصدار العفو 〕 {f} ⌯")
            await asyncio.sleep(0.1)

        # 1. فك الحظر رسمياً في تليجرام
        await client(functions.channels.EditBannedRequest(
            event.chat_id, user_id, 
            types.ChatBannedRights(until_date=None, view_messages=False)
        ))

        # 2. حذفه من ملف ban.json (الرادار التلقائي)
        if ban_file and os.path.exists(ban_file):
            with open(ban_file, "r", encoding="utf-8") as f:
                ban_list = json.load(f)
            
            if user_id in ban_list:
                ban_list.remove(user_id)
                with open(ban_file, "w", encoding="utf-8") as f:
                    json.dump(ban_list, f)

        # جلب الاسم للجمالية
        user = await client.get_entity(user_id)
        name = user.first_name if user.first_name else "المستخدم"

        final_text = (
            "★────────☭────────★\n"
            "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
            f"• 𝑰𝒅 ⌯ `{user_id}`\n"
            "• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **تم فك الحظر والسماح بالدخول** ✅\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
        )
        await event.edit(final_text)

    except Exception as e:
        await event.edit(f"⚠️ **فشل الغاء الحظر:** `{str(e)}`")
