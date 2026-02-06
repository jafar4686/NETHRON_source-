import __main__, asyncio, random, string
from telethon import events, functions, types
from telethon.errors import FloodWaitError

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]

# متغيرات السيطرة
HUNTING = False

# --- دالة توليد اليوزرات بكافة الأنواع ---
def generate_username(style="عادي", length=5):
    chars = string.ascii_lowercase
    nums = string.digits
    all_chars = chars + nums
    
    if style == "مميز":
        # نمط: a_a_a1 أو x_x_xx
        c = random.choice(chars)
        return f"{c}_{c}_{c}{random.choice(all_chars)}"
    
    elif style == "غريب":
        # نمط: aaabb أو xxyyx أو حروف مكررة
        c1 = random.choice(chars)
        c2 = random.choice(chars)
        return random.choice([
            f"{c1}{c1}{c1}{c2}{c2}", 
            f"{c1}{c2}{c1}{c2}{c1}",
            f"{c1}{c1}{c2}{c1}{c1}"
        ])
    
    else: # النمط العادي
        return "".join(random.choice(all_chars) for _ in range(length))

# ==========================================
# 1. منيو الصيد الشامل (.م16)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م16$"))
async def menu_hunting_full(event):
    msg = (
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑯𝑼𝑵𝑻𝑬𝑹 • ☭\n"
        "★────────☭────────★\n\n"
        "• **صيد الحسابات:**\n"
        "  - `.صيد يوزر` [الطول] ⌯ يوزرات عشوائية\n"
        "  - `.صيد مميز` ⌯ نمط (a_a_a1)\n"
        "  - `.صيد غريب` ⌯ نمط (aaabb)\n\n"
        "• **صيد القنوات (حجز تلقائي):**\n"
        "  - `.صيد قناة` [الطول] ⌯ حجز يوزر عشوائي\n"
        "  - `.صيد قناة مميز` ⌯ حجز يوزر نمط مميز\n"
        "  - `.صيد قناة غريب` ⌯ حجز يوزر نمط غريب\n\n"
        "• **التحكم:**\n"
        "  - `.ايقاف الصيد` ⌯ لإيقاف جميع العمليات\n\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )
    await event.edit(msg)

# ==========================================
# 2. محرك الصيد الرئيسي
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.صيد (يوزر|مميز|غريب|قناة|قناة مميز|قناة غريب)(?:\s+(\d+))?$"))
async def hunter_engine(event):
    global HUNTING
    HUNTING = True
    
    cmd_text = event.text
    length = int(event.pattern_match.group(2)) if event.pattern_match.group(2) else 5
    
    # تحديد النمط والنوع
    is_channel = "قناة" in cmd_text
    if "مميز" in cmd_text: style = "مميز"
    elif "غريب" in cmd_text: style = "غريب"
    else: style = "عادي"
    
    attempts = 0
    await event.edit(f"🚀 **بدأ صيد {style} ({'قنوات' if is_channel else 'حسابات'})...**")
    
    while HUNTING:
        username = generate_username(style, length)
        attempts += 1
        
        try:
            # فحص التوفر
            available = await client(functions.account.CheckUsernameRequest(username=username))
            
            if available:
                if is_channel:
                    # إنشاء القناة وحجز اليوزر
                    create = await client(functions.channels.CreateChannelRequest(
                        title=f"IraqThoon - {username}",
                        about="تم الصيد والحجز بواسطة سورس عراق ثون الملكي"
                    ))
                    await client(functions.channels.UpdateUsernameRequest(
                        channel=create.chats[0].id,
                        username=username
                    ))
                    res_msg = f"🏆 **مبروك! تم صيد وحجز يوزر قناة:** @{username}"
                else:
                    res_msg = f"🎯 **لقطت يوزر {style} متاح:** @{username}"
                
                await client.send_message("me", f"{res_msg}\nالمحاولات: {attempts}")
                await event.respond(res_msg)
                break
            
            # تحديث الواجهة كل 10 محاولات
            if attempts % 10 == 0:
                for f in VORTEX:
                    await event.edit(f"⌯ {f} جاري صيد {style}.. محاولة: {attempts} {f} ⌯\n🔍 فحص: @{username}")
                    await asyncio.sleep(0.05)

            # تأخير آمن بين المحاولات
            await asyncio.sleep(random.uniform(1.8, 3.2))
            
        except FloodWaitError as e:
            await event.edit(f"⚠️ **فلود!** توقف لمدة {e.seconds} ثانية.")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            if "USERNAME_INVALID" in str(e): continue
            else: 
                print(f"Error: {e}")
                continue

# ==========================================
# 3. أمر الإيقاف
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف الصيد$"))
async def stop_hunter(event):
    global HUNTING
    HUNTING = False
    await event.edit("🛑 **تم إيقاف جميع عمليات الصيد.**")
