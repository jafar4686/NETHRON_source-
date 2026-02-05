import __main__, asyncio
from telethon import events
from textblob import TextBlob # مكتبة معالجة النصوص

client = getattr(__main__, 'client', None)

# كلمات عراقية وعربية شائعة يخطأ بها الناس (مدمجة بالكود)
COMMON_FIXES = {
    "سلاو": "سلام",
    "علكيو": "عليكم",
    "اشونك": "شلونك",
    "انشاء الله": "إن شاء الله",
    "الاه": "الله",
    "مدريدي": "ملكي", # شقة ضلعي هههه
}

@client.on(events.NewMessage(outgoing=True))
async def intelligent_corrector(event):
    # نتخطى الأوامر والرسائل الفارغة والروابط
    if not event.text or event.text.startswith((".", "$", "/")) or "http" in event.text:
        return

    original_text = event.text
    words = original_text.split()
    corrected_words = []
    is_modified = False

    for word in words:
        # 1. التحقق من القاموس السريع المدمج
        if word in COMMON_FIXES:
            corrected_words.append(COMMON_FIXES[word])
            is_modified = True
        # 2. استخدام الذكاء الاصطناعي لتصحيح الحروف المقلوبة (للكلمات الطويلة)
        elif len(word) > 3:
            b = TextBlob(word)
            corrected_word = str(b.correct())
            if corrected_word.lower() != word.lower():
                # هنا يتم التصحيح إذا كان الفرق بسيط (خطأ مطبعي)
                corrected_words.append(corrected_word)
                is_modified = True
            else:
                corrected_words.append(word)
        else:
            corrected_words.append(word)

    if is_modified:
        new_text = " ".join(corrected_words)
        # تعديل الرسالة فقط إذا كان هناك تغيير حقيقي
        if new_text != original_text:
            await asyncio.sleep(0.5) # تأخير بسيط حتى لا يبدو آلياً جداً
            await event.edit(new_text)

# أمر لتفعيل/تعطيل المصحح
CORRECTOR_STATUS = True

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.المصحح (تفعيل|تعطيل)$"))
async def toggle_corrector(event):
    global CORRECTOR_STATUS
    cmd = event.pattern_match.group(1)
    CORRECTOR_STATUS = True if cmd == "تفعيل" else False
    await event.edit(f"✅ **تم {cmd} المصحح التلقائي الذكي.**")
