import os, sys, asyncio, glob, importlib.util, __main__, subprocess, requests, re
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from config import api_id, api_hash

# إعدادات البوت (التوكن الخاص بك)
BOT_TOKEN = "8136996400:AAEO4uDFUweXXiz49bs91hI_jmvBqh8CStI"
SESSION_DB = "database.txt" 
OLD_SESSION_FILE = "session.session" 

bot = TelegramClient('MakerBot', api_id, api_hash).start(bot_token=BOT_TOKEN)

# --- [ محرك التحميل الذكي المدمج ] ---
def get_url(text):
    urls = re.findall(r'(https?://\S+)', text)
    for url in urls:
        if any(x in url for x in ["youtube.com", "youtu.be", "tiktok.com"]):
            return url
    return None

@bot.on(events.NewMessage)
async def assistant_downloader(event):
    # البوت يستجيب للروابط في الخاص أو المحولة له
    url = get_url(event.text)
    if not url: return

    # تحميل تيك توك (منطق ملفك bot4.py)
    if "tiktok.com" in url:
        try:
            res = requests.get(f"https://www.tikwm.com/api/?url={url}").json()
            if res.get('code') == 0:
                v_url = res['data']['play']
                if v_url.startswith('//'): v_url = 'https:' + v_url
                await bot.send_file(event.chat_id, v_url, caption=f"📱 `{res['data'].get('title')}`")
        except: pass

    # تحميل يوتيوب (تخطى Sign in و 403)
    elif "youtube" in url or "youtu.be" in url:
        try:
            # استخدام API خارجي لتجاوز حماية يوتيوب
            payload = {"url": url, "vQuality": "720"}
            res = requests.post("https://co.wuk.sh/api/json", json=payload, headers={"Accept": "application/json"}).json()
            if res.get('url'):
                await bot.send_file(event.chat_id, res['url'], caption="🎬 **تم التحميل بنجاح (نيثرون)**")
        except:
            await event.reply("❌ يوتيوب فرض حماية قوية حالياً، جرب لاحقاً.")

# --- [ بقية كود الميكر الأصلي ] ---
async def load_plugins(user_client):
    __main__.client = user_client
    files = glob.glob("plugins/**/*.py", recursive=True)
    for f in files:
        if f.endswith("__init__.py"): continue
        name = os.path.basename(f)[:-3]
        try:
            spec = importlib.util.spec_from_file_location(name, f)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except: pass

async def start_all_accounts():
    if os.path.exists(SESSION_DB):
        with open(SESSION_DB, "r") as f:
            for s in f.readlines():
                s = s.strip()
                if s:
                    try:
                        c = TelegramClient(StringSession(s), api_id, api_hash)
                        await c.connect()
                        if await c.is_user_authorized():
                            await load_plugins(c)
                            asyncio.create_task(c.run_until_disconnected())
                    except: pass

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    buttons = [[Button.inline("➕ إضافة حساب", data="add_acc")], [Button.inline("🔄 إعادة تشغيل", data="restart")]]
    await event.respond("☭ **لوحة تحكم نيثرون والتحميل** ☭", buttons=buttons)

@bot.on(events.CallbackQuery)
async def callback(event):
    data = event.data.decode('utf-8')
    if data == "restart":
        os.execl(sys.executable, sys.executable, *sys.argv)
    elif data == "add_acc":
        # (كود إضافة الحساب كما هو لديك)
        pass

loop = asyncio.get_event_loop()
loop.create_task(start_all_accounts())
print("🚀 المساعد والتحميل قيد التشغيل...")
bot.run_until_disconnected()
