import os, sys, asyncio, glob, importlib.util, __main__, subprocess, requests, re, yt_dlp
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from config import api_id, api_hash

# إعدادات البوت والمجلدات
BOT_TOKEN = "8136996400:AAEO4uDFUweXXiz49bs91hI_jmvBqh8CStI"
SESSION_DB = "database.txt" 
OLD_SESSION_FILE = "session.session" 

bot = TelegramClient('MakerBot', api_id, api_hash).start(bot_token=BOT_TOKEN)

if not hasattr(__main__, 'active_sessions'):
    __main__.active_sessions = {}

# --- [ قسم محرك التحميل المضاف ] ---
def get_url(text):
    urls = re.findall(r'(https?://\S+)', text)
    for url in urls:
        if any(x in url for x in ["youtube.com", "youtu.be", "tiktok.com"]):
            return url
    return None

@bot.on(events.NewMessage)
async def assistant_downloader(event):
    if event.is_private:
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

        # تحميل يوتيوب (تخطى 403 عبر محرك Cobalt)
        elif "youtube" in url or "youtu.be" in url:
            try:
                payload = {"url": url, "vQuality": "720"}
                res = requests.post("https://co.wuk.sh/api/json", json=payload, headers={"Accept": "application/json"}).json()
                if res.get('url'):
                    await bot.send_file(event.chat_id, res['url'], caption="🎬 **تم التحميل بواسطة محرك نيثرون**")
            except:
                # محاولة ثانية إذا فشل الأول
                try:
                    with yt_dlp.YoutubeDL({'format': 'best', 'quiet': True}) as ydl:
                        info = ydl.extract_info(url, download=False)
                        await bot.send_file(event.chat_id, info['url'], caption=f"🎬 {info['title']}")
                except: pass
# --- [ نهاية قسم التحميل ] ---

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
        except Exception as e: print(f"❌ Error loading {name}: {e}")

async def start_all_accounts():
    if os.path.exists(OLD_SESSION_FILE):
        try:
            c = TelegramClient("session", api_id, api_hash)
            await c.connect()
            if await c.is_user_authorized():
                await load_plugins(c)
                asyncio.create_task(c.run_until_disconnected())
        except Exception as e: print(f"⚠️ فشل تشغيل ملف الجلسة: {e}")

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
                    except Exception as e: print(f"⚠️ فشل سيزون نصي: {e}")

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    buttons = [
        [Button.inline("➕ إضافة حساب (رقم)", data="add_acc")],
        [Button.inline("🔄 تحديث السورس وإعادة تشغيل", data="restart")],
        [Button.inline("📊 إحصائيات", data="stats")]
    ]
    await event.respond("☭ **مرحباً بك في لوحة تحكم نيثرون** ☭", buttons=buttons)

@bot.on(events.CallbackQuery)
async def callback(event):
    data = event.data.decode('utf-8')
    if data == "add_acc":
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("📱 أرسل الرقم مع رمز الدولة:")
            p_res = await conv.get_response()
            phone = p_res.text.replace(" ", "")
            client = TelegramClient(StringSession(), api_id, api_hash)
            await client.connect()
            try:
                await client.send_code_request(phone)
                await conv.send_message("📥 أرسل الكود:")
                c_res = await conv.get_response()
                await client.sign_in(phone, c_res.text)
                with open(SESSION_DB, "a") as f:
                    f.write(client.session.save() + "\n")
                await conv.send_message("✅ تم الربط بنجاح!")
                await load_plugins(client)
                asyncio.create_task(client.run_until_disconnected())
            except Exception as e: await conv.send_message(f"❌ خطأ: {str(e)}")
    elif data == "restart":
        os.execl(sys.executable, sys.executable, *sys.argv)

loop = asyncio.get_event_loop()
loop.create_task(start_all_accounts())
bot.run_until_disconnected()
