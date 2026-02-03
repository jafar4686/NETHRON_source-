import __main__, os, json, asyncio
from telethon import events

# استخراج الكلاينت والبيانات الأساسية
client = getattr(__main__, 'client', None)
MEM_FILE = "mem.json"
SUDO_ID = 5580918933  # آيدي المطور
VORTEX = ["◜", "◝", "◞", "◟"]

# --- دالات قاعدة البيانات ---
def get_mem_db():
    if not os.path.exists(MEM_FILE): return {}
    try:
        with open(MEM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}

def save_mem_db(data):
    with open(MEM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 1. أمر إضافة صوت (تنسيق عراق ثون)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اضافة ميمز\s+(https?://t\.me/\S+)\s+(.*)$"))
async def add_meme_iraqthoon(event):
    if event.sender_id != SUDO_ID:
        return await event.edit("⚠️ **عذراً عزيزي، هذا الأمر مخصص للمطور فقط!**")
    
    link = event.pattern_match.group(1)
    name = event.pattern_match.group(2).strip()
    db = get_mem_db()
    
    if name in db:
        return await event.edit(f"⚠️ **الاسم ({name}) موجود مسبقاً في السجل!**")
    if link in db.values():
        return await event.edit("⚠️ **هذا الرابط تم حفظه مسبقاً باسم آخر!**")
    
    db[name] = link
    save_mem_db(db)
    
    msg = (
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑴𝑬𝑴𝑬𝑺 • ☭\n"
        "★────────☭────────★\n\n"
        f"• 𝑵𝒂𝒎𝒆 ⌯ `{name}`\n"
        "• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **تمت الإضافة بنجاح** ✅\n\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )
    await event.edit(msg)

# ==========================================
# 2. أمر حذف صوت (تنسيق عراق ثون)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حذف ميمز\s+(.*)$"))
async def delete_meme_iraqthoon(event):
    if event.sender_id != SUDO_ID:
        return await event.edit("⚠️ **عذراً عزيزي، هذا الأمر للمطور فقط!**")
    
    name = event.pattern_match.group(1).strip()
    db = get_mem_db()
    
    if name in db:
        del db[name]
        save_mem_db(db)
        msg = (
            "★────────☭────────★\n"
            "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑴𝑬𝑴𝑬𝑺 • ☭\n"
            "★────────☭────────★\n\n"
            f"• 𝑵𝒂𝒎𝒆 ⌯ `{name}`\n"
            "• 𝑺𝒕𝒂𝒕𝒖𝒔 ⌯ **تم الحذف من السجلات** 🗑️\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
        )
        await event.edit(msg)
    else:
        await event.edit(f"🔍 **لم أجد بصمة باسم ({name}) لحذفها!**")

# ==========================================
# 3. أمر عرض القائمة (تنسيق عراق ثون)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ميمز$"))
async def list_memes_iraqthoon(event):
    db = get_mem_db()
    if not db: return await event.edit("⚠️ **قائمة الميمز فارغة حالياً!**")
    
    res = (
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑴𝑬𝑴𝑬𝑺 • ☭\n"
        "★────────☭────────★\n\n"
        "• **الأصوات المتاحة بالمملكة:**\n\n"
    )
    for i, name in enumerate(db.keys(), 1):
        res += f"{i}- `{name}`\n"
        
    res += "\n• للاستدعاء أرسل: `.م [الاسم]`\n"
    res += "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    await event.edit(res)

# ==========================================
# 4. أمر التشغيل (الدوامة + التنسيق الملكي)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م\s+(.*)$"))
async def play_meme_iraqthoon(event):
    query = event.pattern_match.group(1).strip()
    db = get_mem_db()
    
    found_key = next((k for k in db if query.lower() in k.lower()), None)
    
    if found_key:
        try:
            # حركات الدوامة عراق ثون
            for f in VORTEX:
                await event.edit(f"⌯ {f} 〔 جاري سحب البصمة الملكية 〕 {f} ⌯")
                await asyncio.sleep(0.1)

            # إرسال البصمة
            await client.send_file(
                event.chat_id, 
                db[found_key], 
                voice_note=True, 
                reply_to=event.reply_to_msg_id
            )
            await event.delete()
            
        except Exception as e:
            await event.edit(f"❌ **فشل السحب! الرابط قد يكون معطوباً.**")
    else:
        await event.edit(f"🔍 **لم أجد بصمة باسم ({query})!**")
