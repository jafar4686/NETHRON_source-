from telethon import events, Button
import asyncio, random

client = __main__.client

giveaways = {}

# بدء مسابقة
@client.on(events.NewMessage(pattern=r"\.مسابقة (\d+) (.+)"))
async def giveaway(event):
    if not event.is_group:
        return

    time_sec = int(event.pattern_match.group(1))
    prize = event.pattern_match.group(2)

    msg = await event.reply(
        f"🎉 مسابقة جديدة!\n\n"
        f"🏆 الجائزة: {prize}\n"
        f"⏳ الوقت: {time_sec} ثانية\n\n"
        f"اضغط للمشاركة 👇",
        buttons=[Button.inline("🎟 مشاركة", b"join")]
    )

    giveaways[msg.id] = []

    await asyncio.sleep(time_sec)

    users = giveaways.get(msg.id, [])

    if not users:
        await msg.reply("❌ ماكو مشاركين")
        return

    winner = random.choice(users)

    await msg.reply(
        f"🎊 الفائز:\n"
        f"[{winner.first_name}](tg://user?id={winner.id})\n"
        f"🏆 {prize}"
    )

    del giveaways[msg.id]


# زر المشاركة
@client.on(events.CallbackQuery(data=b"join"))
async def join(event):
    uid = event.sender_id

    if event.message_id not in giveaways:
        return

    if uid not in giveaways[event.message_id]:
        giveaways[event.message_id].append(uid)
        await event.answer("تم الاشتراك ✅", alert=True)
    else:
        await event.answer("مشترك من قبل 😅", alert=True)

