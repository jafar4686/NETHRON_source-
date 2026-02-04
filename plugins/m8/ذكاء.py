import __main__
from telethon import events
import asyncio
# ملاحظة: يجب تثبيت مكتبة g4f عبر: pip install g4f
from g4f.client import Client 

client = __main__.client
ai_client = Client()

# --- إعدادات النظام ---
if not hasattr(__main__, 'ai_config'):
    __main__.ai_config = {
        "active_pv": False,     # الرد التلقائي في الخاص
        "active_groups": True,  # الرد في المجموعات عند المناداة
        "chat_history": {},     # ذاكرة المحادثة
        "personality": "أنا مساعد ذكي اسمي نيثرون، مبرمج بواسطة المطور جعفر، أرد باختصار وذكاء وبلهجة عراقية محببة."
    }

CONFIG = __main__.ai_config

HEADER = (
    "★────────☭────────★\n"
    "   ☭ • 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 𝐴𝐼 𝐵𝑂𝑇 • ☭\n"
    "★────────☭────────★\n"
)

# --- دالة جلب الرد من الذكاء الاصطناعي ---
async def get_ai_response(user_id, text):
    try:
        # جلب الذاكرة للمستخدم
        history = CONFIG["chat_history"].get(user_id, [])
        history.append({"role": "user", "content": text})
        
        response = ai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": CONFIG["personality"]}] + history[-5:] # آخر 5 رسائل فقط للسرعة
        )
        
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        CONFIG["chat_history"][user_id] = history
        return reply
    except Exception as e:
        return f"⚠️ عذراً، واجهت مشكلة تقنية: {str(e)}"

# =========================
# 🎮 أوامر التحكم
# =========================

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل ذكاء (خاص|كروبات)$"))
async def enable_ai(event):
    mode = event.pattern_match.group(1)
    if mode == "خاص": CONFIG["active_pv"] = True
    else: CONFIG["active_groups"] = True
    await event.edit(f"✅ **تم تفعيل الذكاء الاصطناعي في الـ {mode}**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تعطيل ذكاء (خاص|كروبات)$"))
async def disable_ai(event):
    mode = event.pattern_match.group(1)
    if mode == "خاص": CONFIG["active_pv"] = False
    else: CONFIG["active_groups"] = False
    await event.edit(f"❌ **تم تعطيل الذكاء الاصطناعي في الـ {mode}**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.شخصية الذكاء (.*)$"))
async def set_personality(event):
    new_p = event.pattern_match.group(1)
    CONFIG["personality"] = new_p
    await event.edit(f"👤 **تم تغيير شخصية الذكاء إلى:**\n`{new_p}`")

# =========================
# 🕵️ محرك الردود التلقائية
# =========================

@client.on(events.NewMessage(incoming=True))
async def ai_handler(event):
    sender_id = event.sender_id
    text = event.text
    
    if not text or len(text) < 2: return

    # 1. الرد في الخاص (إذا مفعل)
    if event.is_private and CONFIG["active_pv"]:
        if not event.out:
            async with event.client.action(event.chat_id, 'typing'):
                reply = await get_ai_response(sender_id, text)
                await event.reply(reply)

    # 2. الرد في المجموعات (عند المناداة باسم البوت أو "نيثرون")
    elif event.is_group and CONFIG["active_groups"]:
        if "نيثرون" in text or "يا ذكاء" in text:
            async with event.client.action(event.chat_id, 'typing'):
                clean_text = text.replace("نيثرون", "").strip()
                reply = await get_ai_response(sender_id, clean_text)
                await event.reply(reply)

# =========================
# 🔍 أمر السؤال المباشر
# =========================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اسأل (.*)$"))
async def ask_ai(event):
    question = event.pattern_match.group(1)
    await event.edit("⏳ **جاري التفكير...**")
    reply = await get_ai_response("owner", question)
    await event.edit(f"👤 **السؤال:** {question}\n\n🤖 **الرد:**\n{reply}")
