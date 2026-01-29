import __main__
from telethon import events

# جلب الكلاينت المحقون من الميكر
client = getattr(__main__, 'client', None)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تجربه$"))
async def test_command(event):
    # الرابط المباشر للصورة (لازم تستبدله برابط شغال)
    image_url = "https://graph.org/file/45bd809c97cf4e1666b99.jpg"  # <=== حط رابط صورتك هنا

    # الكليشة اللي راح تظهر تحت الصورة
    caption_text = "هلا حب"

    # حذف أمر .تجربه أولاً
    await event.delete()

    try:
        # إرسال الصورة من الرابط مع الكليشة
        await client.send_file(event.chat_id, image_url, caption=caption_text)
    except Exception as e:
        # في حال حدوث خطأ (مثلاً الرابط مو شغال أو مو رابط صورة)
        await event.respond(f"⚠️ ضلعي، ما كدرت أرسل الصورة من الرابط!\nالخطأ: {e}\nتأكد إن الرابط مباشر لصورة (ينتهي بـ .jpg, .png أو رابط منشور تليجرام)")
