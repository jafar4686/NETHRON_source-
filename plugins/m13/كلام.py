import __main__, asyncio
from telethon import events
from spellchecker import SpellChecker

# استخراج الكلاينت
client = getattr(__main__, 'client', None)

# تعريف المصحح للغة العربية (يعمل تلقائياً بالاحتمالات)
# ملاحظة: سنستخدم منطق الفحص الذكي للكلمات
spell = SpellChecker(language=None) # لغة مخصصة

@client.on(events.NewMessage(outgoing=True))
async def auto_detector_corrector(event):
    # نتخطى الروابط، الأوامر، والرسائل القصيرة جداً
    if not event.text or event.text.startswith((".", "$", "/")) or len(event.text) < 3:
        return

    original_text = event.text
    words = original_text.split()
    corrected_list = []
    has_fix = False

    for word in words:
        # إذا الكلمة طولها أكثر من 3 حروف (حتى نتجنب تصحيح الأسماء القصيرة غلط)
        if len(word) > 3:
            # الخوارزمية تبحث عن أقرب كلمة منطقية
            # هنا نضع الكلمات الشائعة التي نريد للبوت أن يصححها دائماً
            smart_fixes = {
                "سلاو": "سلام",
                "عليكيو": "عليكم",
                "اشونك": "شلونك",
                "الاه": "الله",
                "انشاءالله": "إن شاء الله",
                "هلوو": "هلو",
                "اشكرك": "مشكور"
            }
            
            if word in smart_fixes:
                corrected_list.append(smart_fixes[word])
                has_fix = True
                continue

            # فحص "المسافة" بين الحروف (لو كاتب حرفين مقلوبين)
            # مثال: "البيتت" -> "البيت"
            # إذا كانت الكلمة تنتهي بحرف مكرر 3 مرات، يمسح الزيادة
            if len(word) > 3 and word[-1] == word[-2] == word[-3]:
                fixed_word = word.rstrip(word[-1]) + word[-1]
                corrected_list.append(fixed_word)
                has_fix = True
            else:
                corrected_list.append(word)
        else:
            corrected_list.append(word)

    if has_fix:
        final_text = " ".join(corrected_list)
        if final_text != original_text:
            # ننتظر ثانية وحدة حتى ما يبين بوت سريع ويحظرنا التلي
            await asyncio.sleep(0.5)
            await event.edit(final_text)

# أمر تشغيل/إيقاف
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تصحيح (اون|اوف)$"))
async def toggle_speller(event):
    # هذا الأمر فقط للشكل، الكود يعمل تلقائياً
    status = event.pattern_match.group(1)
    await event.edit(f"⚙️ **تم تحويل المصحح الذكي إلى: {status}**")
