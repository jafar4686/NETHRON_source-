import __main__, asyncio, random, string
from telethon import events, functions, types
from telethon.errors import FloodWaitError

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]

# متغيرات السيطرة على الصيد
HUNTING = False

# دالة لتوليد يوزرات عشوائية (ثلاثية، رباعية، خماسية)
def generate_username(length=5):
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))

# ==========================================
# 1. منيو الصيد (.م16)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م16$"))
async def menu_hunting(event):
    msg = (
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑯𝑼𝑵𝑻𝑬𝑹 • ☭\n"
        "★────────☭────────★\n\n"
        "• `.صيد يوزر` [الطول] ⌯ يبدأ بفحص يوزرات متاحة\n"
        "• `.صيد قناة` [الطول] ⌯ فحص وإنشاء قناة تلقائياً\n"
        "• `.ايقاف الصيد` ⌯ لإيقاف جميع عمليات الفحص\n\n"
        "• **مثال:** `.صيد قناة 5` (يصيد يوزر خماسي)\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )
    await event.edit(msg)

# ==========================================
# 2. أمر صيد يوزر حساب
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.صيد يوزر\s+(\d+)$"))
async def hunt_user(event):
    global HUNTING
    HUNTING = True
    length = int(event.pattern_match.group(1))
    attempts = 0
    
    await event.edit(f"🚀 **بدأ صيد اليوزرات (طول {length})...**")
    
    while HUNTING:
        username = generate_username(length)
        attempts += 1
        
        try:
            # فحص إذا كان اليوزر متاحاً
            result = await client(functions.account.CheckUsernameRequest(username=username))
            
            if result: # إذا كان متاحاً
                await client.send_message("me", f"🎯 **يوزر متاح لقطته!**\n• اليوزر: @{username}\n• المحاولات: {attempts}")
                await event.respond(f"✅ **تم إيجاد يوزر متاح:** @{username}")
                break
            
            # تحديث الرسالة كل 5 محاولات لتقليل الضغط
            if attempts % 5 == 0:
                for f in VORTEX:
                    await event.edit(f"⌯ {f} جاري الصيد.. محاولة: {attempts} {f} ⌯\n🔍 فحص: @{username}")
                    await asyncio.sleep(0.1)

            # تأخير بين 1 إلى 2 ثانية لتجنب الحظر كما طلبت
            await asyncio.sleep(random.uniform(1.5, 2.5))
            
        except FloodWaitError as e:
            await event.edit(f"⚠️ **توقف بسبب الفلود!** انتظر {e.seconds} ثانية.")
            await asyncio.sleep(e.seconds)
        except Exception:
            continue

# ==========================================
# 3. صيد يوزر قناة + إنشاء تلقائي
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.صيد قناة\s+(\d+)$"))
async def hunt_channel(event):
    global HUNTING
    HUNTING = True
    length = int(event.pattern_match.group(1))
    attempts = 0
    
    await event.edit(f"🛰 **بدأ صيد يوزرات القنوات (طول {length})...**")
    
    while HUNTING:
        username = generate_username(length)
        attempts += 1
        
        try:
            # فحص التوفر
            available = await client(functions.account.CheckUsernameRequest(username=username))
            
            if available:
                # إنشاء قناة جديدة فوراً
                created_chat = await client(functions.channels.CreateChannelRequest(
                    title=f"IraqThoon Hunter - {username}",
                    about="هذه القناة تم حجزها بواسطة سكرابت الصيد الملكي",
                    megagroup=False
                ))
                channel_id = created_chat.chats[0].id
                
                # تثبيت اليوزر على القناة
                await client(functions.channels.UpdateUsernameRequest(
                    channel=channel_id,
                    username=username
                ))
                
                await client.send_message("me", f"🏆 **مبروك! تم صيد يوزر وحجزه بقناة:**\n• اليوزر: @{username}\n• الرابط: t.me/{username}")
                await event.respond(f"🔥 **تم صيد يوزر قناة وحجزه بنجاح:** @{username}")
                break
            
            if attempts % 5 == 0:
                await event.edit(f"⚙️ **جاري الصيد والحجز..**\nمحاولة رقم: `{attempts}`\nآخر فحص: @{username}")

            await asyncio.sleep(random.uniform(2.0, 3.5)) # تأخير أطول قليلاً للقنوات
            
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception as e:
            if "USERNAME_INVALID" in str(e): continue
            else: break

# ==========================================
# 4. إيقاف الصيد
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف الصيد$"))
async def stop_hunting(event):
    global HUNTING
    HUNTING = False
    await event.edit("🛑 **تم إيقاف عمليات الصيد بنجاح.**")
