import __main__
from telethon import events, Button
import random
import asyncio

# استدعاء الكلاينت (حسابك) والبوت (المساعد)
client = __main__.client
bot = __main__.bot

# مخزن بيانات اللعبة
XO_GAMES = {}

# ==========================================
# دالة بناء اللوحة (بإيموجيات المربعات)
# ==========================================
def build_board(game_id):
    game = XO_GAMES[game_id]
    b = game['board']
    buttons = []
    for i in range(0, 9, 3):
        buttons.append([
            Button.inline(b[i] or "⬜", data=f"xo_{game_id}_{i}"),
            Button.inline(b[i+1] or "⬜", data=f"xo_{game_id}_{i+1}"),
            Button.inline(b[i+2] or "⬜", data=f"xo_{game_id}_{i+2}")
        ])
    buttons.append([Button.inline("🏁 إنهاء اللعبة", data=f"xo_{game_id}_stop")])
    return buttons

# ==========================================
# دالة فحص الفائز
# ==========================================
def check_winner(board):
    win_sets = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for s in win_sets:
        if board[s[0]] == board[s[1]] == board[s[2]] and board[s[0]] is not None:
            return board[s[0]]
    if None not in board: return "draw"
    return None

# ==========================================
# أمر بدء اللعبة (.xo) بالرد
# ==========================================
@client.on(events.NewMessage(pattern=r"^\.xo$"))
async def start_xo(event):
    if not event.out: return
    
    reply = await event.get_reply_message()
    if not reply:
        return await event.edit("**⚠️ يجب الرد على الشخص الذي تريد تحديه!**")

    p1 = event.sender_id # أنت
    p2 = reply.sender_id # الخصم
    
    if p1 == p2:
        return await event.edit("**⚠️ لا يمكنك تحدي نفسك!**")

    # اختيار عشوائي للعلامات
    symbols = ["❌", "⭕"]
    random.shuffle(symbols)
    p1_sym = symbols[0]
    p2_sym = symbols[1]

    game_id = random.randint(1000, 9999)
    XO_GAMES[game_id] = {
        'p1': p1, 'p2': p2,
        'board': [None] * 9,
        'turn': p2, # الخصم يبدأ دائماً لتجنب مشاكل استجابة البوت
        'sym': {p1: p1_sym, p2: p2_sym}
    }

    await event.delete()
    
    # جلب أسماء اللاعبين
    try:
        u1 = await client.get_entity(p1)
        u2 = await client.get_entity(p2)
        n1, n2 = u1.first_name, u2.first_name
    except:
        n1, n2 = "اللاعب 1", "اللاعب 2"

    msg = (
        f"🎮 **تحدي X - O جديد**\n"
        f"★──────────★\n"
        f"👤 {n1} ← ({p1_sym})\n"
        f"👤 {n2} ← ({p2_sym})\n"
        f"★──────────★\n"
        f"🎲 الدور عند: {n2}"
    )

    # الإرسال عبر البوت المساعد
    await bot.send_message(event.chat_id, msg, buttons=build_board(game_id))

# ==========================================
# معالج ضغطات الأزرار (عبر البوت المساعد)
# ==========================================
@bot.on(events.CallbackQuery(pattern=r"xo_(\d+)_(\d+|stop)"))
async def xo_callback(event):
    g_id = int(event.pattern_match.group(1))
    act = event.pattern_match.group(2)
    
    if g_id not in XO_GAMES:
        return await event.answer("⚠️ اللعبة انتهت أو غير موجودة!", alert=True)

    game = XO_GAMES[g_id]

    # 1. منع الغرباء (السماح فقط للطرفين)
    if event.sender_id not in [game['p1'], game['p2']]:
        return await event.answer("❌ هذا التحدي ليس لك! ابدأ تحديك الخاص بـ .xo", alert=True)

    # 2. إنهاء اللعبة
    if act == "stop":
        del XO_GAMES[g_id]
        return await event.edit("❌ تم إنهاء اللعبة من قبل أحد اللاعبين.")

    # 3. التحقق من الدور
    if event.sender_id != game['turn']:
        return await event.answer("⏳ انتظر دور خصمك!", alert=True)

    pos = int(act)
    if game['board'][pos] is not None:
        return await event.answer("🚫 هذا المربع مشغول!", alert=True)

    # 4. تنفيذ الحركة
    current_sym = game['sym'][event.sender_id]
    game['board'][pos] = current_sym
    
    # 5. فحص النتيجة
    res = check_winner(game['board'])
    if res:
        if res == "draw":
            await event.edit("🤝 **تعادل!** انتهت اللعبة بدون فائز.", buttons=None)
        else:
            winner_name = "أنت" if event.sender_id == game['p1'] else "الخصم"
            # محاولة جلب الاسم الحقيقي للفائز
            try:
                user = await bot.get_entity(event.sender_id)
                winner_name = user.first_name
            except: pass
            await event.edit(f"🎊 **مبروك الفوز لـ {winner_name}!** ({res}) 🏆", buttons=None)
        
        del XO_GAMES[g_id]
        return

    # 6. تبديل الدور
    game['turn'] = game['p1'] if game['turn'] == game['p2'] else game['p2']
    try:
        next_user = await bot.get_entity(game['turn'])
        next_name = next_user.first_name
    except:
        next_name = "الطرف الآخر"

    await event.edit(
        f"🎮 **تحدي X - O مستمر**\n🎲 الدور الآن عند: {next_name}",
        buttons=build_board(g_id)
    )
