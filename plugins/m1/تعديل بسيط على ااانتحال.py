import __main__
from telethon import events
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
import os
import asyncio

client = __main__.client

# مخزن المعلومات الأصلية (النسخة الاحتياطية)
if not hasattr(__main__, 'nethron_clone_backup'):
    __main__.nethron_clone_backup = {"first_name": "", "last_name": "", "bio": "", "has_backup": False}

BACKUP = __main__.nethron_clone_backup

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(انتحال|نسخ)(?:\s+(.*))?$"))
async def clone_user(event):
    reply = await event.get_reply_message()
    user_id = None
    if reply: user_id = reply.sender_id
    elif event.pattern_match.group(2): user_id = event.pattern_match.group(2)
    else: return await event.edit("❌ **يرجى الرد على الشخص أو وضع يوزره**")

    # --- شريط تحميل الانتحال ---
    load_frames = [
        "⏳ جاري بدء الانتحال... `[▒▒▒▒▒▒▒▒▒▒]`",
        "📡 سحب البيانات... `[███▒▒▒▒▒▒▒]`",
        "📸 نسخ الصورة... `[██████▒▒▒▒]`",
        "📝 تحديث الحساب... `[█████████▒]`"
    ]
    for frame in load_frames:
        await event.edit(f"**{frame}**")
        await asyncio.sleep(0.3)

    try:
        full_user = await client(GetFullUserRequest(user_id))
        user = full_user.users[0]
        user_bio = full_user.full_user.about or ""
        
        # أخذ نسخة احتياطية لحسابك قبل التغيير
        if not BACKUP["has_backup"]:
            me_full = await client(GetFullUserRequest('me'))
            BACKUP.update({
                "first_name": me_full.users[0].first_name or "",
                "last_name": me_full.users[0].last_name or "",
                "bio": me_full.full_user.about or "",
                "has_backup": True
            })

        # نسخ الصورة
        photo = await client.download_profile_photo(user)
        if photo:
            uploaded_photo = await client.upload_file(photo)
            await client(UploadProfilePhotoRequest(file=uploaded_photo))
            os.remove(photo)
        
        # نسخ الاسم والبايو
        await client(UpdateProfileRequest(
            first_name=user.first_name or "",
            last_name=user.last_name or "",
            about=user_bio[:70]
        ))

        await event.edit(f"✅ **تم انتحال {user.first_name} بنجاح!**\n`[██████████] 100%` \n\n• للرجوع ارسل `.ارجاع`")
        await asyncio.sleep(10)
        await event.delete()

    except Exception as e:
        await event.edit(f"❌ **فشل الانتحال:** `{str(e)}`")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ارجاع$"))
async def restore_info(event):
    if not BACKUP["has_backup"]:
        return await event.edit("⚠️ **لا توجد نسخة أصلية مسجلة!**")

    # --- زخرفة الارجاع المتحركة ---
    back_anim = [
        "🔄 جاري الإرجاع... `◐`",
        "🔄 جاري الإرجاع... `◓`",
        "🔄 جاري الإرجاع... `◑`",
        "🔄 جاري الإرجاع... `◒`",
        "✨ إعادة البيانات... `[██████▒▒▒▒]`",
        "🛡️ تنظيف الحساب... `[█████████▒]`"
    ]
    for f in back_anim:
        await event.edit(f"**{f}**")
        await asyncio.sleep(0.3)

    try:
        # استرجاع البيانات
        await client(UpdateProfileRequest(
            first_name=BACKUP["first_name"],
            last_name=BACKUP["last_name"],
            about=BACKUP["bio"]
        ))
        
        # حذف صور الانتحال
        photos = await client.get_profile_photos('me')
        if photos: await client(DeletePhotosRequest([photos[0]]))
            
        # القائمة النهائية الفخمة
        final_msg = (
            "◆━━━━━━━━━━━━━━◆\n"
            "◈ تم رجع حسابك ضلعي ◈ \n"
            "◆━━━━━━━━━━━━━━◆\n"
            "➥ 𝑫𝑬𝑽 〔 [المطور](https://t.me/NETH_RON) 〕\n"
            "➥ 𝑨𝑫𝑴𝑰𝑵 〔 [الادمن](https://t.me/xxnnxg) 〕"
        )
        
        await event.edit(final_msg, link_preview=False)
        await asyncio.sleep(10)
        await event.delete()

    except Exception as e:
        await event.edit(f"❌ **خطأ أثناء الاستعادة:** `{e}`")
