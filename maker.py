from telethon import TelegramClient, events
import requests
import re

# بيانات البوت الجديد
API_ID = 24789364
API_HASH = "deb58602a303b3440fdc227975ce90ea"
BOT_TOKEN = "@taltbatbot"

bot = TelegramClient('new_downloader', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def get_url(text):
    urls = re.findall(r'(https?://\S+)', text)
    for url in urls:
        if any(x in url for x in ["youtube.com", "youtu.be", "tiktok.com"]):
            return url
    return None

@bot.on(events.NewMessage)
async def dl_handler(event):
    url = get_url(event.text)
    if not url: return
    
    chat = event.chat_id
    # يوتيوب - تجاوز حظر Sign in
    if "youtube" in url or "youtu.be" in url:
        try:
            res = requests.post("https://co.wuk.sh/api/json", 
                               json={"url": url, "vQuality": "720"}, 
                               headers={"Accept": "application/json"}).json()
            if res.get('url'):
                await bot.send_file(chat, res['url'], caption="🎬 **تم التحميل بنجاح (نيثرون)**")
        except: pass

    # تيك توك - منطق bot4.py
    elif "tiktok.com" in url:
        try:
            res = requests.get(f"https://www.tikwm.com/api/?url={url}").json()
            if res.get('code') == 0:
                v_url = res['data']['play']
                if v_url.startswith('//'): v_url = 'https:' + v_url
                await bot.send_file(chat, v_url, caption=f"📱 `{res['data'].get('title')}`")
        except: pass

print("🚀 بوت التحميل الجديد شغال...")
bot.run_until_disconnected()
