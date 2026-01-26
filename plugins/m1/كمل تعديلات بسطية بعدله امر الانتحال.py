import __main__
from telethon import events
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
import os
import asyncio

client = __main__.client

# مخزن المعلومات الأصلية (النسخة الاحتياطية) لضمان عدم ضياع حسابك
if not hasattr(__main__, 'nethron_clone_backup'):
    __main__.nethron_clone_backup = {"first_name": "", "last_name": "", "bio": "", "has_backup": False}

BACKUP = __main__.nethron_clone_backup

# ==========================================
# 1. أمر الانتحال (النسخ)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(انتحال|نسخ)(?:\s+(.*))?$"))
async def clone_user(event):
    reply = await event.get_reply_message()
    user_id = None
    if reply: user_id = reply.sender_id
    elif event.pattern_match.group(2): user_id = event.pattern_match.group(2)
    else: return await event.edit("❌ **يرجى الرد على الشخص أو وضع يوزره**")

    # أنيميشن البداية
    await event.edit("⏳ **جاري بدء عملية الانتحال...**")
    await asyncio.sleep(0.5)

    try:
        full_user = await client(GetFullUserRequest(user_id))
        user = full_user.users[0]
        user_bio = full_user.full_user.about or ""
        
        # أخذ نسخة احتياطية لحسابك قبل التغيير (لمرة واحدة فقط)
        if not BACKUP["has_backup"]:
            me_full = await client(GetFullUserRequest('me'))
            BACKUP.update({
                "first_name": me_full.users[0].first_name or "",
                "last_name": me_full.users[0].last_name or "",
                "bio": me_full.full_user.about or "",
                "has_backup": True
            })

        # نسخ الصورة الشخصية
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

        await event.edit(f"✅ **تم انتحال {user.first_name} بنجاح!**\n\n• للرجوع ارسل `.ارجاع`")
        await asyncio.sleep(5)
        await event.delete()

    except Exception as e:
        await event.edit(f"❌ **فشل الانتحال:** `{str(e)}`")

# ==========================================
# 2. أمر الإرجاع (الدوامة الاحترافية)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ارجاع$"))
async def restore_info(event):
    if not BACKUP["has_backup"]:
        return await event.edit("⚠️ **لا توجد نسخة أصلية مسجلة للعودة إليها!**")

    # --- أنيميشن الدوامة الاحترافية المطلوبة ---
    vortex_frames = ["◜", "◝", "◞", "◟"]
    
    # تكرار الدوران 3 مرات لإعطاء مظهر احترافي
    for _ in range(3):
        for frame in vortex_frames:
            await event.edit(f"**{frame} 〔 ◈ جاي يرجع صبرك ◈ 〕 {frame}**")
            await asyncio.sleep(0.2)

    try:
        # استرجاع بيانات الحساب الأصلية
        await client(UpdateProfileRequest(
            first_name=BACKUP["first_name"],
            last_name=BACKUP["last_name"],
            about=BACKUP["bio"]
        ))
        
        # حذف صورة الانتحال للعودة للصورة الأصلية أو فارغ
        photos = await client.get_profile_photos('me')
        if photos: 
            await client(DeletePhotosRequest([photos[0]]))
            
        # القائمة النهائية الفخمة (بالأسهم والروابط الشغالة)
        final_msg = (
            "◆━━━━━━━━━━━━━━◆\n"
            "◈ تم رجع حسابك ضلعي ◈ \n"
            "◆━━━━━━━━━━━━━━◆\n"
            "➥ 𝑫𝑬𝑽 〔 [المطور](https://t.me/NETH_RON) 〕\n"
            "➥ 𝑨𝑫𝑴𝑰𝑵 〔 [الادمن](https://t.me/xxnnxg) 〕"
        )
        
        await event.edit(final_msg, link_preview=False)
        
        # حذف الرسالة تلقائياً بعد 10 ثواني لتنظيف الدردشة
        await asyncio.sleep(10)
        await event.delete()

    except Exception as e:
        await event.edit(f"❌ **حدث خطأ أثناء الاستعادة:** `{e}`")
