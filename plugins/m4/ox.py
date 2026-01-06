import __main__
from telethon import events, Button
import random

# استدعاء الكلاينت (حسابك) والبوت (المساعد)
client = __main__.client
bot = __main__.bot

# مخزن بيانات اللعبة لضمان عدم التداخل
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
        "• `.كت تويت` \n"
        "➥ أسئلة منوعة وجريئة\n\n"
        "• `.عقوبة` \n"
        "➥ يختار لك عقوبة مضحكة\n\n"
        "★──────────☭──────────★\n"
        "📢 **أرسل اسم اللعبة للاستمتاع!**"
    )
    await event.edit(m4_text)

# ==========================================
# 2. نظام لعبة X-O (الإصدار المصحح للأزرار)
# ==========================================

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
    buttons.append([Button.inline("🏁 إنهاء اللعبة", data=f"xo_{game_id}_stop")])
    return buttons

def check_winner(board):
    win_sets = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for s in win_sets:
        if board[s[0]] == board[s[1]] == board[s[2]] and board[s[0]] is not None:
            return board[s[0]]
    if None not in board: return "draw"
    return None

@client.on(events.NewMessage(pattern=r"^\.xo$"))
async def start_xo(event):
    if not event.out: return
    
    reply = await event.get_reply_message()
    player1 = event.sender_id # أنت
    
    if event.is_private:
        player2 = event.chat_id
    elif reply:
        player2 = reply.sender_id # الخصم
    else:
        return await event.edit("**⚠️ يجب الرد على الشخص للعب معه!**")

    game_id = random.randint(100, 999)
    # الخصم (player2) يبدأ دائماً بـ ❌ لضمان أن البوت يستجيب له فوراً
    XO_GAMES[game_id] = {
        'p1': player1, 'p2': player2,
        'board': [None]*9,
        'turn': player2, 
        'sym': {player1: "⭕", player2: "❌"}
    }

    await event.delete() # حذف الأمر من حسابك فوراً
    
    p2_entity = await client.get_entity(player2)
    p2_name = p2_entity.first_name

    welcome_msg = (
        "🎮 **تحدي X - O نيثرون**\n"
        "★──────────★\n"
        f"👤 اللاعب الأول: أنت (⭕)\n"
        f"👤 اللاعب الثاني: {p2_name} (❌)\n"
        "★──────────★\n"
        f"🎲 دور اللاعب: {p2_name}"
    )

    # الإرسال عبر البوت المساعد لضمان ظهور الأزرار
    await bot.send_message(event.chat_id, welcome_msg, buttons=build_board(game_id))

@bot.on(events.CallbackQuery(pattern=r"xo_(\d+)_(\d+|stop)"))
async def xo_callback(event):
    game_id = int(event.pattern_match.group(1))
    action = event.pattern_match.group(2)
    
    if game_id not in XO_GAMES:
        return await event.answer("⚠️ انتهت اللعبة!", alert=True)

    game = XO_GAMES[game_id]
    
    # معالجة زر الإيقاف
    if action == "stop":
        if event.sender_id not in [game['p1'], game['p2']]:
            return await event.answer("ليست لعبتك!", alert=True)
        del XO_GAMES[game_id]
        return await event.edit("❌ تم إنهاء اللعبة من قبل اللاعبين.")

    # معالجة حركات اللعب
    if event.sender_id != game['turn']:
        return await event.answer("انتظر دورك! ⏳", alert=True)

    move = int(action)
    if game['board'][move] is not None:
        return await event.answer("هذا المكان مشغول!", alert=True)

    # وضع العلامة وتحديث الدور
    game['board'][move] = game['sym'][event.sender_id]
    
    # فحص الفوز أو التعادل
    res = check_winner(game['board'])
    if res:
        if res == "draw":
            await event.edit("🤝 **تعادل!** لا يوجد فائز هذه المرة.", buttons=None)
        else:
            winner_user = await bot.get_entity(event.sender_id)
            await event.edit(f"🎊 **مبروك الفوز!** اللاعب [ {winner_user.first_name} ] هو البطل 🏆", buttons=None)
        del XO_GAMES[game_id]
        return

    # تبديل الدور للطرف الآخر
    game['turn'] = game['p1'] if game['turn'] == game['p2'] else game['p2']
    next_user = await bot.get_entity(game['turn'])
    
    await event.edit(
        f"🎮 **تحدي X - O مستمر**\n🎲 دور اللاعب: {next_user.first_name}",
        buttons=build_board(game_id)
                                 )
