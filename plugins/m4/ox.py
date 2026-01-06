import __main__
from telethon import events, Button
import random

# استدعاء الحساب والبوت المساعد
client = __main__.client
bot = __main__.bot

# مخزن البيانات
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
            Button.inline(b[i] or " ", data=f"xo_{g_id}_{i}"),
            Button.inline(b[i+1] or " ", data=f"xo_{g_id}_{i+1}"),
            Button.inline(b[i+2] or " ", data=f"xo_{g_id}_{i+2}")
        ])
    btns.append([Button.inline("🏁 إنهاء اللعبة", data=f"xo_{g_id}_stop")])
    return btns

@client.on(events.NewMessage(pattern=r"^\.xo$"))
async def start_nethron_xo(event):
    if not event.out: return
    
    p1 = event.sender_id # أنت
    reply = await event.get_reply_message()
    
    if event.is_private:
        p2 = event.chat_id # الخصم في الخاص
    elif reply:
        p2 = reply.sender_id # الخصم في المجموعة
    else:
        return await event.edit("**⚠️ رد على الشخص لبدء التحدي!**")

    g_id = random.randint(100, 999)
    XO_DATA[g_id] = {
        'p1': p1, 'p2': p2,
        'board': [None]*9,
        'turn': p2, # الخصم يبدأ دائماً
        'sym': {p1: "⭕", p2: "❌"}
    }

    await event.delete() # حذف أمر الحساب الشخصي
    
    # جلب اسم الخصم لضمان ظهوره
    try:
        user = await client.get_entity(p2)
        p2_name = user.first_name
    except:
        p2_name = "الخصم"

    msg = (
        f"🎮 **تحدي X - O (نيثرون)**\n"
        f"★──────────★\n"
        f"👤 أنت: (⭕)\n"
        f"👤 {p2_name}: (❌)\n"
        f"★──────────★\n"
        f"🎲 دور: {p2_name}"
    )
    
    # الإرسال عبر البوت المساعد لتفعيل الأزرار
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

    if winner_sym:
        await event.edit(f"🎊 **مبروك الفوز للاعب ({winner_sym})!** 🏆", buttons=None)
        del XO_DATA[g_id]
        return
    elif None not in game['board']:
        await event.edit("🤝 **تعادل!** لا يوجد فائز.", buttons=None)
        del XO_DATA[g_id]
        return

    # تبديل الدور
    game['turn'] = game['p1'] if game['turn'] == game['p2'] else game['p2']
    
    # تحديث الرسالة
    await event.edit(
        f"🎮 **تحدي X - O مستمر**\n🎲 الدور الآن عند الطرف الآخر..",
        buttons=make_board(g_id)
    )
