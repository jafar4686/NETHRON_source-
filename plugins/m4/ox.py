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

async def get_user_name(user_id):
    """جلب اسم المستخدم"""
    try:
        user = await client.get_entity(user_id)
        return user.first_name if user.first_name else f"المستخدم {user_id}"
    except:
        try:
            user = await bot.get_entity(user_id)
            return user.first_name if user.first_name else f"المستخدم {user_id}"
        except:
            return f"المستخدم {user_id}"

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

    g_id = random.randint(1000, 9999)
    
    # جلب الأسماء
    p1_name = await get_user_name(p1)
    p2_name = await get_user_name(p2)
    
    # اختيار عشوائي لمن يبدأ
    starter = random.choice([p1, p2])
    
    XO_DATA[g_id] = {
        'p1': p1, 
        'p2': p2,
        'p1_name': p1_name,
        'p2_name': p2_name,
        'board': [None]*9,
        'turn': starter,
        'sym': {p1: "⭕", p2: "❌"},
        'message_id': None,
        'chat_id': event.chat_id
    }

    await event.delete()
    
    # تحديد من صاحب الدور الحالي
    if starter == p1:
        current_turn = f"{p1_name} (⭕)"
        turn_symbol = "⭕"
    else:
        current_turn = f"{p2_name} (❌)"
        turn_symbol = "❌"

    msg = (
        f"🎮 **تحدي X - O (نيثرون)**\n"
        f"★──────────★\n"
        f"👤 اللاعب 1: {p1_name} (⭕)\n"
        f"👤 اللاعب 2: {p2_name} (❌)\n"
        f"★──────────★\n"
        f"🎲 **دور:** {current_turn}\n"
        f"📍 اضغط على المربعات للعب"
    )
    
    # إرسال الرسالة عبر البوت المساعد
    sent = await bot.send_message(event.chat_id, msg, buttons=make_board(g_id))
    XO_DATA[g_id]['message_id'] = sent.id
    XO_DATA[g_id]['chat_id'] = event.chat_id

# معالج ضغطات الأزرار للحساب الشخصي
@client.on(events.CallbackQuery(pattern=r"xo_(\d+)_(\d+|stop)"))
async def xo_engine_client(event):
    """معالج الأزرار للحساب الشخصي"""
    await handle_xo_callback(event, client)

# معالج ضغطات الأزرار للبوت المساعد
@bot.on(events.CallbackQuery(pattern=r"xo_(\d+)_(\d+|stop)"))
async def xo_engine_bot(event):
    """معالج الأزرار للبوت المساعد"""
    await handle_xo_callback(event, bot)

async def handle_xo_callback(event, source_client):
    """دالة موحدة لمعالجة الأزرار"""
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
        await event.edit("❌ تم إلغاء اللعبة.")
        return

    # التحقق من الدور
    if event.sender_id != game['turn']:
        return await event.answer("⏳ مو دورك، انتظر الخصم!", alert=True)

    pos = int(act)
    if game['board'][pos] is not None:
        return await event.answer("🚫 المكان محجوز!", alert=True)

    # تنفيذ الحركة
    symbol = game['sym'][event.sender_id]
    game['board'][pos] = symbol
    
    # فحص الفوز
    win_sets = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    winner = None
    
    for s in win_sets:
        if game['board'][s[0]] == game['board'][s[1]] == game['board'][s[2]] and game['board'][s[0]]:
            # تحديد الفائز
            if game['board'][s[0]] == "⭕":
                winner = game['p1']
                winner_name = game['p1_name']
            else:
                winner = game['p2']
                winner_name = game['p2_name']
            break

    if winner is not None:
        # عرض اللوحة النهائية
        board_text = ""
        for i in range(0, 9, 3):
            row = []
            for j in range(3):
                cell = game['board'][i+j]
                row.append(cell if cell else "⬜")
            board_text += " ".join(row) + "\n"
        
        final_msg = (
            f"🎊 **مبروك الفوز!** 🏆\n"
            f"👑 الفائز: {winner_name} ({game['sym'][winner]})\n\n"
            f"📊 اللوحة النهائية:\n{board_text}"
        )
        
        try:
            # محاولة تحديث الرسالة الأصلية
            await source_client.edit_message(
                game['chat_id'],
                game['message_id'],
                final_msg,
                buttons=None
            )
        except:
            # إذا فشل، الرد على الرسالة الحالية
            await event.edit(final_msg, buttons=None)
        
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
        
        final_msg = (
            f"🤝 **تعادل!** لا يوجد فائز.\n\n"
            f"📊 اللوحة النهائية:\n{board_text}"
        )
        
        try:
            await source_client.edit_message(
                game['chat_id'],
                game['message_id'],
                final_msg,
                buttons=None
            )
        except:
            await event.edit(final_msg, buttons=None)
        
        del XO_DATA[g_id]
        return

    # تبديل الدور
    game['turn'] = game['p1'] if game['turn'] == game['p2'] else game['p2']
    
    # تحديث الرسالة
    if game['turn'] == game['p1']:
        current_turn = f"{game['p1_name']} (⭕)"
    else:
        current_turn = f"{game['p2_name']} (❌)"
    
    updated_msg = (
        f"🎮 **تحدي X - O (نيثرون)**\n"
        f"★──────────★\n"
        f"👤 اللاعب 1: {game['p1_name']} (⭕)\n"
        f"👤 اللاعب 2: {game['p2_name']} (❌)\n"
        f"★──────────★\n"
        f"🎲 **دور:** {current_turn}"
    )
    
    try:
        await source_client.edit_message(
            game['chat_id'],
            game['message_id'],
            updated_msg,
            buttons=make_board(g_id)
        )
        await event.answer("✓ تم تحديث اللعبة", alert=False)
    except Exception as e:
        await event.answer(f"⚠️ حدث خطأ: {str(e)}", alert=True)

# معالج للأوامر الخاصة بالنظافة
@client.on(events.NewMessage(pattern=r"^\.xo_clean$"))
async def xo_clean(event):
    """تنظيف جميع جلسات XO"""
    if not event.out: return
    XO_DATA.clear()
    await event.edit("✅ تم تنظيف جميع جلسات XO")

# معالج للأوامر لعرض الجلسات النشطة
@client.on(events.NewMessage(pattern=r"^\.xo_sessions$"))
async def xo_sessions(event):
    """عرض الجلسات النشطة"""
    if not event.out: return
    if not XO_DATA:
        await event.edit("📭 لا توجد جلسات XO نشطة")
        return
    
    sessions_text = "🎮 **الجلسات النشطة:**\n\n"
    for g_id, game in XO_DATA.items():
        sessions_text += f"**ID:** {g_id}\n"
        sessions_text += f"👤 {game['p1_name']} vs {game['p2_name']}\n"
        sessions_text += f"🎲 الدور: {'اللاعب 1' if game['turn'] == game['p1'] else 'اللاعب 2'}\n"
        sessions_text += "─" * 30 + "\n"
    
    await event.edit(sessions_text)
