import __main__
from telethon import events, Button
import random
import asyncio

# استدعاء الحساب الشخصي والبوت المساعد من ملف maker.py
client = __main__.client
bot = __main__.bot

# مخزن بيانات اللعبة
XO_GAMES = {}

# ==========================================
# 1. كليشة قائمة الأوامر .م4
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
        "• `.قرعة` (كلمة1 كلمة2) \n"
        "➥ اختيار عشوائي بين شيئين\n\n"
        "• `.كت تويت` \n"
        "➥ أسئلة منوعة وجريئة\n\n"
        "• `.عقوبة` \n"
        "➥ يختار لك عقوبة مضحكة\n\n"
        "★──────────☭──────────★\n"
        "📢 **أرسل اسم اللعبة للاستمتاع!**"
    )
    await event.edit(m4_text)

# ==========================================
# 2. نظام لعبة X-O المتطور
# ==========================================

# دالة بناء لوحة الأزرار
def build_board(game_id):
    game = XO_GAMES[game_id]
    b = game['board']
    buttons = []
    for i in range(0, 9, 3):
        buttons.append([
            Button.inline(b[i] or " ", data=f"xo_{game_id}_{i}"),
            Button.inline(b[i+1] or " ", data=f"xo_{game_id}_{i+1}"),
            Button.inline(b[i+2] or " ", data=f"xo_{game_id}_{i+2}")
        ])
    buttons.append([Button.inline("❌ إنهاء اللعبة", data=f"xo_{game_id}_stop")])
    return buttons

# التحقق من الفوز
def check_winner(board):
    win_sets = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for s in win_sets:
        if board[s[0]] == board[s[1]] == board[s[2]] and board[s[0]] is not None:
            return board[s[0]]
    if None not in board: return "draw"
    return None

# أمر بدء اللعبة من الحساب الشخصي
@client.on(events.NewMessage(pattern=r"^\.xo$"))
async def start_xo(event):
    if not event.out: return
    
    reply = await event.get_reply_message()
    if event.is_private:
        player2 = event.chat_id
    elif reply:
        player2 = reply.sender_id
    else:
        return await event.edit("**⚠️ رد على الشخص أو العب في الخاص!**")

    player1 = event.sender_id
    game_id = random.randint(1000, 9999)
    turn = random.choice([player1, player2])

    XO_GAMES[game_id] = {
        'p1': player1, 'p2': player2,
        'board': [None]*9,
        'turn': turn,
        'sym': {player1: "❌", player2: "⭕"}
    }

    await event.delete() # حذف الأمر من حسابك
    
    # جلب اسم الشخص اللي عليه الدور
    turn_user = await client.get_entity(turn)
    turn_name = "أنت" if turn == player1 else turn_user.first_name

    welcome_msg = (
        "🎮 **لعبة X - O نيثرون**\n"
        "★──────────★\n"
        f"🎲 **الدور الآن عند:** {turn_name}"
    )

    # الإرسال عبر البوت المساعد
    await bot.send_message(event.chat_id, welcome_msg, buttons=build_board(game_id))

# معالجة الأزرار عبر البوت المساعد
@bot.on(events.CallbackQuery(pattern=r"xo_(\d+)_(\d+|stop)"))
async def xo_callback(event):
    game_id = int(event.pattern_match.group(1))
    action = event.pattern_match.group(2)
    
    if game_id not in XO_GAMES:
        return await event.answer("⚠️ انتهت الجلسة!", alert=True)

    game = XO_GAMES[game_id]
    
    if action == "stop":
        if event.sender_id not in [game['p1'], game['p2']]:
            return await event.answer("مو لعبتك!", alert=True)
        del XO_GAMES[game_id]
        return await event.edit("❌ تم إلغاء اللعبة.")

    move = int(action)
    if event.sender_id != game['turn']:
        return await event.answer("مو دورك! انتظر الخصم..", alert=True)

    if game['board'][move] is not None:
        return await event.answer("المكان مشغول!", alert=True)

    # تحديث اللوحة
    game['board'][move] = game['sym'][event.sender_id]
    
    # فحص الفائز
    res = check_winner(game['board'])
    if res:
        if res == "draw":
            await event.edit("🤝 **تعادل! لا يوجد فائز.**", buttons=None)
        else:
            winner_user = await bot.get_entity(event.sender_id)
            await event.edit(f"🎊 **مبروك فاز [ {winner_user.first_name} ]!** 🏆", buttons=None)
        del XO_GAMES[game_id]
        return

    # تبديل الدور
    game['turn'] = game['p2'] if game['turn'] == game['p1'] else game['p1']
    next_user = await bot.get_entity(game['turn'])
    
    await event.edit(
        f"🎮 **لعبة X - O مستمرة**\n🎲 **الدور عند:** {next_user.first_name}",
        buttons=build_board(game_id)
    )
