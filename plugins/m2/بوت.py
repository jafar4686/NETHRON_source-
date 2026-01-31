from telethon import TelegramClient, events, Button

# ذني لازم موجودات بكل ملف يشتغل على تليجرام، بدونهن صدك يلطم الكود!
API_ID = 21743603 
API_HASH = "61e38933224b7496181f26710787e682"
BOT_TOKEN = "8579454046:AAGn52vlNAwQzaRx-ABWfMnBTppv1ckmCds"

# هنا يشتغل "كبل" بس تعطي أمر التشغيل
bot = TelegramClient('CompBotSession', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("✅ شغال بدون تسجيل وبدون دوخة رقم!")

bot.run_until_disconnected()
