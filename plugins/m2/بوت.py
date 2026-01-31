import os, json, asyncio
from telethon import TelegramClient, events, Button
# استيراد الإعدادات من ملفك الأصلي لضمان التطابق
from config import api_id, api_hash

# --- [1] إعدادات البوت الجديد ---
# حط هنا التوكن الجديد اللي سويته من BotFather
COMP_BOT_TOKEN = "8579454046:AAGn52vlNAwQzaRx-ABWfMnBTppv1ckmCds"

# تعريف البوت الجديد بـ Session جديد اسمه 'CompBot'
comp_bot = TelegramClient('CompBot', api_id, api_hash).start(bot_token=COMP_BOT_TOKEN)

BASE_DIR = "group"

# --- [2] دوال مساعدة ---
def get_points(chat_id, user_id):
    # دالة تجلب النقاط من ملفات السورس الأساسي
    for folder in os.listdir(BASE_DIR):
        if folder.endswith(str(chat_id)):
            path = os.path.join(BASE_DIR, folder, "stats.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    user_data = data.get(str(user_id), {})
                    return user_data.get("count", 0)
    return 0

# --- [3] أوامر البوت المساعد بالأزرار ---

@comp_bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    # كليشة ترحيب خاصة بالمسابقات
    welcome_msg = (
        "🏆 **مساعد مسابقات عراق ثون**\n"
        "★────────☭────────★\n\n"
        "• أهلاً بك في البوت الرسمي لإدارة التفاعل.\n"
        "• يمكن للأعضاء معرفة نقاطهم عبر الأزرار أدناه 👇"
    )
    buttons = [
        [Button.inline("📊 عرض نقاطي", data="view_my_pts")],
        [Button.inline("📜 قوانين المسابقة", data="rules")],
        [Button.url("📢 قناة السورس", "https://t.me/NETH_RON")]
    ]
    await event.respond(welcome_msg, buttons=buttons)

@comp_bot.on(events.CallbackQuery)
async def callback(event):
    data = event.data.decode()
    user_id = event.sender_id
    chat_id = event.chat_id

    if data == "view_my_pts":
        if event.is_private:
            return await event.answer("⚠️ أدخل للمجموعة واضغط الزر لمعرفة نقاطك!", alert=True)
        
        pts = get_points(chat_id, user_id)
        await event.answer(f"✅ نقاط تفاعلك الحالية: {pts}", alert=True)

    elif data == "rules":
        rules_text = (
            "📜 **قوانين مسابقات المملكة:**\n"
            "1. النقاط تُحسب بناءً على عدد رسائلك.\n"
            "2. يمنع السبام أو الرسائل المكررة.\n"
            "3. الجوائز توزع أسبوعياً للأكثر تفاعلاً."
        )
        await event.edit(rules_text, buttons=[Button.inline("⬅️ رجوع", data="back")])

    elif data == "back":
        await event.edit("🏆 مساعد مسابقات عراق ثون", buttons=[
            [Button.inline("📊 عرض نقاطي", data="view_my_pts")],
            [Button.inline("📜 قوانين المسابقة", data="rules")]
        ])

# --- [4] التشغيل ---
print("✅ بوت المسابقات المنفصل شغال الآن بالتوكن الجديد...")
comp_bot.run_until_disconnected()
