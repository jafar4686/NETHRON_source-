import __main__
from telethon import events, Button
import random
import asyncio

client = __main__.client
bot = __main__.bot

games = {}

# التنسيق الموحد للسورس
HEADER = "★────────☭────────★\n"

def check_winner(board):
    wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for w in wins:
        if board[w[0]] == board[w[1]] == board[w[2]] != " ":
            return board[w[0]]
    if " " not in board: return "تعادل"
    return None

def update_buttons(game, game_id):
    buttons = []
    for i in range(0, 9, 3):
        row = [Button.inline(game['board'][j] if game['board'][j] != " " else "⬜", data=f"xo_{game_id}_{j}") for j in range(i, i+3)]
        buttons.append(row)
    return buttons

@client.on(events.NewMessage(pattern=r"^\.xo$"))
async def start_xo(event):
    reply = await event.get_reply_message()
    player1 = event.sender_id
    player2 = reply.sender_id if reply else "BOT" 
    
    if player1 == player2:
        return await event.edit("❌ **لا يمكنك اللعب ضد نفسك!**")

    game_id = f"{event.chat_id}_{event.id}"
    await event.delete()
    await setup_game(event.chat_id, game_id, player1, player2)

async def setup_game(chat_id, game_id, p1, p2, edit_msg=None):
    # جلب الأسماء
    p1_name = (await client.get_entity(p1)).first_name
    p2_name = "البوت 🤖" if p2 == "BOT" else (await client.get_entity(p2)).first_name

    games[game_id] = {
        "p1": p1, "p2": p2,
        "p1_name": p1_name, "p2_name": p2_name,
        "turn": p1,
        "board": [" "] * 9,
        "marks": {p1: "❌", p2: "⭕"}
    }

    buttons = update_buttons(games[game_id], game_id)
    msg = (
        f"{HEADER}"
        f"🎮 **تحدي XO (نيثرون)**\n"
        f"👤 **الخصم:** {p2_name}\n"
        f"⏳ **الدور عند:** {p1_name} (❌)\n"
        f"{HEADER}"
    )
    
    if edit_msg:
        await edit_msg.edit(msg, buttons=buttons)
    else:
        await bot.send_message(chat_id, msg, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=r"xo_(.*)"))
async def xo_callback(event):
    data = event.data.decode().split("_")
    
    # معالجة زر إعادة اللعب
    if data[1] == "retry":
        old_game_id = f"{data[2]}_{data[3]}"
        if old_game_id not in games: return await event.answer("⚠️ حدث خطأ!")
        g = games[old_game_id]
        # إعادة تشغيل اللعبة بنفس الخصوم
        await event.answer("🔄 جارِ بدء جولة جديدة بنفس الخصم...", alert=False)
        await setup_game(event.chat_id, old_game_id, g['p1'], g['p2'], edit_msg=event)
        return

    game_id = f"{data[1]}_{data[2]}"
    index = int(data[3])
    
    if game_id not in games: return await event.answer("⚠️ اللعبة انتهت!")
    game = games[game_id]
    
    if event.sender_id != game['turn']:
        return await event.answer("🚫 ليس دورك الآن!", alert=True)
    if game['board'][index] != " ":
        return await event.answer("❌ المربع مشغول!", alert=True)

    # حركة اللاعب
    game['board'][index] = game['marks'][event.sender_id]
    res = check_winner(game['board'])
    if res: return await finish_game(event, game, game_id, res)

    # ذكاء البوت أو تبديل الأدوار
    if game['p2'] == "BOT":
        empty = [i for i, v in enumerate(game['board']) if v == " "]
        if empty:
            game['board'][random.choice(empty)] = "⭕"
            res = check_winner(game['board'])
            if res: return await finish_game(event, game, game_id, res)
        current_name = game['p1_name']
    else:
        game['turn'] = game['p2'] if event.sender_id == game['p1'] else game['p1']
        current_name = game['p2_name'] if game['turn'] == game['p2'] else game['p1_name']

    buttons = update_buttons(game, game_id)
    mark = game['marks'][game['turn']]
    await event.edit(
        f"{HEADER}"
        f"🎮 **تحدي XO مستمر..**\n"
        f"👤 **الخصم:** {game['p2_name']}\n"
        f"⏳ **الدور الآن:** {current_name} ({mark})\n"
        f"{HEADER}", 
        buttons=buttons
    )

async def finish_game(event, game, game_id, result):
    buttons = update_buttons(game, game_id)
    # إضافة زر إعادة اللعب أسفل اللوحة المنتهية
    retry_button = [Button.inline("🔄 جولة جديدة بنفس الخصم", data=f"xo_retry_{game_id}")]
    buttons.append(retry_button)

    if result == "تعادل":
        txt = "🤝 **النتيجة: تعادل مستحق!**"
    elif result == "⭕" and game['p2'] == "BOT":
        txt = "🤖 **لأسف! البوت هزُمك هذه المرة.**"
    else:
        winner = game['p1_name'] if result == "❌" else game['p2_name']
        txt = f"🎊 **الفائز:** {winner} (البطل! 🏆)"
    
    await event.edit(
        f"{HEADER}"
        f"🏁 **انتهت اللعبة**\n"
        f"📝 {txt}\n"
        f"{HEADER}", 
        buttons=buttons
    )
