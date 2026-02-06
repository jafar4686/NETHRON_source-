import __main__, asyncio, random, string, requests
from telethon import events, functions, types
from telethon.errors import FloodWaitError

client = getattr(__main__, 'client', None)
HUNTING = False

# --- دالة توليد اليوزرات ---
def generate_username(style="عادي", length=5):
    chars = string.ascii_lowercase
    nums = string.digits
    all_chars = chars + nums
    if style == "مميز":
        c = random.choice(chars)
        return f"{c}_{c}_{c}{random.choice(all_chars)}"
    elif style == "غريب":
        c1, c2 = random.choice(chars), random.choice(chars)
        return random.choice([f"{c1}{c1}{c1}{c2}{c2}", f"{c1}{c2}{c1}{c2}{c1}", f"{c1}{c1}{c2}{c1}{c1}"])
    else:
        return "".join(random.choice(all_chars) for _ in range(length))

# --- دالات فحص المنصات الخارجية ---
def check_insta(user):
    url = f"https://www.instagram.com/{user}/"
    res = requests.get(url)
    return True if res.status_code == 404 else False

def check_tiktok(user):
    url = f"https://www.tiktok.com/@{user}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    return True if res.status_code == 404 else False

# ==========================================
# 1. المنيو المطور (.م16)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م16$"))
async def menu_hunting_global(event):
    msg = (
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑮𝑳𝑶𝑩𝑨𝑳 𝑯𝑼𝑵𝑻𝑬𝑹 • ☭\n"
        "★────────☭────────★\n\n"
        "• **صيد تليجرام:** `.صيد تلي` [نوع] [طول]\n"
        "• **صيد انستقرام:** `.صيد انستا` [نوع] [طول]\n"
        "• **صيد تيك توك:** `.صيد تيك` [نوع] [طول]\n\n"
        "• **الأنواع المتاحة:** (يوزر، مميز، غريب)\n"
        "• **أمثلة:** `.صيد انستا مميز` | `.صيد تيك يوزر 4`\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )
    await event.edit(msg)

# ==========================================
# 2. محرك الصيد العالمي
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.صيد (تلي|انستا|تيك)(?:\s+(يوزر|مميز|غريب))?(?:\s+(\d+))?$"))
async def global_hunter(event):
    global HUNTING
    HUNTING = True
    
    platform = event.pattern_match.group(1)
    style = event.pattern_match.group(2) or "يوزر"
    length = int(event.pattern_match.group(3)) if event.pattern_match.group(3) else 5
    
    attempts = 0
    await event.edit(f"🚀 **بدأ الصيد في {platform}.. النمط: {style}**")
    
    while HUNTING:
        username = generate_username(style if style != "يوزر" else "عادي", length)
        attempts += 1
        is_available = False
        
        try:
            if platform == "تلي":
                is_available = await client(functions.account.CheckUsernameRequest(username=username))
            elif platform == "انستا":
                is_available = check_insta(username)
            elif platform == "تيك":
                is_available = check_tiktok(username)
            
            if is_available:
                res_msg = f"🎯 **لقطت يوزر متاح في {platform}!**\n• اليوزر: `@{username}`\n• النمط: {style}"
                await client.send_message("me", res_msg + f"\n• المحاولات: {attempts}")
                await event.respond(res_msg)
                break
                
            if attempts % 10 == 0:
                await event.edit(f"🔍 **صيد {platform}...**\nالمحاولة: `{attempts}`\nآخر فحص: `@{username}`")
            
            await asyncio.sleep(2.5) # تأخير آمن للمنصات الخارجية
            
        except Exception:
            await asyncio.sleep(5)
            continue

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ايقاف الصيد$"))
async def stop_h(event):
    global HUNTING
    HUNTING = False
    await event.edit("🛑 **تم إيقاف جميع عمليات الصيد العالمية.**")
