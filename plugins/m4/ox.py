import __main__
from telethon import events, Button
import random

# استدعاء الكلاينت (حسابك) والبوت (المساعد)
client = __main__.client
bot = __main__.bot

# مخزن بيانات اللعبة
XO_GAMES = {}

# ==========================================
# 1. قائمة الأوامر .م4 (تنسيق نيثرون)
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
# 2. نظام لعبة X-O (إصلاح استجابة الأزرار)
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
    
    player1 = event.sender_id # صاحب الحساب
    player2 = None
    
    reply = await event.get_reply_message()
    
    # التحقق من نوع المحادثة والخصم
    if event.is_private:
        player2 = event.chat_id # في الخاص، الخصم هو صاحب المحادثة
    elif reply:
        player2 = reply.sender_id # في المجموعات، الخصم هو الشخص المردود عليه
    else:
        return await event.edit("**⚠️ في المجموعات، يجب الرد على الشخص للعب معه!**")

    game_id = random.randint(100, 999)
    # جعل الخصم (الطرف الآخر) هو من يبدأ اللعب دائماً
    turn = player2 

    XO_GAMES[game_id] = {
        'p1': player1, 'p2': player2,
        'board': [None]*9,
        'turn': turn, 
        'sym': {player1: "⭕", player2: "❌"}
    }

    await event.delete()
    
    try:
        p2_ent = await client.get_entity(player2)
        p2_name = p2_ent.first_name
    except:
        p2_name = "الخصم"

    welcome_msg = (
        "🎮 **تحدي X - O نيثرون**\n"
        "★──────────★\n"
        f"👤 لاعب 1: أنت (⭕)\n"
        f"👤 لاعب 2: {p2_name} (❌)\n"
        "★──────────★\n"
        f"🎲 الدور الآن عند: {p2_name}"
    )

    await bot.send_message(event.chat_id, welcome_msg, buttons=build_board(game_id))

@bot.on(events.CallbackQuery(pattern=r"xo_(\d+)_(\d+|stop)"))
async def xo_callback(event):
    game_id = int(event.pattern_match.group(1))
    action = event.pattern_match.group(2)
    
    if game_id not in XO_GAMES:
        return await event.answer("⚠️ اللعبة انتهت!", alert=True)

    game = XO_GAMES[game_id]
    
    # التحقق من أن الضغط من أحد اللاعبين فقط
    if event.sender_id not in [game['p1'], game['p2']]:
        return await event.answer("❌ عذراً، هذه اللعبة ليست لك!", alert=True)

    if action == "stop":
        del XO_GAMES[game_id]
        return await event.edit("❌ تم إنهاء اللعبة.")

    # التحقق من الدور
    if event.sender_id != game['turn']:
        return await event.answer("⏳ انتظر دور الخصم!", alert=True)

    move = int(action)
    if game['board'][move] is not None:
        return await event.answer("🚫 المكان محجوز!", alert=True)

    # تنفيذ الحركة
    game['board'][move] = game['sym'][event.sender_id]
    
    # فحص النتيجة
    res = check_winner(game['board'])
    if res:
        if res == "draw":
            await event.edit("🤝 **تعادل!** لا يوجد فائز.", buttons=None)
        else:
            winner_name = (await bot.get_entity(event.sender_id)).first_name
            await event.edit(f"🎊 **مبروك الفوز لـ [ {winner_name} ]** 🏆", buttons=None)
        del XO_GAMES[game_id]
        return

    # تبديل الدور
    game['turn'] = game['p1'] if game['turn'] == game['p2'] else game['p2']
    next_user = await bot.get_entity(game['turn'])
    
    await event.edit(
        f"🎮 **تحدي X - O مستمر**\n🎲 الدور الآن عند: {next_user.first_name}",
        buttons=build_board(game_id)
)
