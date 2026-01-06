import __main__
from telethon import events, Button
import random
import asyncio

client = __main__.client
bot = __main__.bot

XO_DATA = {}

# ==========================================
# 1. قائمة الأوامر .م4
# ==========================================
@client.on(events.NewMessage(pattern=r"^\.م4$"))
async def m4_list(event):
    if not event.out: return
    text = (
        "★────────☭────────★\n"
        "   ☭ • 𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 • ☭\n"
        "★────────☭────────★\n\n"
        "🎮 **أوامر الألعاب والتسلية:**\n\n"
        "• `.xo` • لبدء تحدي إكس أو\n"
        "• `.تفكيك` • لعبة تفكيك الكلمات\n"
        "• `.كت تويت` • أسئلة جريئة\n\n"
        "★──────────☭──────────★"
    )
    await event.edit(text)

# ==========================================
# 2. برمجة X-O بنظام التعريف المباشر
# ==========================================

def make_board(g_id):
    game = XO_DATA[g_id]
    b = game['board']
    btns = []
    for i in range(0, 9, 3):
        btns.append([
            Button.inline(b[i] if b[i] is not None else "⬜", data=f"xo_{g_id}_{i}"),
            Button.inline(b[i+1] if b[i+1] is not None else "⬜", data=f"xo_{g_id}_{i+1}"),
            Button.inline(b[i+2] if b[i+2] is not None else "⬜", data=f"xo_{g_id}_{i+2}")
        ])
    btns.append([Button.inline("🏁 إنهاء اللعبة", data=f"xo_{g_id}_stop")])
    return btns

def get_game_status(game, current_player_id=None):
    """الحصول على حالة اللعبة مع تحديد الدور"""
    p1_id = game['p1']
    p2_id = game['p2']
    
    # محاولة جلب الأسماء
    async def get_name(user_id):
        try:
            user = await client.get_entity(user_id)
            return user.first_name if user.first_name else f"المستخدم {user_id}"
        except:
            return f"المستخدم {user_id}"
    
    # تحديد من صاحب الدور الحالي
    if game['turn'] == p1_id:
        turn_name = "اللاعب 1 (⭕)"
    else:
        turn_name = "اللاعب 2 (❌)"
    
    return turn_name

@client.on(events.NewMessage(pattern=r"^\.xo$"))
async def start_nethron_xo(event):
    if not event.out: return
    
    p1 = event.sender_id
    reply = await event.get_reply_message()
    
    if event.is_private:
        p2 = event.chat_id
    elif reply:
        p2 = reply.sender_id
    else:
        return await event.edit("**⚠️ رد على الشخص لبدء التحدي!**")

    # التأكد من أن المستخدم لا يلعب مع نفسه
    if p1 == p2:
        return await event.edit("**⚠️ لا يمكنك اللعب مع نفسك!**")

    g_id = random.randint(100, 999)
    
    # جلب الأسماء
    try:
        user1 = await client.get_entity(p1)
        p1_name = user1.first_name if user1.first_name else f"المستخدم {p1}"
    except:
        p1_name = f"المستخدم {p1}"
    
    try:
        user2 = await client.get_entity(p2)
        p2_name = user2.first_name if user2.first_name else f"المستخدم {p2}"
    except:
        p2_name = f"المستخدم {p2}"
    
    # اختيار عشوائي لمن يبدأ
    starter = random.choice([p1, p2])
    
    XO_DATA[g_id] = {
        'p1': p1, 
        'p2': p2,
        'p1_name': p1_name,
        'p2_name': p2_name,
        'board': [None]*9,
        'turn': starter, # يبدأ عشوائياً
        'sym': {p1: "⭕", p2: "❌"}
    }

    await event.delete()
    
    # تحديد من صاحب الدور الحالي
    if starter == p1:
        current_turn = p1_name + " (⭕)"
    else:
        current_turn = p2_name + " (❌)"

    msg = (
        f"🎮 **تحدي X - O (نيثرون)**\n"
        f"★──────────★\n"
        f"👤 اللاعب 1: {p1_name} (⭕)\n"
        f"👤 اللاعب 2: {p2_name} (❌)\n"
        f"★──────────★\n"
        f"🎲 **دور:** {current_turn}\n"
        f"📍 اضغط على المربعات للعب"
    )
    
    await bot.send_message(event.chat_id, msg, buttons=make_board(g_id))

@bot.on(events.CallbackQuery(pattern=r"xo_(\d+)_(\d+|stop)"))
async def xo_engine(event):
    g_id = int(event.pattern_match.group(1))
    act = event.pattern_match.group(2)
    
    if g_id not in XO_DATA:
        return await event.answer("⚠️ انتهت الجلسة!", alert=True)

    game = XO_DATA[g_id]

    # منع الغرباء
    if event.sender_id not in [game['p1'], game['p2']]:
        return await event.answer("❌ التحدي مو إلك!", alert=True)

    if act == "stop":
        del XO_DATA[g_id]
        return await event.edit("❌ تم إلغاء اللعبة.")

    # التحقق من الدور
    if event.sender_id != game['turn']:
        return await event.answer("⏳ مو دورك، انتظر الخصم!", alert=True)

    pos = int(act)
    if game['board'][pos] is not None:
        return await event.answer("🚫 المكان محجوز!", alert=True)

    # تنفيذ الحركة
    game['board'][pos] = game['sym'][event.sender_id]
    
    # فحص الفوز
    win_sets = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    winner_sym = None
    for s in win_sets:
        if game['board'][s[0]] == game['board'][s[1]] == game['board'][s[2]] and game['board'][s[0]]:
            winner_sym = game['board'][s[0]]
            break

    if winner_sym:
        # تحديد الفائز
        if winner_sym == "⭕":
            winner_name = game['p1_name']
        else:
            winner_name = game['p2_name']
        
        # عرض اللوحة النهائية
        board_text = ""
        for i in range(0, 9, 3):
            row = []
            for j in range(3):
                cell = game['board'][i+j]
                row.append(cell if cell else "⬜")
            board_text += " ".join(row) + "\n"
        
        await event.edit(
            f"🎊 **مبروك الفوز!** 🏆\n"
            f"👑 الفائز: {winner_name} ({winner_sym})\n\n"
            f"📊 اللوحة النهائية:\n{board_text}",
            buttons=None
        )
        del XO_DATA[g_id]
        return
        
    elif None not in game['board']:
        board_text = ""
        for i in range(0, 9, 3):
            row = []
            for j in range(3):
                cell = game['board'][i+j]
                row.append(cell if cell else "⬜")
            board_text += " ".join(row) + "\n"
        
        await event.edit(
            f"🤝 **تعادل!** لا يوجد فائز.\n\n"
            f"📊 اللوحة النهائية:\n{board_text}",
            buttons=None
        )
        del XO_DATA[g_id]
        return

    # تبديل الدور
    game['turn'] = game['p1'] if game['turn'] == game['p2'] else game['p2']
    
    # تحديث الرسالة مع تحديد صاحب الدور
    if game['turn'] == game['p1']:
        current_turn = game['p1_name'] + " (⭕)"
    else:
        current_turn = game['p2_name'] + " (❌)"
    
    await event.edit(
        f"🎮 **تحدي X - O (نيثرون)**\n"
        f"★──────────★\n"
        f"👤 اللاعب 1: {game['p1_name']} (⭕)\n"
        f"👤 اللاعب 2: {game['p2_name']} (❌)\n"
        f"★──────────★\n"
        f"🎲 **دور:** {current_turn}",
        buttons=make_board(g_id)
    )
