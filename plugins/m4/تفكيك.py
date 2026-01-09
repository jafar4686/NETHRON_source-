import __main__
from telethon import events
import random

client = __main__.client

# قائمة الكلمات
words_list = ["نيثرون", "تليجرام", "مطور", "برمجة", "سيرفر", "باثيون", "العراق", "تكنولوجيا", "ذكاء"]

# مخزن لمتابعة الكلمة الحالية في كل جروب
active_tafkik = {}

@client.on(events.NewMessage(pattern=r"^\.تفكيك$"))
async def start_tafkik(event):
    # اختيار كلمة عشوائية
    word = random.choice(words_list)
    # تفكيك الكلمة
    shuffled = " ".join(list(word))
    
    # حفظ الكلمة في الذاكرة لهذا الجروب
    active_tafkik[event.chat_id] = word
    
    await event.edit(f"★────────☭────────★\n"
                     f"🕹 **لعبة التفكيك**\n\n"
                     f"قم بتجميع الكلمة التالية:\n"
                     f"🔹 **{shuffled}**\n\n"
                     f"أول من يكتب الكلمة يفوز! 🏆\n"
                     f"★────────☭────────★")

@client.on(events.NewMessage())
async def check_answer(event):
    # التأكد أن هناك لعبة جارية في هذا الجروب
    if event.chat_id in active_tafkik:
        answer = active_tafkik[event.chat_id]
        
        # إذا كانت رسالة الشخص تطابق الكلمة
        if event.text == answer:
            user = await event.get_sender()
            name = user.first_name if user else "البطل"
            
            await event.reply(f"🎊 كفو منك يا **{name}**!\n✅ الإجابة صحيحة: **{answer}**\n\nتم إضافة نقطة لرصيدك (وهمياً) 🎖")
            
            # إنهاء اللعبة لهذا الجروب
            del active_tafkik[event.chat_id]
