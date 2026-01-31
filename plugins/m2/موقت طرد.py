import __main__, os, asyncio, json, re, time
from telethon import events, functions, types

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
BASE_DIR = "group"

# دالة تحويل الوقت إلى ثواني
def parse_time(time_str):
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    match = re.match(r"(\d+)([smhd])", time_str.lower())
    if match:
        val, unit = match.groups()
        return int(val) * units[unit]
    return None

# دالة التأكد من المالك
def get_owner_only(chat_id):
    if not os.path.exists(BASE_DIR): return None
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            owner_path = os.path.join(BASE_DIR, folder, "owner.json")
            if os.path.exists(owner_path):
                with open(owner_path, "r", encoding="utf-8") as f:
                    return json.load(f).get("id")
    return None

# ==========================================
# 13. أمر موقت طرد (تحديث ذكي وآمن)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.موقت طرد\s+(.*)$"))
async def timed_kick(event):
    if not event.is_group: return
    owner_id = get_owner_only(event.chat_id)
    if not owner_id or event.sender_id != owner_id: return

    args = event.pattern_match.group(1).split()
    if not args:
        return await event.edit("⚠️ **مثال: .موقت طرد 5m**")

    time_val = args[0]
    seconds = parse_time(time_val)
    
    # --- الشرط: أقل مدة دقيقة واحدة ---
    if not seconds or seconds < 60:
        return await event.edit("⚠️ **ملكنا، أقل مدة للطرد المؤقت هي دقيقة واحدة (1m)!**")

    user_id = None
    if event.is_reply:
        reply = await event.get_reply_message()
        user_id = reply.sender_id
    elif len(args) > 1:
        try:
            user = await client.get_entity(args[1])
            user_id = user.id
        except:
            return await event.edit("⚠️ **لم أجد العضو المطلوب!**")
    else:
        return await event.edit("⚠️ **رد على العضو أو أرسل يوزره مع الوقت!**")

    if user_id == event.sender_id:
        return await event.edit("⚠️ **لا يمكن طرد الملك!**")

    try:
        target = await client.get_entity(user_id)
        name = target.first_name or "المستخدم"
        
        while seconds > 0:
            # --- نظام التحديث الذكي (نفس الكتم) ---
            if seconds > 300: # أكثر من 5 دقائق
                step = 30 # تحديث كل 30 ثانية لضمان عدم الحظر
            else: # 5 دقائق وأقل
                step = 10 # تحديث كل 10 ثواني لزيادة الحماس

            # لضمان عدم تجاوز الصفر في الخطوة الأخيرة
            if step > seconds: step = seconds
            
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            time_left = f"{int(h)}h {int(m)}m {int(s)}s" if h > 0 else f"{int(m)}m {int(s)}s" if m > 0 else f"{int(s)}s"
            
            await event.edit(
                "★────────☭────────★\n"
                "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
                "★────────☭────────★\n\n"
                f"• 𝑵𝒂𝒎𝒆 ⌯ {name}\n"
                f"• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **جاري العد التنازلي للطرد** ⏳\n"
                f"• 𝑻𝒊𝒎𝒆 𝑳𝒆𝒇𝒕 ⌯ `{time_left}`\n\n"
                "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔[𝑵](https://t.me/NETH_RON)〕⌯"
            )
            
            await asyncio.sleep(step)
            seconds -= step

        # تنفيذ الطرد النهائي
        await client.kick_participant(event.chat_id, user_id)
        await event.edit(f"• ⌯ **تم استبعاد {name} من المملكة بنجاح!** ✅")

    except Exception as e:
        await event.edit(f"⚠️ **حدث خطأ:** `{str(e)}`")
