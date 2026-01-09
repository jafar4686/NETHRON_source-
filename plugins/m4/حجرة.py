import __main__
from telethon import events, Button
import random

client = __main__.client
bot = __main__.bot

# مخزن لتحديات الأشخاص
rps_games = {}
tools = {"rock": "💎 حجرة", "paper": "📄 ورقة", "scissors": "✂️ مقص"}

@client.on(events.NewMessage(pattern=r"^\.حومص$"))
async def start_rps(event):
    reply = await event.get_reply_message()
    p1 = event.sender_id
    p2 = reply.sender_id if reply else "BOT"

    if p1 == p2:
        return await event.edit("❌ **لا يمكنك تحدي نفسك!**")

    game_id = f"{event.chat_id}_{event.id}"
    
    # تنسيق الرسالة حسب نوع اللعب
    if p2 == "BOT":
        msg = "★────────☭────────★\n🕹 **تحدي (حجرة-ورقة-مقص) ضد البوت**\n\nاختر سلاحك الآن:\n★────────☭────────★"
    else:
        p2_name = (await client.get_entity(p2)).first_name
        msg = f"★────────☭────────★\n🕹 **تحدي (حجرة-ورقة-مقص)**\n\n👤 **المتحدي الأول:** أنت\n👤 **المتحدي الثاني:** {p2_name}\n\nبانتظار اختياركما (الاختيارات سرية 🤐)\n★────────☭────────★"

    rps_games[game_id] = {"p1": p1, "p2": p2, "p1_choice": None, "p2_choice": None}

    buttons = [
        [Button.inline("💎 حجرة", data=f"rps_{game_id}_rock"), Button.inline("📄 ورقة", data=f"rps_{game_id}_paper")],
        [Button.inline("✂️ مقص", data=f"rps_{game_id}_scissors")]
    ]
    
    await event.delete()
    await bot.send_message(event.chat_id, msg, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=r"rps_(.*)"))
async def rps_callback(event):
    data = event.data.decode().split("_")
    game_id = f"{data[1]}_{data[2]}"
    choice = data[3]

    if game_id not in rps_games:
        return await event.answer("⚠️ التحدي قديم!", alert=True)

    game = rps_games[game_id]

    # منع التطفل
    if event.sender_id != game['p1'] and (game['p2'] != "BOT" and event.sender_id != game['p2']):
        return await event.answer("🚫 لست طرفاً في هذا التحدي!", alert=True)

    # إذا كان ضد البوت
    if game['p2'] == "BOT":
        bot_choice = random.choice(list(tools.keys()))
        await finish_rps(event, game_id, choice, bot_choice, is_bot=True)
        return

    # إذا كان ضد شخص (تسجيل الاختيارات)
    if event.sender_id == game['p1']:
        if game['p1_choice']: return await event.answer("✅ اخترت سابقاً، انتظر خصمك!", alert=True)
        game['p1_choice'] = choice
        await event.answer("✅ تم تسجيل اختيارك سراً!", alert=True)
    else:
        if game['p2_choice']: return await event.answer("✅ اخترت سابقاً، انتظر خصمك!", alert=True)
        game['p2_choice'] = choice
        await event.answer("✅ تم تسجيل اختيارك سراً!", alert=True)

    # إذا اختار الشخصين، نعلن النتيجة
    if game['p1_choice'] and game['p2_choice']:
        await finish_rps(event, game_id, game['p1_choice'], game['p2_choice'], is_bot=False)

async def finish_rps(event, game_id, c1, c2, is_bot):
    game = rps_games[game_id]
    
    def get_win(a, b):
        if a == b: return "تعادل"
        if (a == "rock" and b == "scissors") or (a == "paper" and b == "rock") or (a == "scissors" and b == "paper"):
            return "p1"
        return "p2"

    winner = get_win(c1, c2)
    p1_name = "أنت"
    p2_name = "البوت 🤖" if is_bot else (await client.get_entity(game['p2'])).first_name

    if winner == "تعادل":
        res_text = "🤝 **النتيجة: تعادل!**"
    elif winner == "p1":
        res_text = f"🎊 **الفائز هو: {p1_name}**"
    else:
        res_text = f"🎊 **الفائز هو: {p2_name}**"

    final_msg = (
        "★────────☭────────★\n"
        "🏁 **خاتمة تحدي (حومص)**\n\n"
        f"👤 {p1_name}: {tools[c1]}\n"
        f"👤 {p2_name}: {tools[c2]}\n\n"
        f"📝 {res_text}\n"
        "★────────☭────────★"
    )
    
    if game_id in rps_games: del rps_games[game_id]
    await event.edit(final_msg)
