import __main__
from telethon import events

# استخراج الكلاينت
client = getattr(__main__, 'client', None)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ميمز$"))
async def play_specific_meme(event):
    # الرابط اللي عطيته إليّ
    meme_url = "https://t.me/N_G_A_A/7"
    
    await event.edit("🚀 **جاري سحب البصمة الملكية...**")
    
    try:
        # إرسال الملف مباشرة من الرابط كبصمة (Voice Note)
        await client.send_file(
            event.chat_id, 
            meme_url, 
            voice_note=True, # يخليها تظهر كبصمة مو ملف
            reply_to=event.reply_to_msg_id
        )
        # حذف رسالة "جاري السحب" بعد ما يرسل البصمة
        await event.delete()
        
    except Exception as e:
        # إذا طلع خطأ راح يكتبه لك هنا (مثلاً القناة خاصة أو الرابط انحذف)
        await event.edit(f"❌ **فشل السحب!**\nالسبب: `{str(e)}` \nتأكد أن القناة عامة.")
