import __main__
from telethon import events, Button
import random
import asyncio

client = __main__.client
bot = __main__.bot

games = {}

def check_winner(board):
    wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for w in wins:
        if board[w[0]] == board[w[1]] == board[w[2]] != " ":
            return board[w[0]]
    if " " not in board: return "تعادل"
    return None

@client.on(events.NewMessage(pattern=r"^\.xo$"))
async def start_xo(event):
    reply = await event.get_reply_message()
    
    player1 = event.sender_id
    player2 = reply.sender_id if reply else "BOT" 
    
    if player1 == player2:
        return await event.edit("❌ **لا يمكنك اللعب ضد نفسك!**")

    game_id = f"{event.chat_id}_{event.id}"
    
    # جلب أسماء اللاعبين للعرض
    p1_name = (await client.get_entity(player1)).first_name
    p2_name = "البوت 🤖" if player2 == "BOT" else (await client.get_entity(player2)).first_name

    games[game_id] = {
        "p1": player1, "p2": player2,
        "p1_name": p1_name, "p2_name": p2_name,
        "turn": player1,
        "board": [" "] * 9,
        "marks": {player1: "❌", player2: "⭕"}
    }

    buttons = update_buttons(games[game_id], game_id)
    await event.delete()
    
    msg = (
        f"🎮 **تحدي XO جديد**\n"
        f"👤 **الخصم:** {p2_name}\n"
        f"⏳ **الدور عند:** {p1_name} (❌)"
    )
    await bot.send_message(event.chat_id, msg, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=r"xo_(.*)"))
async def xo_callback(event):
    data = event.data.decode().split("_")
    game_id = f"{data[1]}_{data[2]}"
    index = int(data[3])
    
    if game_id not in games: return await event.answer("⚠️ اللعبة انتهت!")
    game = games[game_id]
    
    # التحقق من أن الضغطة من صاحب الدور حصراً
    if event.sender_id != game['turn']:
        return await event.answer("🚫 ليس دورك الآن، انتظر الخصم!", alert=True)

    if game['board'][index] != " ":
        return await event.answer("❌ المربع مشغول!", alert=True)

    # حركة اللاعب
    game['board'][index] = game['marks'][event.sender_id]
    
    # فحص الفوز بعد حركة اللاعب
    res = check_winner(game['board'])
    if res: return await finish_game(event, game, game_id, res)

    # تبديل الدور ومنطق البوت
    if game['p2'] == "BOT":
        # إذا كان ضد البوت، يلعب البوت فوراً
        empty_cells = [i for i, val in enumerate(game['board']) if val == " "]
        if empty_cells:
            bot_move = random.choice(empty_cells)
            game['board'][bot_move] = "⭕"
            res = check_winner(game['board'])
            if res: return await finish_game(event, game, game_id, res)
        # يبقى الدور للاعب لأن البوت لعب وانتهى
        current_turn_name = game['p1_name']
    else:
        # تبديل الدور بين الشخصين
        game['turn'] = game['p2'] if event.sender_id == game['p1'] else game['p1']
        current_turn_name = game['p2_name'] if game['turn'] == game['p2'] else game['p1_name']

    # تحديث اللوحة مع عرض الدور الجديد
    buttons = update_buttons(game, game_id)
    mark = game['marks'][game['turn']]
    await event.edit(
        f"🎮 **لعبة XO مستمرة...**\n"
        f"👤 **الخصم:** {game['p2_name']}\n"
        f"⏳ **الدور الآن:** {current_turn_name} ({mark})", 
        buttons=buttons
    )

def update_buttons(game, game_id):
    buttons = []
    for i in range(0, 9, 3):
        row = [Button.inline(game['board'][j] if game['board'][j] != " " else "⬜", data=f"xo_{game_id}_{j}") for j in range(i, i+3)]
        buttons.append(row)
    return buttons

async def finish_game(event, game, game_id, result):
    buttons = update_buttons(game, game_id)
    if result == "تعادل":
        text = "🤝 **انتهت المباراة بالتعادل!**"
    elif result == "⭕" and game['p2'] == "BOT":
        text = "🤖 **لأسف! البوت فاز عليك هذه المرة.**"
    else:
        # تحديد اسم الفائز
        winner_name = game['p1_name'] if result == "❌" else game['p2_name']
        text = f"🎊 **مبروك! الفائز هو: {winner_name}**"
    
    if game_id in games: del games[game_id]
    await event.edit(f"🏁 **خاتمة اللعبة**\n\n{text}", buttons=buttons)
