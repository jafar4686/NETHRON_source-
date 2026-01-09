# قائمة الكلمات للعبة التفكيك
words_list = ["نيثرون", "تليجرام", "مطور", "برمجة", "سيرفر", "باثيون", "العراق", "تكنولوجيا", "ذكاء"]

@client.on(events.NewMessage(pattern=r"^\.تفكيك$"))
async def tafkik_game(event):
    word = random.choice(words_list)
    # تفكيك الكلمة بوضع مسافات بين الحروف
    shuffled_word = " ".join(list(word))
    
    await event.edit(f"★────────☭────────★\n"
                     f"🕹 **لعبة التفكيك**\n\n"
                     f"فكك الكلمة التالية بأسرع وقت:\n"
                     f"🔹 **{shuffled_word}**\n\n"
                     f"★────────☭────────★")
    
    # انتظار أول رد يحتوي على الكلمة الصحيحة
    async with client.conversation(event.chat_id) as conv:
        try:
            response = await conv.get_response()
            if response.text == word:
                name = (await client.get_entity(response.sender_id)).first_name
                await response.reply(f"🎊 كفوو {name}! أنت الفائز، الكلمة هي: **{word}**")
            else:
                await event.respond(f"❌ خطأ، انتهى الوقت أو الإجابة غلط. الكلمة كانت: {word}")
        except:
            pass
