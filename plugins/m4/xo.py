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
    
    # إذا لم يوجد رد، يلعب المستخدم ضد البوت
    player1 = event.sender_id
    player2 = reply.sender_id if reply else "BOT" 
    
    game_id = f"{event.chat_id}_{event.id}"
    turn = player1 # المستخدم يبدأ دائماً
    
    games[game_id] = {
        "p1": player1, "p2": player2,
        "turn": turn,
        "board": [" "] * 9,
        "marks": {player1: "❌", player2: "⭕"}
    }

    buttons = []
    for i in range(0, 9, 3):
        row = [Button.inline("⬜", data=f"xo_{game_id}_{j}") for j in range(i, i+3)]
        buttons.append(row)

    await event.delete()
    mode_text = "ضد البوت 🤖" if player2 == "BOT" else f"ضد [(خصم)](tg://user?id={player2})"
    await bot.send_message(event.chat_id, f"🎮 **تحدي XO جديد ({mode_text})**\n\nدورك الآن: ارسل حركتك بالضغط على المربعات.", buttons=buttons)

@bot.on(events.CallbackQuery(pattern=r"xo_(.*)"))
async def xo_callback(event):
    data = event.data.decode().split("_")
    game_id = f"{data[1]}_{data[2]}"
    index = int(data[3])
    
    if game_id not in games: return await event.answer("⚠️ اللعبة انتهت!")
    
    game = games[game_id]
    
    # منع التدخل
    if event.sender_id != game['turn']:
        return await event.answer("🚫 ليس دورك الآن!", alert=True)

    if game['board'][index] != " ":
        return await event.answer("❌ المربع مشغول!", alert=True)

    # حركة اللاعب (الإنسان)
    game['board'][index] = game['marks'][event.sender_id]
    
    # فحص الفوز بعد حركة اللاعب
    res = check_winner(game['board'])
    if res: return await finish_game(event, game, game_id, res)

    # إذا كان اللعب ضد البوت
    if game['p2'] == "BOT":
        # حركة البوت
        empty_cells = [i for i, val in enumerate(game['board']) if val == " "]
        if empty_cells:
            bot_move = random.choice(empty_cells)
            game['board'][bot_move] = "⭕"
            
            # فحص الفوز بعد حركة البوت
            res = check_winner(game['board'])
            if res: return await finish_game(event, game, game_id, res)
    else:
        # تبديل الدور للإنسان الآخر
        game['turn'] = game['p2'] if event.sender_id == game['p1'] else game['p1']

    # تحديث اللوحة
    buttons = update_buttons(game, game_id)
    mention = "دورك الآن" if game['p2'] == "BOT" else f"دور: [(اللاعب)](tg://user?id={game['turn']})"
    await event.edit(f"🎮 **لعبة XO مستمرة...**\n\n{mention}", buttons=buttons)

def update_buttons(game, game_id):
    buttons = []
    for i in range(0, 9, 3):
        row = [Button.inline(game['board'][j] if game['board'][j] != " " else "⬜", data=f"xo_{game_id}_{j}") for j in range(i, i+3)]
        buttons.append(row)
    return buttons

async def finish_game(event, game, game_id, result):
    buttons = update_buttons(game, game_id)
    if result == "تعادل":
        text = "🤝 **انتهت بالتعادل!**"
    elif result == "⭕" and game['p2'] == "BOT":
        text = "🤖 **لأسف! البوت فاز عليك.**"
    else:
        text = f"🎊 **مبروك! الفائز هو {result}**"
    
    del games[game_id]
    await event.edit(f"🎮 **خاتمة اللعبة**\n\n{text}", buttons=buttons)
