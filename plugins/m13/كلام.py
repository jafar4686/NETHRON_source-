import __main__, asyncio, os
from telethon import events
from googletrans import Translator
from gtts import gTTS

# استخراج الكلاينت من الملف الرئيسي
client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]
translator = Translator()

# --- دالة نماذج الزخرفة ---
def get_zakhrafa(text):
    return [
        f"╰╼ {text} ╾╯",
        f"★ {text} ★",
        f"☭ {text} ☭",
        f"『 {text} 』",
        f"【 {text} 】",
        f"々{text}々",
        f"♛ {text} ♛",
        f"💠 {text} 💠",
        f"◈ {text} ◈",
        f"⎔ {text} ⎔"
    ]

# ==========================================
# 1. قائمة أوامر الأدوات (.م14)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م14$"))
async def menu_pro(event):
    for f in VORTEX:
        await event.edit(f"⌯ {f} جاري تحميل قائمة الأدوات {f} ⌯")
        await asyncio.sleep(0.05)
    
    msg = (
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑻𝑶𝑶𝑳𝑺 • ☭\n"
        "★────────☭────────★\n\n"
        "• `.ترجم` [لغة] ⌯ ترجمة بالرد\n"
        "• `.نطق` [لغة] [نص] ⌯ تحويل النص لبصمة\n"
        "• `.زخرف` [نص] ⌯ زخرفة ملكية (10 نماذج)\n"
        "• `$نسخ` [نص] ⌯ تحويل لنص قابل للنسخ\n\n"
        "• **أمثلة:** `.ترجم en` | `.نطق ar`\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )
    await event.edit(msg)

# ==========================================
# 2. ميزة النطق الذكي (.نطق [اللغة])
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.نطق\s+([a-z]{2})(?:\s+(.*))?$"))
async def speak_cmd(event):
    lang = event.pattern_match.group(1)
    text = event.pattern_match.group(2)
    
    # جلب النص من الرد إذا لم يكتب بجانب الأمر
    if not text and event.is_reply:
        reply_msg = await event.get_reply_message()
        text = reply_msg.text

    if not text:
        return await event.edit("⚠️ **يرجى كتابة نص أو الرد على رسالة!**")

    await event.edit("⌛ **جاري معالجة الصوت...**")
    
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save("voice.ogg")
        await client.send_file(
            event.chat_id, 
            "voice.ogg", 
            voice_note=True, 
            reply_to=event.reply_to_msg_id
        )
        os.remove("voice.ogg")
        await event.delete()
    except Exception as e:
        await event.edit(f"❌ **حدث خطأ فني:**\n`{str(e)}`")

# ==========================================
# 3. ميزة الزخرفة الفورية (.زخرف)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.زخرف(?:\s+(.*))?$"))
async def zakhrafa_cmd(event):
    text = event.pattern_match.group(1)
    if not text and event.is_reply:
        reply_msg = await event.get_reply_message()
        text = reply_msg.text
        
    if not text:
        return await event.edit("⚠️ **يرجى كتابة اسم لزخرفته!**")

    results = get_zakhrafa(text)
    msg = (
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑫𝑬𝑪𝑶𝑹 • ☭\n"
        "★────────☭────────★\n\n"
        "• **اضغط على النص لنسخه:**\n\n"
    )
    for res in results:
        msg += f"• `{res}`\n"
    
    msg += "\n• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    await event.edit(msg)

# ==========================================
# 4. ميزة الترجمة الفورية (.ترجم [اللغة])
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ترجم\s+([a-z]{2})(?:\s+(.*))?$"))
async def translate_cmd(event):
    target_lang = event.pattern_match.group(1)
    text = event.pattern_match.group(2)
    
    if not text and event.is_reply:
        reply_msg = await event.get_reply_message()
        text = reply_msg.text
        
    if not text:
        return await event.edit("⚠️ **رد على رسالة لترجمتها!**")

    await event.edit("⌛ **جاري الترجمة...**")
    
    try:
        res = translator.translate(text, dest=target_lang)
        msg = (
            "★────────☭────────★\n"
            "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑻𝑹𝑨𝑵𝑺𝑳𝑨𝑻𝑬 • ☭\n"
            "★────────☭────────★\n\n"
            f"• **النص:** `{text}`\n\n"
            f"• **الترجمة ({target_lang}):**\n`{res.text}`\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
        )
        await event.edit(msg)
    except:
        await event.edit("❌ فشل في الاتصال بخدمة الترجمة.")

# ==========================================
# 5. ميزة النسخ الملكي ($نسخ)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\$نسخ(?:\s+(.*))?$"))
async def copy_maker_final(event):
    input_text = event.pattern_match.group(1)
    if event.is_reply and not input_text:
        reply_msg = await event.get_reply_message()
        input_text = reply_msg.text

    if not input_text:
        return await event.edit("⚠️ **اكتب نصاً لتحويله لنسخ!**")

    msg = (
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑪𝑶𝑷𝒀 • ☭\n"
        "★────────☭────────★\n\n"
        f" `{input_text}` \n\n"
        "• **اضغط على النص أعلاه للنسخ.**\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )
    await event.edit(msg)
