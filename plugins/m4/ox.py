import __main__
from telethon import events, Button
from telethon.tl.functions.users import GetFullUserRequest
import random
import asyncio

# جلب الكلاينت والبوت من الملف الرئيسي (maker.py)
client = __main__.client
bot = __main__.bot

# مخزن لبيانات الألعاب النشطة
XO_GAMES = {}

# دالة لرسم لوحة اللعبة بالأزرار
def build_board(game):
    board = game['board']
    buttons = []
    for i in range(0, 9, 3):
        row = [
            Button.inline(board[i] if board[i] else " ", data=f"xo_{game['id']}_{i}"),
            Button.inline(board[i+1] if board[i+1] else " ", data=f"xo_{game['id']}_{i+1}"),
            Button.inline(board[i+2] if board[i+2] else " ", data=f"xo_{game['id']}_{i+2}")
        ]
        buttons.append(row)
    buttons.append([Button.inline("❌ إنهاء اللعبة", data=f"xo_{game['id']}_stop")])
    return buttons

# التحقق من الفوز
def check_winner(board):
    win_sets = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for s in win_sets:
        if board[s[0]] == board[s[1]] == board[s[2]] and board[s[0]] is not None:
            return board[s[0]]
    if None not in board: return "draw"
    return None

# --- [ أمر بدء اللعبة من الحساب الشخصي ] ---
@client.on(events.NewMessage(pattern=r"^\.xo$"))
async def start_xo(event):
    if not event.out: return
    
    player1 = event.sender_id
    player2 = None
    
    # تحديد الخصم
    reply = await event.get_reply_message()
    if event.is_private:
        player2 = event.chat_id
    elif reply:
        player2 = reply.sender_id
    else:
        return await event.edit("**- عذراً ، في المجموعات يجب الرد على الشخص للعب معه!**")

    game_id = random.randint(1000, 9999)
    turn = random.choice([player1, player2])
    
    XO_GAMES[game_id] = {
        'id': game_id,
        'p1': player1, 'p2': player2,
        'sym': {player1: "❌", player2: "⭕"},
        'board': [None]*9,
        'turn': turn
    }

    p2_user = await client.get_entity(player2)
    turn_name = "أنت" if turn == player1 else p2_user.first_name

    welcome_msg = (
        "🎮 **لعبة X - O (نيثرون)**\n"
        "★──────────★\n"
        f"👤 **اللاعب الأول:** أنت (❌)\n"
        f"👤 **اللاعب الثاني:** {p2_user.first_name} (⭕)\n"
        "★──────────★\n"
        f"🎲 **الدور الآن عند:** {turn_name}"
    )

    # إرسال الرسالة عبر البوت المساعد لتظهر الأزرار
    bot_user = await bot.get_me()
    await event.delete()
    await bot.send_message(
        event.chat_id, 
        welcome_msg, 
        buttons=build_board(XO_GAMES[game_id])
    )

# --- [ معالجة ضغطات الأزرار عبر البوت المساعد ] ---
@bot.on(events.CallbackQuery(pattern=r"xo_(\d+)_(\d+|stop)"))
async def xo_callback(event):
    game_id = int(event.pattern_match.group(1))
    action = event.pattern_match.group(2)
    
    if game_id not in XO_GAMES:
        return await event.answer("⚠️ اللعبة انتهت بالفعل!", alert=True)

    game = XO_GAMES[game_id]
    
    if action == "stop":
        if event.sender_id not in [game['p1'], game['p2']]:
            return await event.answer("ليست لعبتك!", alert=True)
        del XO_GAMES[game_id]
        return await event.edit("❌ تم إنهاء اللعبة من قبل اللاعبين.")

    move = int(action)
    
    # التأكد من دور اللاعب
    if event.sender_id != game['turn']:
        return await event.answer("مو دورك! انتظر الخصم يلعب ⏳", alert=True)

    # التأكد من أن المكان فارغ
    if game['board'][move] is not None:
        return await event.answer("هذا المكان محجوز! اختر غيره.", alert=True)

    # تنفيذ الحركة
    game['board'][move] = game['sym'][event.sender_id]
    
    # التحقق من الفوز
    winner_sym = check_winner(game['board'])
    if winner_sym:
        if winner_sym == "draw":
            await event.edit("🤝 **تعادل! لا يوجد فائز.**", buttons=None)
        else:
            winner_id = game['p1'] if game['sym'][game['p1']] == winner_sym else game['p2']
            winner_user = await bot.get_entity(winner_id)
            await event.edit(f"🎊 **مبروك فاز [ {winner_user.first_name} ] باللعبة!** 🏆", buttons=None)
        del XO_GAMES[game_id]
        return

    # تبديل الأدوار
    game['turn'] = game['p2'] if game['turn'] == game['p1'] else game['p1']
    next_user = await bot.get_entity(game['turn'])
    
    await event.edit(
        f"🎮 **لعبة X - O نشطة**\n🎲 **الدور عند:** {next_user.first_name}",
        buttons=build_board(game)
  )
