import __main__, asyncio
from telethon import events
from googletrans import Translator

# استخراج الكلاينت
client = getattr(__main__, 'client', None)
VORTEX = ["◜", "◝", "◞", "◟"]
translator = Translator()

# ==========================================
# 1. منيو الترجمة والنسخ (.م14)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.م14$"))
async def menu_tr_copy(event):
    msg = (
        "★────────☭────────★\n"
        "   ☭ • 𝑻𝑹𝑨𝑵𝑺𝑳𝑨𝑻𝑬 & 𝑪𝑶𝑷𝒀 • ☭\n"
        "★────────☭────────★\n\n"
        "• `.ترجم` [اللغة] ⌯ ترجمة بالرد على النص\n"
        "• `.عربي` ⌯ ترجمة النص المكتوب للعربي\n"
        "• `.انكليزي` ⌯ ترجمة النص المكتوب للإنكليزي\n"
        "• `$نسخ` ⌯ تحويل النص لنص قابل للنسخ\n\n"
        "• **اللغات المتاحة:** (ar, en, fr, tr, ru)\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )
    await event.edit(msg)

# ==========================================
# 2. ميزة الترجمة الذكية
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(ترجم|عربي|انكليزي)(?:\s+(.*))?$"))
async def translate_cmd(event):
    cmd = event.pattern_match.group(1)
    input_text = event.pattern_match.group(2)
    
    # تحديد اللغة الهدف
    target_lang = 'ar' # الافتراضي
    if cmd == "انكليزي": target_lang = 'en'
    elif cmd == "ترجم" and input_text:
        parts = input_text.split(maxsplit=1)
        target_lang = parts[0]
        input_text = parts[1] if len(parts) > 1 else None

    # جلب النص من الرد إذا لم يكتب نص
    if event.is_reply and not input_text:
        reply_msg = await event.get_reply_message()
        input_text = reply_msg.text
    
    if not input_text:
        return await event.edit("⚠️ **يرجى كتابة نص أو الرد على رسالة لترجمتها!**")

    await event.edit("⌛ **جاري الترجمة...**")
    
    try:
        result = translator.translate(input_text, dest=target_lang)
        msg = (
            "★────────☭────────★\n"
            "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑻𝑹𝑨𝑵𝑺𝑳𝑨𝑻𝑬 • ☭\n"
            "★────────☭────────★\n\n"
            f"• **النص الأصلي:**\n`{input_text}`\n\n"
            f"• **الترجمة ({target_lang}):**\n`{result.text}`\n\n"
            "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
        )
        await event.edit(msg)
    except Exception as e:
        await event.edit(f"❌ **فشل في الترجمة:**\n`{str(e)}`")

# ==========================================
# 3. ميزة النسخ الذكي ($نسخ)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\$نسخ(?:\s+(.*))?$"))
async def copy_maker(event):
    input_text = event.pattern_match.group(1)
    
    if event.is_reply and not input_text:
        reply_msg = await event.get_reply_message()
        input_text = reply_msg.text

    if not input_text:
        return await event.edit("⚠️ **رد على رسالة أو اكتب نص بعد $نسخ!**")

    for f in VORTEX:
        await event.edit(f"⌯ {f} جاري التنسيق للنسخ {f} ⌯")
        await asyncio.sleep(0.05)

    msg = (
        "★────────☭────────★\n"
        "   ☭ • 𝑰𝑹𝑨𝑸𝑻𝑯𝑶𝑶𝑵 𝑪𝑶𝑷𝒀 • ☭\n"
        "★────────☭────────★\n\n"
        f" `{input_text}` \n\n"
        "• **اضغط على النص أعلاه لنسخه فوراً.**\n"
        "• 𝑫𝑬𝑽 𝑩𝒚 ⌯〔 @NETH_RON 〕⌯"
    )
    await event.edit(msg)
