import __main__
from telethon import events, Button
import random

# استدعاء الحساب والبوت
client = __main__.client
bot = __main__.bot

XO_GAMES = {}

# ==========================================
# 1. كليشة القائمة .م4
# ==========================================
@client.on(events.NewMessage(pattern=r"^\.م4$"))
async def m4_command(event):
    if not event.out: return
    m4_text = (
        "★────────☭────────★\n"
        "   ☭ • 𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 • ☭\n"
        "                  ☭ • سورس نيثرون • ☭\n"
        "★────────☭────────★\n\n"
        "🎮 **قائمة الألعاب والتسلية:**\n\n"
        "• `.xo` \n"
        "➥ بدء لعبة إكس أو (أزرار عبر البوت)\n\n"
        "• `.تفكيك` \n"
        "➥ لعبة أسرع واحد يفكك الكلمة\n\n"
        "• `.كت تويت` \n"
        "➥ أسئلة منوعة وجريئة\n\n"
        "• `.عقوبة` \n"
        "➥ يختار لك عقوبة مضحكة\n\n"
        "★──────────☭──────────★\n"
        "📢 **أرسل اسم اللعبة للاستمتاع!**"
    )
    await event.edit(m4_text)

# ==========================================
# 2. برمجة لعبة X-O (نظام الوسيط)
# ==========================================

def get_buttons(g_id):
    g = XO_GAMES[g_id]
    b = g['board']
    btns = []
    for i in range(0, 9, 3):
        btns.append([
            Button.inline(b[i] or " ", data=f"x_{g_id}_{i}"),
            Button.inline(b[i+1] or " ", data=f"x_{g_id}_{i+1}"),
            Button.inline(b[i+2] or " ", data=f"x_{g_id}_{i+2}")
        ])
    btns.append([Button.inline("🏁 إنهاء", data=f"x_{g_id}_stop")])
    return btns

def check_win(b):
    ways = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for s in ways:
        if b[s[0]] == b[s[1]] == b[s[2]] and b[s[0]] is not None: return b[s[0]]
    return "draw" if None not in b else None

# التشغيل من الحساب الشخصي
@client.on(events.NewMessage(pattern=r"^\.xo$"))
async def start_game(event):
    if not event.out: return
    
    player1 = event.sender_id # أنت
    player2 = None
    reply = await event.get_reply_message()

    if event.is_private:
        player2 = event.chat_id
    elif reply:
        player2 = reply.sender_id
    else:
        return await event.edit("**⚠️ رد على الشخص لبدء اللعبة!**")

    # توليد ID للعبة
    g_id = random.randint(100, 999)
    
    # تخزين البيانات
    XO_GAMES[g_id] = {
        'p1': player1, 'p2': player2,
        'board': [None]*9, 'turn': player2, # الخصم يبدأ
        'sym': {player1: "⭕", player2: "❌"}
    }

    await event.delete()
    
    # الحساب الشخصي يرسل الرسالة "كوسيط" ويجعل البوت يضع الأزرار
    try:
        p2_user = await client.get_entity(player2)
        name2 = p2_user.first_name
    except: name2 = "الخصم"

    msg = f"🎮 **تحدي X-O (نيثرون)**\n★──────────★\n👤 أنت: (⭕)\n👤 {name2}: (❌)\n★──────────★\n🎲 الدور عند: {name2}"
    
    # إرسال عبر البوت المساعد لظهور الأزرار
    await bot.send_message(event.chat_id, msg, buttons=get_buttons(g_id))

# معالجة الأزرار (تسمح للطرفين بالضغط)
@bot.on(events.CallbackQuery(pattern=r"x_(\d+)_(\d+|stop)"))
async def xo_callback(event):
    g_id = int(event.pattern_match.group(1))
    act = event.pattern_match.group(2)
    
    if g_id not in XO_GAMES:
        return await event.answer("⚠️ اللعبة غير موجودة!", alert=True)
    
    g = XO_GAMES[g_id]

    # السماح بالضغط فقط للاعبين
    if event.sender_id not in [g['p1'], g['p2']]:
        return await event.answer("❌ لست طرفاً في هذه اللعبة!", alert=True)

    if act == "stop":
        del XO_GAMES[g_id]
        return await event.edit("❌ تم إنهاء اللعبة.")

    # التحقق من الدور
    if event.sender_id != g['turn']:
        return await event.answer("⏳ انتظر دور خصمك!", alert=True)

    move = int(act)
    if g['board'][move] is not None:
        return await event.answer("🚫 المكان مشغول!", alert=True)

    # تحديث اللوحة
    g['board'][move] = g['sym'][event.sender_id]
    
    res = check_win(g['board'])
    if res:
        if res == "draw":
            await event.edit("🤝 **تعادل!**", buttons=None)
        else:
            # استخدام bot.get_entity لضمان جلب الاسم حتى لو الحساب الشخصي ما عنده يوزره
            winner = await bot.get_entity(event.sender_id)
            await event.edit(f"🎊 **مبروك الفوز لـ {winner.first_name}** 🏆", buttons=None)
        del XO_GAMES[g_id]
        return

    # تبديل الدور
    g['turn'] = g['p1'] if g['turn'] == g['p2'] else g['p2']
    try:
        next_p = await bot.get_entity(g['turn'])
        next_name = next_p.first_name
    except: next_name = "الخصم"

    await event.edit(
        f"🎮 **تحدي X-O (نيثرون)**\n🎲 الدور الآن: {next_name}",
        buttons=get_buttons(g_id)
        )
