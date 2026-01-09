import __main__
from telethon import events, Button
import random

# استدعاء الكلاينت والبوت من الملف الرئيسي
client = __main__.client
bot = __main__.bot

# مخزن لحالة الألعاب الجارية
games = {}

def check_winner(board):
    # احتمالات الفوز (صفوف، أعمدة، أقطار)
    wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for w in wins:
        if board[w[0]] == board[w[1]] == board[w[2]] != " ":
            return board[w[0]]
    if " " not in board: return "تعادل"
    return None

@client.on(events.NewMessage(pattern=r"^\.xo$"))
async def start_xo(event):
    if not event.is_group: return await event.edit("❌ **عذراً، هذه اللعبة مخصصة للمجموعات فقط!**")
    
    reply = await event.get_reply_message()
    if not reply: return await event.edit("⚠️ **يجب الرد على الشخص الذي تريد تحديه!**")
    
    player1 = event.sender_id # صاحب الأمر
    player2 = reply.sender_id # الشخص المردود عليه
    
    if player1 == player2: return await event.edit("🤣 **لا يمكنك اللعب ضد نفسك!**")

    # اختيار من يبدأ ومن يأخذ X عشوائياً
    players = [player1, player2]
    random.shuffle(players)
    turn = players[0]
    
    game_id = f"{event.chat_id}_{event.id}"
    games[game_id] = {
        "p1": players[0], "p2": players[1],
        "turn": turn,
        "board": [" "] * 9,
        "marks": {players[0]: "❌", players[1]: "⭕"}
    }

    buttons = []
    for i in range(0, 9, 3):
        row = [Button.inline("⬜", data=f"xo_{game_id}_{j}") for j in range(i, i+3)]
        buttons.append(row)

    await event.delete()
    mention = f"[{ (await client.get_entity(turn)).first_name }](tg://user?id={turn})"
    await bot.send_message(event.chat_id, f"🎮 **تحدي XO جديد!**\n\nدور اللاعب: {mention}\nالعلامة: {games[game_id]['marks'][turn]}", buttons=buttons)

@bot.on(events.CallbackQuery(pattern=r"xo_(.*)"))
async def xo_callback(event):
    data = event.data.decode().split("_")
    game_id = f"{data[1]}_{data[2]}"
    index = int(data[3])
    
    if game_id not in games:
        return await event.answer("⚠️ هذه اللعبة قديمة، ابدأ واحدة جديدة!", alert=True)
    
    game = games[game_id]
    
    # التحقق من أن الشخص هو صاحب الدور
    if event.sender_id != game['turn']:
        if event.sender_id in [game['p1'], game['p2']]:
            return await event.answer("⏳ انتظر دورك يا بطل!", alert=True)
        else:
            return await event.answer("🚫 لست طرفاً في هذه اللعبة!", alert=True)

    # التحقق من أن المربع فارغ
    if game['board'][index] != " ":
        return await event.answer("❌ هذا المربع محجوز، اختر غيره!", alert=True)

    # تسجيل الحركة
    mark = game['marks'][event.sender_id]
    game['board'][index] = mark
    
    # تبديل الدور
    game['turn'] = game['p2'] if event.sender_id == game['p1'] else game['p1']
    
    # فحص الفوز أو التعادل
    winner_mark = check_winner(game['board'])
    
    # تحديث الأزرار
    buttons = []
    for i in range(0, 9, 3):
        row = [Button.inline(game['board'][j] if game['board'][j] != " " else "⬜", data=f"xo_{game_id}_{j}") for j in range(i, i+3)]
        buttons.append(row)

    if winner_mark:
        if winner_mark == "تعادل":
            result_text = "🤝 **النتيجة: تعادل! لا يوجد فائز.**"
        else:
            name = (await client.get_entity(event.sender_id)).first_name
            result_text = f"🎊 **مبروك للفائز: [{name}](tg://user?id={event.sender_id})**"
        
        del games[game_id] # حذف اللعبة بعد الانتهاء
        await event.edit(f"🎮 **انتهت لعبة XO!**\n\n{result_text}", buttons=buttons)
    else:
        next_player = game['turn']
        mention = f"[{ (await client.get_entity(next_player)).first_name }](tg://user?id={next_player})"
        await event.edit(f"🎮 **لعبة XO مستمرة...**\n\nدور اللاعب: {mention}\nالعلامة: {game['marks'][next_player]}", buttons=buttons)
