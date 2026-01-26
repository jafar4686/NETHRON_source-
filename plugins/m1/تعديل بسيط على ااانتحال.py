import __main__
from telethon import events
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
import os
import asyncio

client = __main__.client

# مخزن المعلومات الأصلية
my_original_info = {"first_name": "", "last_name": "", "bio": "", "has_backup": False}

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(انتحال|نسخ)(?:\s+(.*))?$"))
async def clone_user(event):
    global my_original_info
    
    reply = await event.get_reply_message()
    user_id = None
    if reply: user_id = reply.sender_id
    elif event.pattern_match.group(2): user_id = event.pattern_match.group(2)
    else: return await event.edit("❌ **يرجى الرد على الشخص أو وضع يوزره**")

    # --- شريط التحميل الفخم ---
    frames = [
        "⏳ جاري بدء الانتحال... \n`[▒▒▒▒▒▒▒▒▒▒] 0%`",
        "📡 سحب بيانات الحساب... \n`[███▒▒▒▒▒▒▒] 30%`",
        "🖼 جاري نسخ الصورة... \n`[██████▒▒▒▒] 60%`",
        "📝 تحديث الاسم والبايو... \n`[█████████▒] 90%`"
    ]
    for frame in frames:
        await event.edit(frame)
        await asyncio.sleep(0.4)

    try:
        full_user = await client(GetFullUserRequest(user_id))
        user = full_user.users[0]
        user_bio = full_user.full_user.about or ""
        
        # أخذ نسخة احتياطية إذا لم تكن موجودة
        if not my_original_info["has_backup"]:
            me_full = await client(GetFullUserRequest('me'))
            my_original_info.update({
                "first_name": me_full.users[0].first_name or "",
                "last_name": me_full.users[0].last_name or "",
                "bio": me_full.full_user.about or "",
                "has_backup": True
            })

        # --- نسخ الصورة ---
        photo = await client.download_profile_photo(user)
        if photo:
            try:
                uploaded_photo = await client.upload_file(photo)
                await client(UploadProfilePhotoRequest(file=uploaded_photo))
                os.remove(photo)
            except: pass
        
        # --- نسخ الاسم والبايو ---
        await client(UpdateProfileRequest(
            first_name=user.first_name or "",
            last_name=user.last_name or "",
            about=user_bio[:70]
        ))

        await event.edit(f"✅ **تم انتحال {user.first_name} بنجاح!**\n`[██████████] 100%` \n\n• للرجوع ارسل `.ارجاع`")
        
        # حذف الرسالة بعد 10 ثواني
        await asyncio.sleep(10)
        await event.delete()

    except Exception as e:
        await event.edit(f"❌ **فشل الانتحال:**\n`{str(e)}`")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ارجاع$"))
async def restore_info(event):
    if not my_original_info["has_backup"]:
        return await event.edit("⚠️ **لا توجد نسخة أصلية مسجلة!**")

    # --- شريط ارجاع فخم ---
    back_frames = [
        "🔄 جاري استعادة الحساب... \n`[▒▒▒▒▒▒▒▒▒▒] 0%`",
        "📂 استرجاع البيانات الأصلية... \n`[█████▒▒▒▒▒] 50%`",
        "✨ تنظيف البروفايل... \n`[█████████▒] 90%`"
    ]
    for f in back_frames:
        await event.edit(f)
        await asyncio.sleep(0.4)

    try:
        await client(UpdateProfileRequest(
            first_name=my_original_info["first_name"],
            last_name=my_original_info["last_name"],
            about=my_original_info["bio"]
        ))
        
        # حذف صورة الانتحال
        photos = await client.get_profile_photos('me')
        if photos: await client(DeletePhotosRequest([photos[0]]))
            
        await event.edit("✅ **تم استعادة حسابك الأصلي بنجاح!**\n`[██████████] 100%`")
        
        # حذف الرسالة بعد 10 ثواني
        await asyncio.sleep(10)
        await event.delete()

    except Exception as e:
        await event.edit(f"❌ **خطأ أثناء الاستعادة:** `{e}`")
