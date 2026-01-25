# plugins/autopost.py
import __main__
import asyncio
from telethon import events, Button
from datetime import datetime

client = __main__.client
bot = __main__.bot

# ======================
# 🧠 التخزين
# ======================
if not hasattr(__main__, "AUTOPOST"):
    __main__.AUTOPOST = {
        "enabled": False,
        "caption": None,
        "media": None,
        "delay": 60,
        "fixed_time": None,
        "chats": []
    }

# ======================
# 🔘 قائمة .م3 بالأزرار
# ======================
@client.on(events.NewMessage(pattern=r"^\.م3$"))
async def menu(event):
    if not event.out:
        return

    buttons = [
        [Button.inline("▶️ تشغيل", b"ap_on"), Button.inline("⛔ إيقاف", b"ap_off")],
        [Button.inline("📊 الحالة", b"ap_status"), Button.inline("📋 القروبات", b"ap_list")]
    ]

    await bot.send_message(
        event.chat_id,
        "📢 **نظام النشر التلقائي الذكي**\n\n"
        "• يدعم نص / صورة / فيديو\n"
        "• جدولة زمنية\n"
        "• نشر من جلسة الحساب\n",
        buttons=buttons
    )

# ======================
# 🔘 أزرار التحكم
# ======================
@bot.on(events.CallbackQuery)
async def buttons_handler(event):
    data = event.data.decode()
    ap = __main__.AUTOPOST

    if data == "ap_on":
        if not ap["caption"] and not ap["media"]:
            return await event.answer("❌ لا توجد مادة للنشر", alert=True)
        if not ap["chats"]:
            return await event.answer("❌ لا توجد قروبات", alert=True)
        if ap["enabled"]:
            return await event.answer("⚠️ النشر يعمل", alert=True)

        ap["enabled"] = True
        asyncio.create_task(autopost_loop())
        await event.answer("✅ تم تشغيل النشر")

    elif data == "ap_off":
        ap["enabled"] = False
        await event.answer("⛔ تم الإيقاف")

    elif data == "ap_status":
        txt = (
            f"⚙️ **الحالة:** {'شغال ✅' if ap['enabled'] else 'متوقف ❌'}\n"
            f"⏱️ **الوقت:** {ap['delay']} ثانية\n"
            f"📌 **القروبات:** {len(ap['chats'])}"
        )
        await event.answer(txt, alert=True)

    elif data == "ap_list":
        if not ap["chats"]:
            return await event.answer("📭 لا توجد قروبات", alert=True)
        await event.answer("\n".join(map(str, ap["chats"])), alert=True)

# ======================
# 📝 الإعداد
# ======================
@client.on(events.NewMessage(pattern=r"^\.نشر كليشه$"))
async def set_text(event):
    if not event.out:
        return
    r = await event.get_reply_message()
    if not r or not r.text:
        return await event.edit("❌ رد على نص")
    __main__.AUTOPOST["caption"] = r.text
    await event.edit("✅ تم حفظ الكليشة")

@client.on(events.NewMessage(pattern=r"^\.نشر وسائط$"))
async def set_media(event):
    if not event.out:
        return
    r = await event.get_reply_message()
    if not r or not r.media:
        return await event.edit("❌ رد على صورة أو فيديو")
    __main__.AUTOPOST["media"] = r
    await event.edit("🖼️ تم حفظ الوسائط")

@client.on(events.NewMessage(pattern=r"^\.نشر وقت (\d+)$"))
async def set_delay(event):
    sec = int(event.pattern_match.group(1))
    __main__.AUTOPOST["delay"] = sec
    await event.edit(f"⏱️ الوقت: {sec} ثانية")

@client.on(events.NewMessage(pattern=r"^\.نشر ساعة (\d+:\d+)$"))
async def set_fixed(event):
    __main__.AUTOPOST["fixed_time"] = event.pattern_match.group(1)
    await event.edit(f"⏰ وقت ثابت: {event.pattern_match.group(1)}")

# ======================
# 📌 القروبات
# ======================
@client.on(events.NewMessage(pattern=r"^\.نشر اضافه$"))
async def add_chat(event):
    if not event.out:
        return
    r = await event.get_reply_message()
    if not r:
        return
    cid = r.chat_id
    if cid not in __main__.AUTOPOST["chats"]:
        __main__.AUTOPOST["chats"].append(cid)
    await event.edit("✅ تم الإضافة")

@client.on(events.NewMessage(pattern=r"^\.نشر حذف$"))
async def del_chat(event):
    if not event.out:
        return
    r = await event.get_reply_message()
    if not r:
        return
    try:
        __main__.AUTOPOST["chats"].remove(r.chat_id)
        await event.edit("🗑️ تم الحذف")
    except:
        await event.edit("❌ غير موجود")

# ======================
# 🔁 حلقة النشر الذكي
# ======================
async def autopost_loop():
    ap = __main__.AUTOPOST
    while ap["enabled"]:
        if ap["fixed_time"]:
            now = datetime.now().strftime("%H:%M")
            if now != ap["fixed_time"]:
                await asyncio.sleep(20)
                continue

        for chat in ap["chats"]:
            try:
                if ap["media"]:
                    await ap["media"].forward_to(chat)
                elif ap["caption"]:
                    await client.send_message(chat, ap["caption"])
            except Exception as e:
                await client.send_message("me", f"⚠️ نشر فشل:\n{e}")

        await asyncio.sleep(ap["delay"])