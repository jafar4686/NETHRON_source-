import __main__
from telethon import events
import asyncio
from g4f.client import Client # تأكد من تثبيت مكتبة g4f

client = __main__.client
ai_client = Client()

# إعدادات النظام في الذاكرة
if not hasattr(__main__, 'ai_pro_config'):
    __main__.ai_pro_config = {
        "pv": False, "groups": False, "reply_all": False,
        "lang": "العربية", "mood": "ذكاء حاد", "history": {}
    }

AI_CFG = __main__.ai_pro_config
HEADER = "<b>★────────☭────────★\n   ☭ • 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 𝐴𝐼 𝑃𝑅𝑂 • ☭\n★────────☭────────★</b>\n\n"

# دالة جلب الرد
async def get_ai_reply(uid, text):
    try:
        hist = AI_CFG["history"].get(uid, [])
        hist.append({"role": "user", "content": text})
        resp = ai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": f"أنت ذكاء نيثرون، تتحدث بـ {AI_CFG['lang']} وبأسلوب {AI_CFG['mood']}"}] + hist[-6:]
        )
        reply = resp.choices[0].message.content
        hist.append({"role": "assistant", "content": reply})
        AI_CFG["history"][uid] = hist
        return reply
    except: return "⚠️ عذراً، الخادم مشغول حالياً."

# ===============================
# 🤖 أوامر التحكم والتشغيل (10 أوامر)
# ===============================

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(تفعيل|تعطيل) ذكاء (خاص|كروبات|الكل)$"))
async def ai_toggle(e):
    cmd, mode = e.pattern_match.group(1), e.pattern_match.group(2)
    state = True if cmd == "تفعيل" else False
    if mode == "خاص": AI_CFG["pv"] = state
    elif mode == "كروبات": AI_CFG["groups"] = state
    else: AI_CFG["reply_all"] = state
    await e.edit(f"✅ **تم {cmd} الذكاء في {mode}**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اسأل (.*)$"))
async def ask(e):
    q = e.pattern_match.group(1)
    await e.edit("🤔 **جاري التفكير...**")
    r = await get_ai_reply("owner", q)
    await e.edit(f"🙋‍♂️ **السؤال:** {q}\n\n🤖 **الرد:**\n{r}")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.لغة الذكاء (.*)$"))
async def set_lang(e):
    AI_CFG["lang"] = e.pattern_match.group(1)
    await e.edit(f"🌐 **تم تغيير لغة الذكاء إلى: {AI_CFG['lang']}**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.مود الذكاء (.*)$"))
async def set_mood(e):
    AI_CFG["mood"] = e.pattern_match.group(1) # مثال: مضحك، حزين، عدواني، تقني
    await e.edit(f"🎭 **تم تغيير أسلوب الذكاء إلى: {AI_CFG['mood']}**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.صفر الذكاء$"))
async def reset_ai(e):
    AI_CFG["history"] = {}
    await e.edit("🧹 **تم تصفير ذاكرة الذكاء لجميع المحادثات.**")

# ===============================
# 🛠️ أوامر الخدمات الذكية (10 أوامر)
# ===============================

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ترجم (.*)$"))
async def ai_trans(e):
    txt = e.pattern_match.group(1)
    await e.edit("🔄 **جاري الترجمة...**")
    r = await get_ai_reply("tool", f"ترجم هذا النص للعربية: {txt}")
    await e.edit(f"📖 **الترجمة:**\n`{r}`")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.صحح (.*)$"))
async def ai_fix(e):
    txt = e.pattern_match.group(1)
    r = await get_ai_reply("tool", f"صحح الأخطاء الإملائية في هذا النص: {txt}")
    await e.edit(f"✍️ **النص المصحح:**\n`{r}`")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.لخص (.*)$"))
async def ai_sum(e):
    txt = e.pattern_match.group(1)
    await e.edit("📝 **جاري التلخيص...**")
    r = await get_ai_reply("tool", f"لخص هذا النص باختصار شديد: {txt}")
    await e.edit(f"📑 **الملخص:**\n{r}")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كود (.*)$"))
async def ai_code(e):
    req = e.pattern_match.group(1)
    await e.edit("💻 **جاري كتابة الكود...**")
    r = await get_ai_reply("tool", f"اكتب كود برمجي بلغة بايثون لـ: {req}")
    await e.edit(f"✅ **الكود الجاهز:**\n\n`{r}`")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.اوامر الذكاء$"))
async def ai_help(e):
    help_msg = (
        HEADER +
        "1. `.تفعيل ذكاء خاص`\n2. `.تفعيل ذكاء كروبات`\n3. `.تفعيل ذكاء الكل`\n"
        "4. `.اسأل (نص)`\n5. `.لغة الذكاء (اللغة)`\n6. `.مود الذكاء (الأسلوب)`\n"
        "7. `.صفر الذكاء` (مسح الذاكرة)\n8. `.ترجم (نص)`\n9. `.صحح (نص إملائي)`\n"
        "10. `.لخص (نص طويل)`\n11. `.كود (وصف الكود)`\n12. `.تحليل (بالرد على رسالة)`\n"
        "13. `.شعر (موضوع)`\n14. `.نكتة`\n15. `.بوت (نص)` (رد سريع)\n"
        "16. `.ذكاء تعليق` (رد تلقائي على الكل)\n17. `.هوية الذكاء` (تغيير اسمه)\n"
        "18. `.ايقاف ذكاء` (للكل)\n19. `.تخيل` (وصف صورة)\n20. `.فحص الذكاء` (الحالة)"
    )
    await e.edit(help_msg, parse_mode='html')

# محرك الردود التلقائية
@client.on(events.NewMessage(incoming=True))
async def auto_ai(event):
    if event.is_private and AI_CFG["pv"]:
        res = await get_ai_reply(event.sender_id, event.text)
        await event.reply(res)
    elif event.is_group and AI_CFG["groups"] and "نيثرون" in event.text:
        res = await get_ai_reply(event.sender_id, event.text.replace("نيثرون",""))
        await event.reply(res)
